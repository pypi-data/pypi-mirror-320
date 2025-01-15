"""Quadrature rules."""

from enum import Enum as _Enum
import typing as _typing
import numpy.typing as _npt
import numpy as _np

from quadraturerules import rules
from quadraturerules.domain import Domain


class QuadratureRule(_Enum):
    """A quadrature rule family."""

    GaussLegendre = 1
    XiaoGimbutas = 2


def single_integral_quadrature(
    rtype: QuadratureRule,
    domain: Domain,
    order: int,
) -> _typing.Tuple[_npt.NDArray[_np.float64], _npt.NDArray[_np.float64]]:
    """Get a quadrature rule for a single integral."""
    match rtype:
        case QuadratureRule.GaussLegendre:
            return rules.gauss_legendre(domain, order)
        case QuadratureRule.XiaoGimbutas:
            return rules.xiao_gimbutas(domain, order)
        case _:
            raise ValueError(f"Unsupported rule for single integral: {rtype}")
