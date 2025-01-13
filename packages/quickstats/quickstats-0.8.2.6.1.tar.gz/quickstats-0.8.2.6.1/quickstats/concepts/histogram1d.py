from __future__ import annotations

from typing import (
    Optional, Union, Tuple, Any, Callable, Sequence,
    cast, TypeVar, Dict
)
from numbers import Real

import numpy as np

from quickstats import stdout
from quickstats.core.typing import ArrayLike, NOTSET
from quickstats.maths.numerics import all_integers, safe_div
from quickstats.maths.histograms import (
    BinErrorMode,
    HistComparisonMode,
    poisson_interval,
    histogram,
    get_histogram_mask,
)
from .binning import Binning
from .ranges import MultiRange, Range

# Type aliases for better type safety
H = TypeVar('H', bound='Histogram1D')
BinErrors = Optional[Tuple[np.ndarray, np.ndarray]]
ComparisonMode = Union[HistComparisonMode, str, Callable[[H, H], H]]

class Histogram1D:
    """
    A class representing a one-dimensional histogram with bin contents, edges, and errors.

    Attributes
    ----------
    bin_content : np.ndarray
        The bin content of the histogram
    bin_errors : Optional[Tuple[np.ndarray, np.ndarray]]
        The bin errors (lower, upper) if available
    bin_edges : np.ndarray
        The bin edges of the histogram
    bin_centers : np.ndarray
        The bin centers of the histogram
    bin_widths : np.ndarray
        The widths of the bins
    nbins : int 
        The number of bins
    error_mode : BinErrorMode
        The current error mode
    """
    
    def __init__(
        self,
        bin_content: np.ndarray,
        bin_edges: np.ndarray,
        bin_errors: Union[NOTSET, ArrayLike, None] = NOTSET,
        error_mode: Union[BinErrorMode, str] = "auto"
    ) -> None:
        """
        Initialize a Histogram1D instance.

        Parameters
        ----------
        bin_content : np.ndarray
            The bin content of the histogram
        bin_edges : np.ndarray 
            The bin edges of the histogram
        bin_errors : Optional[ArrayLike], default NOTSET
            The bin errors of the histogram. Supported formats:
            - NOTSET (default): Deduced
            - None: No errors
            - scalar: Same error for all bins
            - 1D array: Symmetric errors, length must match bins
            - 2D array: Asymmetric errors, shape must be (2, nbins)
            - Tuple[array, array]: Asymmetric errors, each array length matches bins
            If NOTSET, the bin errors will be automatically calculated if 
            Poisson error mode is used, otherwise bin errors will be set to None (i.e. no error).
        error_mode : Union[BinErrorMode, str], default "auto"
            The method for error calculation. It can
            be "sumw2" (symmetric error from Wald approximation), "poisson"
            (Poisson interval at one sigma), or "auto" (deduced from bin content)

        Raises
        ------
        ValueError
            If bin_content or bin_edges are not 1D arrays
            If arrays have incompatible sizes
        """
        self.set_data(
            bin_content=bin_content,
            bin_edges=bin_edges,
            bin_errors=bin_errors,
            error_mode=error_mode,
        )
    
    def __add__(self, other: Union[Histogram1D, Real]) -> Histogram1D:
        """Add another histogram or scalar value."""
        return self._operate("add", other)

    def __sub__(self, other: Union[Histogram1D, Real]) -> Histogram1D:
        """Subtract another histogram or scalar value."""
        return self._operate("sub", other)

    def __mul__(self, other: Union[Real, ArrayLike]) -> Histogram1D:
        """Multiply by a scalar or array."""
        return self._operate("scale", other)

    def __rmul__(self, other: Union[Real, ArrayLike]) -> Histogram1D:
        """Right multiplication by a scalar or array."""
        return self._operate("scale", other)

    def __truediv__(self, other: Union[Histogram1D, Union[Real, ArrayLike]]) -> Histogram1D:
        """Divide by another histogram, scalar, or array."""
        instance = self._operate("div", other)
        # Ensure that bin content is treated as weighted after division
        instance._bin_content = instance._bin_content.astype(float)
        return instance
        
    def __iadd__(self, other: Union[Histogram1D, Real]) -> Histogram1D:
        """In-place addition with histogram or scalar."""
        return self._ioperate("add", other)

    def __isub__(self, other: Union[Histogram1D, Real]) -> Histogram1D:
        """In-place subtraction with histogram or scalar."""
        return self._ioperate("sub", other)

    def __itruediv__(self, other: Union[Histogram1D, Real, ArrayLike]) -> Histogram1D:
        """In-place division by histogram or scalar."""
        return self._ioperate("div", other)

    def __imul__(self, other: Union[Real, ArrayLike]) -> Histogram1D:
        """
        In-place multiplication by scalar or array.

        Parameters
        ----------
        other : Union[Real, ArrayLike]
            Scalar or array to multiply by

        Returns
        -------
        Histogram1D
            Self multiplied by other
        """
        return self._ioperate("scale", other)
        
    def _operate(
        self,
        method: str,
        other: Any
    ) -> Histogram1D:
        """
        Perform operations on histogram data.

        Parameters
        ----------
        method : str
            The operation to perform ('add', 'sub', 'div', 'scale')
        other : Any
            The other operand (histogram, scalar, or array)

        Returns
        -------
        Histogram1D
            A new histogram with the operation result

        Raises
        ------
        ValueError
            If operation is invalid or operands are incompatible
        """
        operation = getattr(self, f"_{method}", None)
        if operation is None:
            raise ValueError(f'Invalid operation: "{method}"')
            
        bin_content, bin_errors = operation(other)
        bin_content_raw, bin_errors_raw = self._operate_masked(method, other)
        
        if isinstance(other, Histogram1D):
            error_mode = self._resolve_error_mode(bin_content, other._error_mode)
        else:
            error_mode = self._error_mode
            
        mask = self._combine_mask(other)
        self._apply_mask(mask, bin_content, bin_errors)
        
        instance = type(self)(
            bin_content=bin_content,
            bin_edges=self._binning._bin_edges,
            bin_errors=bin_errors,
            error_mode=error_mode,
        )

        instance._bin_content_raw = bin_content_raw
        instance._bin_errors_raw = bin_errors_raw
        instance._mask = mask
        return instance

    def _operate_masked(
        self,
        method: str,
        other: Any
    ) -> Tuple[Optional[np.ndarray], BinErrors]:
        """
        Handle operations with masked histograms.

        Parameters
        ----------
        method : str
            Operation to perform
        other : Any
            Other operand

        Returns
        -------
        Tuple[Optional[np.ndarray], BinErrors]
            Raw bin content and errors if masked, else (None, None)
        """
        self_masked = self.is_masked()
        other_masked = isinstance(other, Histogram1D) and other.is_masked()
        
        if not (self_masked or other_masked):
            return None, None
            
        self_copy = self.copy()
        other_copy = other.copy() if isinstance(other, Histogram1D) else other
        
        if self_masked:
            self_copy.unmask()
        if other_masked:
            other_copy.unmask()
            
        operation = getattr(self_copy, f"_{method}")
        return operation(other_copy)
        
    def _ioperate(self, method: str, other: Any) -> Histogram1D:
        """
        Perform in-place operation.

        Parameters
        ----------
        method : str
            Operation to perform ('add', 'sub', 'div', 'scale')
        other : Any
            Other operand

        Returns
        -------
        Histogram1D
            Self with operation applied

        Raises
        ------
        ValueError
            If operation is invalid
        """
        if not hasattr(self, f"_{method}"):
            raise ValueError(f'Invalid operation: "{method}"')
            
        operation = getattr(self, f"_{method}")
        bin_content, bin_errors = operation(other)
        bin_content_raw, bin_errors_raw = self._operate_masked(method, other)
        
        if isinstance(other, Histogram1D):
            self._error_mode = self._resolve_error_mode(
                bin_content, other._error_mode
            )
            
        mask = self._combine_mask(other)
        self._apply_mask(mask, bin_content, bin_errors)
        
        self._bin_content = bin_content
        self._bin_errors = bin_errors
        self._bin_content_raw = bin_content_raw
        self._bin_errors_raw = bin_errors_raw
        self._mask = mask
        
        return self        

    def _combine_mask(self, other: Any) -> np.ndarray:
        """
        Combine masks between operands.

        Parameters
        ----------
        other : Any
            Other operand

        Returns
        -------
        np.ndarray
            Combined mask or None if no masks exist
        """
        mask = self._mask
        if isinstance(other, Histogram1D) and other.is_masked():
            if mask is None:
                mask = other._mask.copy()
            else:
                mask = mask | other._mask
        return mask.copy() if mask is not None else None

    def _apply_mask(
        self,
        mask: np.ndarray,
        bin_content: np.ndarray,
        bin_errors: BinErrors
    ) -> None:
        """
        Apply mask to bin content and errors.

        Parameters
        ----------
        mask : np.ndarray
            Mask to apply
        bin_content : np.ndarray
            Bin content to mask
        bin_errors : BinErrors
            Bin errors to mask
        """
        if mask is None:
            return
            
        bin_content[mask] = 0
        if bin_errors is not None:
            bin_errors[0][mask] = 0.0
            bin_errors[1][mask] = 0.0

    def _validate_other(self, other: Histogram1D) -> None:
        """
        Validate compatibility of another histogram.

        Parameters
        ----------
        other : Histogram1D
            Histogram to validate

        Raises
        ------
        ValueError
            If histograms are incompatible
        """
        if not isinstance(other, Histogram1D):
            raise ValueError(
                "Operation only allowed between Histogram1D objects"
            )
        if self.binning != other.binning:
            raise ValueError(
                "Operations not allowed between histograms with different binning"
            )

    def _resolve_error_mode(
        self,
        bin_content: np.ndarray,
        other_mode: BinErrorMode
    ) -> BinErrorMode:
        """
        Resolve error mode for operations.

        Parameters
        ----------
        bin_content : np.ndarray
            Current bin content
        other_mode : BinErrorMode
            Other histogram's error mode

        Returns
        -------
        BinErrorMode
            Resolved error mode
        """
        # Prefer Poisson errors if possible
        use_poisson = (
            bin_content.dtype == np.int64 or
            self._error_mode == BinErrorMode.POISSON or
            other_mode == BinErrorMode.POISSON
        )
        return BinErrorMode.POISSON if use_poisson else BinErrorMode.SUMW2

    def _scale(
        self,
        val: Union[Real, ArrayLike]
    ) -> Tuple[np.ndarray, BinErrors]:
        """
        Scale histogram contents.

        Parameters
        ----------
        val : Union[Real, ArrayLike]
            Scaling factor

        Returns
        -------
        Tuple[np.ndarray, BinErrors]
            Scaled bin content and errors

        Raises
        ------
        ValueError
            If scaling array has invalid shape
        """
        val = np.asarray(val)
        is_weighted = self.is_weighted()

        # Handle integer scaling
        if not is_weighted and all_integers(val):
            val = val.astype(np.int64)
            if not np.all(val >= 0):
                stdout.warning(
                    "Scaling unweighted histogram by negative values "
                    "will make it weighted and force sumw2 errors"
                )
                val = val.astype(float)
        else:
            val = val.astype(float)

        # Validate scaling array shape
        if val.ndim > 1:
            raise ValueError(f"Cannot scale with {val.ndim}-dimensional value")
        if val.ndim == 1 and val.size != self.nbins:
            raise ValueError(
                f"Scaling array size ({val.size}) doesn't match bins ({self.nbins})"
            )

        bin_content = self._bin_content * val

        if self._bin_errors is None:
            return bin_content, None

        # Handle errors based on content type
        if bin_content.dtype == np.int64:
            bin_errors = poisson_interval(bin_content)
            if self.is_masked():
                bin_errors[0][self._mask] = 0.0
                bin_errors[1][self._mask] = 0.0
        else:
            errlo, errhi = self._bin_errors
            bin_errors = (val * errlo, val * errhi)

        return bin_content, bin_errors

    def _add(
        self,
        other: Union[Histogram1D, Real],
        neg: bool = False
    ) -> Tuple[np.ndarray, BinErrors]:
        """
        Add/subtract histograms or scalar.

        Parameters
        ----------
        other : Union[Histogram1D, Real]
            Value to add/subtract
        neg : bool, default False
            True for subtraction

        Returns
        -------
        Tuple[np.ndarray, BinErrors]
            The resulting bin content and bin errors.
        """
        if isinstance(other, Real):
            # Convert scalar to histogram
            bin_content = np.full(
                self._bin_content.shape,
                other,
                dtype=self._bin_content.dtype
            )
            bin_errors = (
                np.zeros_like(self._bin_content),
                np.zeros_like(self._bin_content)
            )
            other = type(self)(
                bin_content=bin_content,
                bin_edges=self._binning._bin_edges,
                bin_errors=bin_errors,
            )
            
        self._validate_other(other)
        
        # Perform addition/subtraction
        bin_content = (
            self._bin_content - other._bin_content if neg
            else self._bin_content + other._bin_content
        )

        if self._bin_errors is None and other._bin_errors is None:
            return bin_content, None

        # Handle errors
        if self._bin_errors is not None and other._bin_errors is not None:
            use_poisson = False
            if bin_content.dtype == np.int64:
                if np.all(bin_content >= 0):
                    use_poisson = True
                else:
                    stdout.warning(
                        "Negative bin content - forcing sumw2 errors"
                    )

            if use_poisson:
                bin_errors = poisson_interval(bin_content)
                if self.is_masked():
                    bin_errors[0][self._mask] = 0.0
                    bin_errors[1][self._mask] = 0.0
            else:
                errlo = np.sqrt(
                    self._bin_errors[0] ** 2 + other._bin_errors[0] ** 2
                )
                errhi = np.sqrt(
                    self._bin_errors[1] ** 2 + other._bin_errors[1] ** 2
                )
                bin_errors = (errlo, errhi)
        else:
            bin_errors = (
                self._bin_errors if self._bin_errors is not None
                else other._bin_errors
            )

        return bin_content, bin_errors

    def _sub(
        self,
        other: Union[Histogram1D, Real]
    ) -> Tuple[np.ndarray, BinErrors]:
        """
        Subtract another histogram from the current histogram.

        Parameters
        ----------
        other : Histogram1D
            The other histogram to subtract.

        Returns
        -------
        Tuple[np.ndarray, BinErrors]
            The resulting bin content and bin errors.
        """
        return self._add(other, neg=True)
        
    def _div(
        self,
        other: Union[Histogram1D, Real, ArrayLike]
    ) -> Tuple[np.ndarray, BinErrors]:
        """
        Divide histogram by another histogram or scalar.

        Parameters
        ----------
        other : Union[Histogram1D, Union[Real, ArrayLike]]
            Divisor (histogram or scalar/array)

        Returns
        -------
        Tuple[np.ndarray, BinErrors]
            Resulting bin content and errors

        Raises
        ------
        ValueError
            If division by zero occurs
            If histograms have incompatible binning
        """
        if not isinstance(other, Histogram1D):
            # Handle scalar division
            if np.any(other == 0):
                raise ValueError("Division by zero")
            return self._scale(1.0 / other)

        self._validate_other(other)
        bin_content = safe_div(self._bin_content, other._bin_content, True)

        # Force float type for division results
        bin_content = bin_content.astype(float)

        if self._bin_errors is None and other._bin_errors is None:
            return bin_content, None

        # Handle errors
        err1 = self._bin_errors or (np.zeros(self.nbins), np.zeros(self.nbins))
        err2 = other._bin_errors or (np.zeros(other.nbins), np.zeros(other.nbins))
        
        errlo, errhi = self._calculate_division_errors(
            self._bin_content,
            other._bin_content,
            err1,
            err2
        )
        
        if self.is_masked():
            errlo[self._mask] = 0.0
            errhi[self._mask] = 0.0
            
        return bin_content, (errlo, errhi)

    @staticmethod
    def _calculate_division_errors(
        num: np.ndarray,
        den: np.ndarray,
        num_errs: Tuple[np.ndarray, np.ndarray],
        den_errs: Tuple[np.ndarray, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate errors for histogram division.

        Uses error propagation formula for ratio: σ(a/b)² = (a/b)² * (σa²/a² + σb²/b²)

        Parameters
        ----------
        num : np.ndarray
            Numerator values
        den : np.ndarray
            Denominator values
        num_errs : Tuple[np.ndarray, np.ndarray]
            Numerator errors (low, high)
        den_errs : Tuple[np.ndarray, np.ndarray]
            Denominator errors (low, high)

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Resulting low and high errors
        """
        den_sq = den * den
        errlo = safe_div(
            np.sqrt(num_errs[0]**2 * den_sq + den_errs[0]**2 * num * num),
            den_sq * den_sq,
            False
        )
        errhi = safe_div(
            np.sqrt(num_errs[1]**2 * den_sq + den_errs[1]**2 * num * num),
            den_sq * den_sq,
            False
        )
        return errlo, errhi

    @staticmethod
    def _regularize_errors(
        bin_content: np.ndarray,
        bin_errors: Optional[ArrayLike] = None
    ) -> BinErrors:
        """
        Convert bin errors to standard format.

        Converts various error input formats to the standard 
        (lower_errors, upper_errors) tuple format.

        Parameters
        ----------
        bin_content : np.ndarray
            The histogram bin content
        bin_errors : Optional[ArrayLike], default None
            Bin errors in one of several formats:
            - None: No errors
            - scalar: Same error for all bins
            - 1D array: Symmetric errors, length must match bins
            - 2D array: Asymmetric errors, shape must be (2, nbins)
            - Tuple[array, array]: Asymmetric errors, each array length matches bins

        Returns
        -------
        BinErrors
            Tuple of (lower_errors, upper_errors) arrays, or None

        Raises
        ------
        ValueError
            If error array has invalid shape or size
        """
        if bin_errors is None:
            return None

        size = bin_content.size
        
        # Handle scalar errors
        if np.isscalar(bin_errors):
            err = np.full(size, bin_errors, dtype=float)
            return (err, err)
            
        bin_errors = np.asarray(bin_errors)
        
        # Handle 1D error array
        if bin_errors.ndim == 1:
            if bin_errors.size != size:
                raise ValueError(
                    "Error array size must match bin content size"
                )
            return (bin_errors, bin_errors)
            
        # Handle 2D error array
        if bin_errors.ndim == 2:
            if bin_errors.shape != (2, size):
                raise ValueError(
                    "2D error array must have shape (2, nbins)"
                )
            return (bin_errors[0], bin_errors[1])
            
        raise ValueError(
            f"Error array has invalid dimension: {bin_errors.ndim}"
        )

    def set_data(
        self,
        bin_content: np.ndarray,
        bin_edges: np.ndarray,
        bin_errors: Optional[ArrayLike] = NOTSET,
        error_mode: Union[BinErrorMode, str] = "auto",
    ) -> None:
        """
        Set the histogram data.

        Parameters
        ----------
        bin_content : np.ndarray
            The bin contents
        bin_edges : np.ndarray
            The bin edges
        bin_errors : Union[ArrayLike, None, NOTSET], default None
            The bin errors in any valid format
        error_mode : Union[BinErrorMode, str], default "auto"
            Error calculation mode

        Raises
        ------
        ValueError
            If data arrays have invalid shapes or sizes
            If bin_content and bin_edges sizes don't match
        """
        # Validate input arrays
        bin_content = np.asarray(bin_content)
        if bin_content.ndim != 1:
            raise ValueError("Bin content must be 1-dimensional")

        bin_edges = np.asarray(bin_edges)
        if bin_edges.ndim != 1:
            raise ValueError("Bin edges must be 1-dimensional")

        if bin_content.size != (bin_edges.size - 1):
            raise ValueError(
                f"Expected {bin_edges.size - 1} bins from edges, "
                f"got {bin_content.size} from content"
            )

        # Create binning object
        binning = Binning(bins=bin_edges)
        error_mode = BinErrorMode.parse(error_mode)

        # Determine content type and error mode
        is_poisson_data = all_integers(bin_content) and not np.all(bin_content == 0)
        if error_mode == BinErrorMode.AUTO:
            error_mode = (
                BinErrorMode.POISSON if is_poisson_data
                else BinErrorMode.SUMW2
            )

        # Set content type based on error mode
        if error_mode == BinErrorMode.POISSON and is_poisson_data:
            bin_content = bin_content.astype(np.int64)
        else:
            bin_content = bin_content.astype(float)

        # Handle errors
        if bin_errors is NOTSET:
            if error_mode == BinErrorMode.POISSON:
                bin_errors = poisson_interval(bin_content)
            else:
                bin_errors = None
        bin_errors = self._regularize_errors(bin_content, bin_errors)
        
        # Set attributes
        self._bin_content = bin_content
        self._binning = binning
        self._bin_errors = bin_errors
        self._error_mode = error_mode
        self._bin_content_raw = None
        self._bin_errors_raw = None
        self._mask = None

    @classmethod
    def create(
        cls,
        x: np.ndarray,
        weights: Optional[np.ndarray] = None,
        bins: Union[int, ArrayLike] = 10,
        bin_range: Optional[ArrayLike] = None,
        underflow: bool = False,
        overflow: bool = False,
        divide_bin_width: bool = False,
        normalize: bool = False,
        clip_weight: bool = False,
        evaluate_error: bool = True,
        error_mode: Union[BinErrorMode, str] = "auto",
    ) -> Histogram1D:
        """
        Create a histogram from array data.

        Parameters
        ----------
        x : np.ndarray
            Input data to histogram
        weights : Optional[np.ndarray], default None
            Optional weights for each data point
        bins : Union[int, ArrayLike], default 10
            Number of bins or bin edges
        bin_range : Optional[ArrayLike], default None
            Optional (min, max) range for binning
        underflow : bool, default False
            Include underflow in first bin
        overflow : bool, default False
            Include overflow in last bin
        divide_bin_width : bool, default False
            Normalize by bin width
        normalize : bool, default False
            Normalize histogram to unit area
        clip_weight : bool, default False
            Ignore out-of-range weights
        evaluate_error : bool, default True
            Calculate bin errors
        error_mode : Union[BinErrorMode, str], default "auto"
            Error calculation mode

        Returns
        -------
        Histogram1D
            New histogram instance
        """
        bin_content, bin_edges, bin_errors = histogram(
            x=x,
            weights=weights,
            bins=bins,
            bin_range=bin_range,
            underflow=underflow,
            overflow=overflow,
            divide_bin_width=divide_bin_width,
            normalize=normalize,
            clip_weight=clip_weight,
            evaluate_error=evaluate_error,
            error_mode=error_mode,
        )

        return cls(
            bin_content=bin_content,
            bin_edges=bin_edges,
            bin_errors=bin_errors,
            error_mode=error_mode,
        )
        
    @property
    def bin_content(self) -> np.ndarray:
        """Get copy of bin content array."""
        return self._bin_content.copy()

    @property
    def binning(self) -> Binning:
        """Get binning object."""
        return self._binning

    @property
    def bin_edges(self) -> np.ndarray:
        """Get bin edges array."""
        return self._binning.bin_edges

    @property
    def bin_centers(self) -> np.ndarray:
        """Get bin centers array."""
        return self._binning.bin_centers

    @property
    def bin_widths(self) -> np.ndarray:
        """Get bin widths array."""
        return self._binning.bin_widths

    @property
    def nbins(self) -> int:
        """Get number of bins."""
        return self._binning.nbins

    @property
    def bin_range(self) -> Tuple[float, float]:
        """Get (min, max) bin range."""
        return self._binning.bin_range

    @property
    def uniform_binning(self) -> bool:
        """Check if binning is uniform."""
        return self._binning.is_uniform()

    @property
    def bin_errors(self) -> BinErrors:
        """
        Get bin errors.

        Returns
        -------
        BinErrors
            Tuple of (lower_errors, upper_errors) arrays or None
        """
        if self._bin_errors is None:
            return None
        return (
            self._bin_errors[0].copy(),
            self._bin_errors[1].copy()
        )

    @property
    def bin_errlo(self) -> Optional[np.ndarray]:
        """Get lower bin errors array."""
        if self._bin_errors is None:
            return None
        return self._bin_errors[0].copy()

    @property
    def bin_errhi(self) -> Optional[np.ndarray]:
        """Get upper bin errors array."""
        if self._bin_errors is None:
            return None
        return self._bin_errors[1].copy()

    @property
    def rel_bin_errors(self) -> BinErrors:
        """Get relative bin errors with content."""
        if self._bin_errors is None:
            return None
        errlo = self._bin_content - self._bin_errors[0]
        errhi = self._bin_content + self._bin_errors[1]
        return (errlo, errhi)

    @property
    def rel_bin_errlo(self) -> Optional[np.ndarray]:
        """Get relative lower bin errors with content."""
        if self._bin_errors is None:
            return None
        return self._bin_content - self._bin_errors[0]

    @property
    def rel_bin_errhi(self) -> Optional[np.ndarray]:
        """Get relative upper bin errors with content."""
        if self._bin_errors is None:
            return None
        return self._bin_content + self._bin_errors[1]

    @property
    def error_mode(self) -> BinErrorMode:
        """Get current error mode."""
        return self._error_mode

    @property
    def bin_mask(self) -> np.ndarray:
        """Get bin mask array if any."""
        if self._mask is None:
            return None
        return self._mask.copy()

    def has_errors(self) -> bool:
        """Check if histogram has errors."""
        return self._bin_errors is not None

    def is_weighted(self) -> bool:
        """
        Check if histogram is weighted.

        Returns True if bin content is non-integer type.
        """
        return self._bin_content.dtype != np.int64

    def is_empty(self) -> bool:
        """Check if histogram is empty (zero sum)."""
        return np.sum(self._bin_content) == 0

    def sum(self) -> Union[float, int]:
        """
        Calculate sum of bin contents.

        Returns
        -------
        Union[float, int]
            Sum, preserving integer type if unweighted
        """
        return self._bin_content.sum()

    def integral(self, subranges: Optional[Union[List[ArrayLike], MultiRange]]=None) -> float:
        """
        Calculate histogram integral.

        Returns
        -------
        float
            Integral (sum of bin contents * bin widths)
        """
        if subranges is None:
            return np.sum(self.bin_widths * self._bin_content)
        if isinstance(subranges, MultiRange):
            subranges = subranges.to_list()
        sums = 0.
        bin_centers = self.bin_centers
        for subrange in subranges:
            vmin, vmax = subrange
            mask = (vmin < bin_centers) & (bin_centers < vmax)
            sums += np.sum(self.bin_widths[mask] * self._bin_content[mask])
        return sums

    def copy(self) -> Histogram1D:
        """
        Create a deep copy of histogram.

        Returns
        -------
        Histogram1D
            New histogram instance with copied data
        """
        instance = type(self)(
            bin_content=self.bin_content,
            bin_edges=self.bin_edges,
            bin_errors=self.bin_errors,
            error_mode=self.error_mode,
        )
        if self.is_masked():
            instance._bin_content_raw = self._bin_content_raw.copy()
            if self.has_errors():
                instance._bin_errors_raw = (
                    self._bin_errors_raw[0].copy(),
                    self._bin_errors_raw[1].copy(),
                )
            instance._mask = self._mask.copy()
        return instance

    def mask(
        self,
        condition: Union[Sequence[float], Callable]
    ) -> None:
        """
        Apply mask to histogram data.

        Parameters
        ----------
        condition : Union[Sequence[float], Callable]
            Either [min, max] range or function returning bool
            for each bin

        Examples
        --------
        >>> hist.mask([1.0, 2.0])  # Mask bins outside [1, 2]
        >>> hist.mask(lambda x: x > 0)  # Mask bins where x <= 0
        """
        x = self.bin_centers
        has_errors = self.has_errors()

        # Store raw data if needed
        if self._bin_content_raw is None:
            self._bin_content_raw = self._bin_content.copy()
            if has_errors:
                self._bin_errors_raw = (
                    self._bin_errors[0].copy(),
                    self._bin_errors[1].copy(),
                )
            y = self._bin_content
            yerr = self._bin_errors
        else:
            y = self._bin_content_raw
            yerr = self._bin_errors_raw

        mask = get_histogram_mask(x=x, y=y, condition=condition)
        y[mask] = 0
        if has_errors:
            yerr[0][mask] = 0.0
            yerr[1][mask] = 0.0
        self._mask = mask

    def unmask(self) -> None:
        """Remove mask and restore original data."""
        if self.is_masked():
            self._bin_content = self._bin_content_raw
            self._bin_errors = self._bin_errors_raw
            self._bin_content_raw = None
            self._bin_errors_raw = None
            self._mask = None

    def is_masked(self) -> bool:
        """Check if histogram has mask applied."""
        return self._bin_content_raw is not None

    def scale(
        self,
        val: Union[Real, ArrayLike],
        inplace: bool = False
    ) -> Histogram1D:
        """
        Scale histogram by value.

        Parameters
        ----------
        val : Union[Real, ArrayLike]
            Scale factor(s)
        inplace : bool, default False
            If True, modify in place

        Returns
        -------
        Histogram1D
            Scaled histogram
        """
        if inplace:
            return self._ioperate("scale", val)
        return self._operate("scale", val)

    def normalize(
        self,
        density: bool = False,
        inplace: bool = False
    ) -> Histogram1D:
        """
        Normalize histogram.

        Parameters
        ----------
        density : bool, default False
            If True, normalize by bin widths
        inplace : bool, default False
            If True, modify in place

        Returns
        -------
        Histogram1D
            Normalized histogram
        """
        norm_factor = float(self.sum())
        if norm_factor == 0:
            return self.copy() if not inplace else self
            
        if density:
            norm_factor *= self.bin_widths

        if inplace:
            return self._ioperate("div", norm_factor)
        return self._operate("div", norm_factor)

    def reweight(
        self,
        other: Histogram1D,
        subranges: Optional[Union[List[ArrayLike], MultiRange]]=None,
        inplace: bool = False,
    ):
        if not isinstance(other, Histogram1D):
            raise ValueError('Operation only allowed between Histogram1D objects')
        if isinstance(subranges, MultiRange):
            subranges = subranges.to_list()            
        scale_factor = other.integral(subranges=subranges) / self.integral(subranges=subranges)
        return self.scale(scale_factor, inplace=inplace)        

    def compare(
        self,
        reference: Histogram1D,
        mode: ComparisonMode = "ratio"
    ) -> Histogram1D:
        """
        Compare with reference histogram.

        Parameters
        ----------
        reference : Histogram1D
            Reference histogram
        mode : ComparisonMode, default "ratio"
            Comparison mode ("ratio", "difference" or callable)

        Returns
        -------
        Histogram1D
            Comparison histogram

        Raises
        ------
        ValueError
            For invalid comparison mode
        """
        if callable(mode):
            return mode(self, reference)
            
        mode = HistComparisonMode.parse(mode)
        if mode == HistComparisonMode.RATIO:
            return self / reference
        elif mode == HistComparisonMode.DIFFERENCE:
            return self - reference
            
        raise ValueError(f"Unknown comparison mode: {mode}")

    def remove_errors(self) -> None:
        self._bin_errors = None
        self._biin_errors_raw = None

    def get_mean(self) -> float:
        x, y = self.bin_centers, self._bin_content
        return np.sum(x * y) / np.sum(y)

    def get_std(self) -> float:
        mean = self.get_mean()
        x, y = self.bin_centers, self._bin_content
        count = np.sum(y)
        if count == 0.0:
            return 0.0
        # for negative stddev (e.g. when having negative weights) - return std=0
        std2 = np.max([np.sum(y * (x - mean) ** 2) / count, 0.0])
        return np.sqrt(std2)

    def get_effective_entries(self) -> float:
        if self._error_mode == BinErrorMode.POISSON:
            return np.sum(self._bin_content)
        if self._bin_errors is None:
            return 0.
        sumw2 = np.sum(self._bin_errors[0] ** 2)
        if sumw2 != 0.0:
            return (np.sum(self._bin_content) ** 2) / sumw2

    def get_mean_error(self) -> float:
        neff = self.get_effective_entries()
        if neff > 0.0:
            std = self.get_std()
            return std / np.sqrt(neff)
        return 0.0

    def get_cumul_hist(self) -> Histogram1D:
        bin_content = np.cumsum(self._bin_content)
        if self._bin_errors is not None:
            bin_errors = (
                np.sqrt(np.cumsum(self._bin_errors[0] ** 2)),
                np.sqrt(np.cumsum(self._bin_errors[1] ** 2))
            )
        else:
            bin_errors = None
        return Histogram1D(
            bin_content=bin_content,
            bin_edges=self.bin_edges,
            bin_errors=bin_errors,
            error_mode=self._error_mode
        )
        
    def get_maximum(self) -> float:
        return np.max(self._bin_content)

    def get_minimum(self) -> float:
        return np.min(self._bin_content)

    def get_maximum_bin(self) -> int:
        return np.argmax(self._bin_content)

    def get_minimum_bin(self) -> int:
        return np.argmin(self._bin_content)

    def get_bin_content_slice(
        self,
        first_bin: Optional[int] = None,
        last_bin: Optional[int] = None,
    ) -> np.ndarray:
        if first_bin is None:
            first_bin = 0
        if last_bin is None:
            last_bin = self.nbins
        return self._bin_content[first_bin : last_bin]

    def get_first_bin_above(
        self,
        threshold: float,
        first_bin: Optional[int] = None,
        last_bin: Optional[int] = None
    ) -> Optional[int]:
        bin_content = self.get_bin_content_slice(
            first_bin, last_bin
        )
        indices = np.where(bin_content > threshold)[0]
        if len(indices):
            return indices[0] + (first_bin or 0)
        return None

    def get_last_bin_above(
        self,
        threshold: float,
        first_bin: Optional[int] = None,
        last_bin: Optional[int] = None
    ) -> int:
        bin_content = self.get_bin_content_slice(
            first_bin, last_bin
        )
        indices = np.where(bin_content > threshold)[0]
        if len(indices):
            return indices[-1] + (first_bin or 0)
        return None