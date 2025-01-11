"""
Enhanced binning utilities for numerical data analysis.

This module provides a flexible class for defining and manipulating binning information,
supporting both uniform and non-uniform bins with comprehensive validation and error handling.
"""

from __future__ import annotations

from typing import (
    Optional, Union, Tuple, ClassVar,
    overload, cast
)
from dataclasses import dataclass
from copy import deepcopy

import numpy as np
from numpy.typing import ArrayLike, NDArray

from quickstats.maths.statistics import bin_edge_to_bin_center
from .ranges import Range

class BinningError(Exception):
    """Base exception for binning-related errors."""
    pass

@dataclass
class BinningConfig:
    """Configuration for binning operations."""
    min_bins: int = 1
    min_edges: int = 2
    rtol: float = 1e-05  # Relative tolerance for float comparisons
    atol: float = 1e-08  # Absolute tolerance for float comparisons

class Binning:
    """
    A class for defining and manipulating binning information.
    
    This class provides functionality for creating and managing bin definitions,
    supporting both uniform and non-uniform binning with comprehensive validation.

    Parameters
    ----------
    bins : Union[ArrayLike, int]
        Either bin edges array or number of bins
    bin_range : Optional[ArrayLike], default None
        Range for bin creation when bins is an integer (low, high)

    Raises
    ------
    BinningError
        If initialization parameters are invalid
    ValueError
        If input values are out of valid ranges

    Examples
    --------
    >>> # Create uniform binning with 10 bins
    >>> binning = Binning(10, (0, 1))
    >>> print(binning.nbins)
    10

    >>> # Create custom binning with specific edges
    >>> edges = [0, 1, 2, 4, 8]
    >>> binning = Binning(edges)
    >>> print(binning.bin_widths)
    array([1, 1, 2, 4])
    """

    # Class-level configuration
    config: ClassVar[BinningConfig] = BinningConfig()

    def __init__(
        self,
        bins: Union[ArrayLike, int],
        bin_range: Optional[Union[Range, ArrayLike]] = None
    ) -> None:
        """Initialize binning with edges or number of bins."""
        try:
            self._bin_edges = self._init_bin_edges(bins, bin_range)
        except Exception as e:
            raise BinningError(f"Failed to initialize binning: {str(e)}") from e

    def _init_bin_edges(
        self,
        bins: Union[ArrayLike, int],
        bin_range: Optional[ArrayLike]
    ) -> NDArray:
        """
        Initialize bin edges with validation.

        Parameters
        ----------
        bins : Union[ArrayLike, int]
            Bin specification
        bin_range : Optional[ArrayLike]
            Optional range for bin creation

        Returns
        -------
        NDArray
            Validated bin edges array

        Raises
        ------
        ValueError
            If bin specification is invalid
        """
        if np.ndim(bins) == 1:
            return self._init_from_edges(np.asarray(bins))
        
        if np.ndim(bins) == 0:
            return self._init_from_count(
                cast(int, bins),
                bin_range
            )
        
        raise ValueError(
            "Invalid bins parameter. Must be either bin edges array or bin count."
        )

    def _init_from_edges(self, edges: NDArray) -> NDArray:
        """Initialize from explicit bin edges."""
        if len(edges) < self.config.min_edges:
            raise ValueError(
                f"Number of bin edges must be at least {self.config.min_edges}"
            )
        
        if not np.all(np.diff(edges) > 0):
            raise ValueError("Bin edges must be strictly increasing")
            
        return edges

    def _init_from_count(
        self,
        nbins: int,
        bin_range: Optional[Union[Range, ArrayLike]]
    ) -> NDArray:
        """Initialize from bin count and range."""
        if not isinstance(nbins, int) or nbins < self.config.min_bins:
            raise ValueError(
                f"Number of bins must be integer >= {self.config.min_bins}"
            )
            
        if bin_range is None:
            raise ValueError("bin_range required when specifying bin count")

        bin_range = Range.create(bin_range)
        if not bin_range.is_finite():
            return np.full(nbins + 1, np.nan)
        return np.linspace(bin_range.min, bin_range.max, nbins + 1)

    def __copy__(self) -> Binning:
        """
        Create a shallow copy.

        Returns
        -------
        Binning
            New instance with copy of bin edges
        """
        new_instance = self.__class__(self._bin_edges.copy())
        return new_instance

    def __deepcopy__(self, memo: dict) -> Binning:
        """
        Create a deep copy.

        Parameters
        ----------
        memo : dict
            Memo dictionary for deepcopy

        Returns
        -------
        Binning
            New instance with deep copy of bin edges
        """
        new_instance = self.__class__(deepcopy(self._bin_edges, memo))
        return new_instance

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Binning instance.

        Parameters
        ----------
        other : object
            Object to compare with

        Returns
        -------
        bool
            True if binnings are equal
        """
        if not isinstance(other, Binning):
            return NotImplemented
        
        return (
            self.bin_edges.shape == other.bin_edges.shape and
            np.allclose(
                self.bin_edges,
                other.bin_edges,
                rtol=self.config.rtol,
                atol=self.config.atol
            )
        )

    def __repr__(self) -> str:
        """Create string representation."""
        return (
            f"{self.__class__.__name__}("
            f"edges=[{self.bin_edges[0]}, ..., {self.bin_edges[-1]}], "
            f"nbins={self.nbins})"
        )

    @property
    def bin_edges(self) -> NDArray:
        """
        Get bin edges array.

        Returns
        -------
        NDArray
            Array of bin edges
        """
        return self._bin_edges.copy()

    @property
    def bin_centers(self) -> NDArray:
        """
        Get bin centers array.

        Returns
        -------
        NDArray
            Array of bin centers
        """
        return bin_edge_to_bin_center(self.bin_edges)

    @property
    def bin_widths(self) -> NDArray:
        """
        Get bin widths array.

        Returns
        -------
        NDArray
            Array of bin widths
        """
        return np.diff(self.bin_edges)

    @property
    def nbins(self) -> int:
        """
        Get number of bins.

        Returns
        -------
        int
            Number of bins
        """
        return len(self.bin_edges) - 1

    @property
    def bin_range(self) -> Tuple[Any, Any]:
        """
        Get bin range.

        Returns
        -------
        Tuple[Any, Any]
            (minimum edge, maximum edge) with original types preserved
        """
        return (self.bin_edges[0], self.bin_edges[-1])

    def is_uniform(self) -> bool:
        """
        Check if binning is uniform.

        A binning is uniform if all bins have the same width within
        numerical tolerance.

        Returns
        -------
        bool
            True if binning is uniform
        """
        widths = self.bin_widths
        return np.allclose(
            widths,
            widths[0],
            rtol=self.config.rtol,
            atol=self.config.atol
        )

    def is_well_defined(self) -> bool:
        return np.isfinite(self._bin_edges).all()