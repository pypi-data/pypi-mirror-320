"""Gauss--Legendre quadrature rule."""

import numpy as np
import numpy.typing as npt
from quadraturerules.domain import Domain
import typing


def gauss_legendre(
    domain: Domain,
    order: int,
) -> typing.Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Get a Gauss--Legendre quadrature rule."""
    match domain:
        case Domain.Tetrahedron:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.Triangle:
            match order:
                case _:
                    raise ValueError(f"Invalid order: {order}")
        case Domain.Interval:
            match order:
                case 1:
                    return np.array([[0.5, 0.5]]), np.array([1.0])
                case 2:
                    return np.array(
                        [
                            [0.21132486540518708, 0.7886751345948129],
                            [0.7886751345948129, 0.21132486540518708],
                        ]
                    ), np.array([0.5, 0.5])
                case 3:
                    return np.array(
                        [
                            [0.5, 0.5],
                            [0.11270166537925835, 0.8872983346207417],
                            [0.8872983346207417, 0.11270166537925835],
                        ]
                    ), np.array([0.4444444444444444, 0.2777777777777778, 0.2777777777777778])
                case _:
                    raise ValueError(f"Invalid order: {order}")
