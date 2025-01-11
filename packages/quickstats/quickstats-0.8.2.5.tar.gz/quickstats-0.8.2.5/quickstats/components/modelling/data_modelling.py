from typing import List, Optional, Union, Dict, Callable, Tuple, Any
from itertools import repeat
import os
import copy
import json
import uuid

import numpy as np

from quickstats import semistaticmethod, timer, cached_import
from quickstats.core import mappings as mp
from quickstats.core.typing import ArrayLike
from quickstats.concepts import Binning, RealVariable, RealVariableSet, Range, NamedRanges
from quickstats.components import ROOTObject
from quickstats.components.modelling import PdfFitTool
from quickstats.interface.root import RooDataSet, RooRealVar
from quickstats.utils.py_utils import get_argnames
from quickstats.utils.common_utils import (
    combine_dict,
    in_notebook,
    dict_of_list_to_list_of_dict
)
from quickstats.utils.roofit_utils import dataset_to_histogram, pdf_to_histogram
from .data_source import DataSource
from .model_parameters import (
    ParametersType,
    ModelParameters,
)
from .model_parameters import get as get_model_parameters 

class DataModelling(ROOTObject):
    
    _DEFAULT_FIT_OPTION_ = {
        'prefit': True,
        'print_level': -1,
        'min_fit': 2,
        'max_fit': 3,
        'binned': False,
        'minos': False,
        'hesse': True,
        'sumw2': False,
        'asymptotic': True,
        'strategy': 1,
        'range_expand_rate': 1        
    }
    
    _DEFAULT_PLOT_OPTION_ = {
        'bin_range': None,
        'nbins_data': None,
        'nbins_pdf': 1000,
        'show_comparison': True,
        'show_params': True,
        'show_stats': True,
        'show_fit_error': True,
        'show_bin_error': True,
        'value_fmt': "{:.2g}",
        'stats_list': ["chi2/ndf"],
        'init_options': {
            'label_map': {
                'data' : "MC",
                'pdf'  : "Fit"
            }
        },
        'draw_options': {
            'comparison_options':{
                "mode": "difference",
                "ylabel": "MC - Fit",
            }
        },
        'summary_text_option': {
            'x': 0.05,
            'y': 0.9
        },
        'extra_text_option': None,
    }

    # pdf class defined in macros
    _EXTERNAL_PDF_ = ['RooTwoSidedCBShape']

    # name aliases for various pdfs
    _PDF_MAP_ = {
        'RooCrystalBall_DSCB' : 'RooCrystalBall',
        'DSCB'                : 'RooTwoSidedCBShape',
        'ExpGaussExp'         : 'RooExpGaussExpShape',
        'Exp'                 : 'RooExponential',
        'Exponential'         : 'RooExponential',
        'Bukin'               : 'RooBukinPdf',
        'Gaussian'            : 'RooGaussian',
        'Gauss'               : 'RooGaussian'
    }
    
    _DEFAULT_ROOT_CONFIG_ = {
        "SetBatch" : True,
        "TH1Sumw2" : True
    }
    
    _REQUIRE_CONFIG_ = {
        "ROOT"  : True,
        "RooFit": True
    }
    
    @property
    def plot_options(self) -> Dict[str, Any]:
        return self._plot_options
    
    @property
    def fit_options(self) -> Dict[str, Any]:
        return self._fit_options
        
    @property
    def functional_form(self) -> str:
        return self._functional_form
    
    @property
    def model_class(self) -> Callable:
        return self._model_class

    @property
    def observable(self) -> RealVariable:
        return self._observable
    
    @property
    def parameters(self) -> RealVariableSet:
        return self._parameters

    @property
    def fit_range(self) -> NamedRanges:
        return self.observable.named_ranges

    def __init__(self, functional_form:Union[str, Callable],
                 fit_range:Union[ArrayLike, Dict[str, ArrayLike]],
                 bin_range:Optional[ArrayLike]=None,
                 parameters:Optional[ParametersType]=None,
                 nbins:Optional[int]=None,
                 fit_options:Optional[Dict]=None,
                 plot_options:Optional[Dict]=None,
                 observable_name:str="observable",
                 weight_name:Optional[str]='weight',
                 verbosity:str="INFO"):
        """
        Modelling of a data distribution by a simple analytic function.
        
        Parameters:
            observable: str
                Name of observable.
        """
        self._fit_options  = mp.concat((self._DEFAULT_FIT_OPTION_, fit_options), copy=True)
        self._plot_options = mp.concat((self._DEFAULT_PLOT_OPTION_, plot_options), copy=True)
        roofit_config = {
            "MinimizerPrintLevel": self.fit_options.get("print_level", -1)
        }
        super().__init__(
            roofit_config=roofit_config,
            verbosity=verbosity
        )
        self.configure_model(functional_form, parameters)
        self.configure_observable(
            name=observable_name,
            bin_range=bin_range,
            fit_range=fit_range,
            nbins=nbins
        )
        self.weight_name = weight_name
        self.result = None

    def configure_model(
        self,
        functional_form: Union[str, Callable],
        parameters: Optional[ParametersType] = None
    ) -> None:
        self._model_class = self.get_model_class(functional_form)
        if not isinstance(functional_form, str):
            functional_form = type(functional_form).__name__
        self._functional_form = functional_form
        self._parameters = get_model_parameters(parameters or functional_form)

    def configure_observable(
        self,
        name: str = 'observable',
        fit_range: Optional[Union[ArrayLike, Dict[str, ArrayLike]]] = None,
        bin_range: Optional[ArrayLike] = None,
        nbins: Optional[int] = None
    ):
        if fit_range is None:
            fit_range = (-np.infty, np.infty)
        if not isinstance(fit_range, dict):
            fit_range = {
                'fitRange': fit_range
            }
        if bin_range is None:
            if len(fit_range) > 1:
                raise ValueError('`bin_range` must be given if multiple fit ranges are defined')
            bin_range = next(iter(fit_range.values()))
        observable = RealVariable(
            name=name,
            range=bin_range,
            named_ranges=fit_range,
            nbins=nbins
        )
        self._observable = observable
        
    @semistaticmethod
    def get_model_class(self, source:Union[str, Callable]):
        """
        Resolves the pdf class that describes the data model.

        Parameters
        ----------
            source : string or callable
                Name of the pdf or a callable representing the pdf class.
        """
        if isinstance(source, Callable):
            return source
        ROOT = cached_import("ROOT")
        pdf_name = self._PDF_MAP_.get(source, source)
        if hasattr(ROOT, pdf_name):
            return getattr(ROOT, pdf_name)

        if pdf_name in self._EXTERNAL_PDF_:
            # load definition of external pdfs
            self.load_extension(pdf_name)
            return self.get_model_class(pdf_name)
        
        raise ValueError(f'Failed to load model pdf: "{source}"')

    def create_model_pdf(self) -> "ROOT.RooAbsPdf":
        return self._create_model_pdf()[0]

    def _create_model_pdf(self) -> Tuple["ROOT.RooAbsPdf", "ROOT.RooArgSet"]:
        model_name = f"model_{self.model_class.Class_Name()}"
        observable = RooRealVar(self.observable).to_root()
        parameters = [RooRealVar(parameter).to_root() for parameter in self.parameters]
        model_pdf = self.model_class(model_name, model_name, observable, *parameters)
        ROOT = cached_import("ROOT")
        norm_var = ROOT.RooRealVar('norm', 'norm', 1, -float('inf'), float('inf'))
        ROOT.SetOwnership(norm_var, False)
        ROOT.SetOwnership(model_pdf, False)
        sum_pdf = ROOT.RooAddPdf(
            f'{model_name}_extended',
            f'{model_name}_extended',
            ROOT.RooArgList(model_pdf),
            ROOT.RooArgList(norm_var)
        )
        return sum_pdf, observable, *parameters

    def create_data_source(
        self,
        data: Union[np.ndarray, "ROOT.RooDataSet", "ROOT.TTree", "DataSource"],
        weights: Optional[np.ndarray]=None
    ) -> DataSource:
        ROOT = cached_import("ROOT")
 
        if isinstance(data, DataSource):
            return data
        kwargs = {
            'observable': self.observable,
            'weight_name': self.weight_name,
            'verbosity': self.stdout.verbosity
        }
        if isinstance(data, np.ndarray):
            from quickstats.components.modelling import ArrayDataSource
            return ArrayDataSource(data, weights=weights, **kwargs)
        elif isinstance(data, ROOT.RooDataSet):
            from quickstats.components.modelling import RooDataSetDataSource
            return RooDataSetDataSource(data, **kwargs)
        elif isinstance(data, ROOT.TTree):
            from quickstats.components.modelling import TreeDataSource
            return TreeDataSource(data, **kwargs)
        else:
            raise ValueError(f'Unsupported data type: "{type(data).__name__}"')
        
    def fit(self, data: Union[np.ndarray, "ROOT.RooDataSet", "ROOT.TTree", DataSource],
            weights: Optional[np.ndarray]=None):
        with timer() as t:
            data_source = self.create_data_source(data, weights=weights)
            dataset = data_source.as_dataset()
            if dataset.numEntries() == 0:
                raise RuntimeError('No events found in the dataset. Please make sure you have specified the '
                                   'correct fit range and that the input data is not empty.')
            fit_options = combine_dict(self.fit_options)
            do_prefit = fit_options.pop('prefit', True)
            if do_prefit:
                self.parameters.prefit(data_source)
            model_pdf = self.create_model_pdf()
            fit_tool = PdfFitTool(model_pdf, dataset, verbosity=self.stdout.verbosity)
            fit_kwargs = {}
            for key in get_argnames(fit_tool.mle_fit):
                if key in fit_options:
                    fit_kwargs[key] = fit_options[key]
            fit_kwargs['fit_range'] = ','.join(self.fit_range.names)
            fit_result = fit_tool.mle_fit(**fit_kwargs)
        if fit_result is not None:
            self.parameters.copy_data(fit_result.parameters)
        self.result = fit_result
        self.stdout.info(f"Task finished. Total time taken: {t.interval:.3f}s")
        return fit_result

    def sample_parameters(
        self,
        size: int = 1,
        norm: Optional[float] = None,
        norm_range: Optional[str] = None,
        seed: Optional[int] = None
    ) -> Dict[str, np.ndarray]:
        if self.result is None:
            raise RuntimeError('No fit result available. Did you perform a fit?')
        sampled_values = self.result.randomize_parameters(size=size, seed=seed, fmt='dict')
        if norm is None:
            return sampled_values
        pdf, observable, *parameters = self._create_model_pdf()
        ROOT = cached_import('ROOT')
        param_set = ROOT.RooArgSet()
        for parameter in parameters:
            param_set.add(parameter)
        values_list = dict_of_list_to_list_of_dict(sampled_values)
        norm_values = []
        obs_set = ROOT.RooArgSet(observable)
        dummy_set = ROOT.RooArgSet()
        norm_range = norm_range or ''
        code = pdf.getAnalyticalIntegral(obs_set, dummy_set)
        if code == 0:
            raise RuntimeError(
                'Failed to get normalization: '
                'pdf does not have analytical integral implemented'
            )
        for data in values_list:
            for key, value in data.items():
                param_set[key].setVal(value)
            integral = pdf.analyticalIntegral(code, norm_range)
            N = norm / integral
            norm_values.append(N)
        sampled_values['norm'] = np.array(norm_values)
        return sampled_values

    def get_summary(self):
        summary = {
            'configuration': {
                'functional_form': self.functional_form,
                'parameters': self.parameters.data,
                'observable': self.observable.data,
                'fit_options': mp.concat((self.fit_options,), copy=True)
            },
            'fit_result': None if self.result is None else self.result.to_dict()
        }
        return summary
        
    def create_plot(
        self,
        data: Union[np.ndarray, "ROOT.RooDataSet", "ROOT.TTree", DataSource],
        weights: Optional[np.ndarray] = None,
        saveas: Optional[str] = None,
    ):
        if not self.result:
            raise RuntimeError("No results to plot")
        from quickstats.plots import DataModelingPlot
        ROOT = cached_import("ROOT")
        data_source = self.create_data_source(data, weights=weights)
        dataset = data_source.as_dataset()
        pdf = self.create_model_pdf()
        plot_options = self.plot_options
        data_hist = dataset_to_histogram(
            dataset,
            nbins=plot_options['nbins_data'],
            bin_range=plot_options['bin_range'],
            evaluate_error=plot_options['show_bin_error'],
        )
        pdf_hist = pdf_to_histogram(
            pdf,
            observables,
            nbins=plot_options['nbins_pdf'],
            bin_range=plot_options['bin_range'],
        )
        pdf_hist_data_binning = pdf_to_histogram(
            pdf,
            observables,
            nbins=plot_options['nbins_data'],
            bin_range=plot_options['bin_range'],
        )
        fit_range = self._fit_options['fit_range']
        subranges = list(fit_range.values()) if isinstance(fit_range, dict) else None
        pdf_hist.reweight(data_hist, subranges=subranges, inplace=True)
        pdf_hist_data_binning.reweight(data_hist, subranges=subranges, inplace=True)
        if isinstance(fit_range, dict):
            def blind_condition(x, y):
                mask = np.full(x.shape, True)
                for ranges in fit_range.values():
                    mask &= ~((ranges[0] < x) & (x < ranges[1]))
                return mask
            data_hist.mask(blind_condition)
            pdf_hist.mask(blind_condition)
            pdf_hist_data_binning.mask(blind_condition)
        dfs = {
            'data': data_hist,
            'pdf': pdf_hist,
            'pdf_data_binning': pdf_hist_data_binning
            
        }
        plotter = DataModelingPlot(
            data_map=dfs,
            analytic_model=True,
            **plot_options['init_options']
        )

        summary_kwargs = {
            "value_fmt" : plot_options["value_fmt"],
            "show_params" : plot_options['show_params'],
            "show_stats" : plot_options["show_stats"],
            "show_fit_error" : plot_options["show_fit_error"],
            "stats_list" : plot_options["stats_list"]
        }
        summary_text = self.get_summary_text(**summary_kwargs)
        if summary_text:
            options = plot_options.get('summary_text_option', {})
            plotter.add_text(summary_text, **options)
        
        extra_text_option = plot_options.get("extra_text_option", None)
        if extra_text_option is not None:
            if isinstance(extra_text_option, dict):
                plotter.add_text(**extra_text_option)
            elif isinstance(extra_text_option, list):
                for options in extra_text_option:
                    plotter.add_text(**options)
            else:
                raise ValueError('invalid format for the plot option "extra_text_option"')
                
        draw_options = mp.concat((plot_options.get('draw_options'),), copy=True)
        draw_options.setdefault('xlabel', observable.GetName())
        draw_options['primary_target'] = 'data'
        if plot_options['show_comparison']:
            comparison_options = mp.concat((draw_options.get('comparison_options'),), copy=True)
            comparison_options['components'] = [
                {
                    "reference": "pdf_data_binning",
                    "target": "data",
                }
            ]
        else:
            comparison_options = None
        draw_options['comparison_options'] = comparison_options

        axes = plotter.draw(
            data_targets=['data'],
            model_targets=['pdf'],
            **draw_options
        )
        if saveas is not None:
            plotter.figure.savefig(saveas, bbox_inches="tight")
        if in_notebook():
            import matplotlib.pyplot as plt
            plt.show()
        return axes