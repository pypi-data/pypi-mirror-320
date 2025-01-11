from collections.abc import Sequence
from typing import Any, Literal as L, TypeAlias, overload
from typing_extensions import TypeVar, Unpack, deprecated

import numpy as np
import numpy.typing as npt
import optype as op
import optype.numpy as onp
from scipy._typing import Falsy, Truthy
from ._ufuncs import _KwBase, psi as digamma

__all__ = [
    "ai_zeros",
    "assoc_laguerre",
    "bei_zeros",
    "beip_zeros",
    "ber_zeros",
    "bernoulli",
    "berp_zeros",
    "bi_zeros",
    "clpmn",
    "comb",
    "digamma",
    "diric",
    "erf_zeros",
    "euler",
    "factorial",
    "factorial2",
    "factorialk",
    "fresnel_zeros",
    "fresnelc_zeros",
    "fresnels_zeros",
    "h1vp",
    "h2vp",
    "ivp",
    "jn_zeros",
    "jnjnp_zeros",
    "jnp_zeros",
    "jnyn_zeros",
    "jvp",
    "kei_zeros",
    "keip_zeros",
    "kelvin_zeros",
    "ker_zeros",
    "kerp_zeros",
    "kvp",
    "lmbda",
    "lpmn",
    "lpn",
    "lqmn",
    "lqn",
    "mathieu_even_coef",
    "mathieu_odd_coef",
    "obl_cv_seq",
    "pbdn_seq",
    "pbdv_seq",
    "pbvv_seq",
    "perm",
    "polygamma",
    "pro_cv_seq",
    "riccati_jn",
    "riccati_yn",
    "sinc",
    "softplus",
    "stirling2",
    "y0_zeros",
    "y1_zeros",
    "y1p_zeros",
    "yn_zeros",
    "ynp_zeros",
    "yvp",
    "zeta",
]

###

_T0 = TypeVar("_T0")
_T1 = TypeVar("_T1")

_ArrayT = TypeVar("_ArrayT", bound=onp.ArrayND)

_SCT = TypeVar("_SCT", bound=np.generic)
_SCT_f = TypeVar("_SCT_f", bound=np.floating[Any])
_SCT_fc = TypeVar("_SCT_fc", bound=np.inexact[Any])

_ShapeT = TypeVar("_ShapeT", bound=tuple[int, ...])

_ArrayOrScalar: TypeAlias = _SCT | onp.ArrayND[_SCT]

# ruff: noqa: PYI042
_tuple2: TypeAlias = tuple[_T0, _T0]
_tuple4: TypeAlias = tuple[_T0, _T1, _T1, _T1]
_tuple8: TypeAlias = tuple[_T0, _T1, _T1, _T1, _T1, _T1, _T1, _T1]

_i1: TypeAlias = np.int8
_i2: TypeAlias = np.int16
_i4: TypeAlias = np.int32
_i8: TypeAlias = np.int64
_f2: TypeAlias = np.float16
_f4: TypeAlias = np.float32
_f8: TypeAlias = np.float64
_c8: TypeAlias = np.complex64
_c16: TypeAlias = np.complex128
_i: TypeAlias = _i1 | _i2 | _i4 | _i8
_f: TypeAlias = _f2 | _f4 | _f8 | np.longdouble
_c: TypeAlias = _c8 | _c16 | np.clongdouble

_Extend0: TypeAlias = L["zero"]
_ExtendZ: TypeAlias = L["complex"]
_Extend: TypeAlias = L[_Extend0, _ExtendZ]

###

@overload
def sinc(x: _SCT_fc) -> _SCT_fc: ...
@overload
def sinc(x: float | onp.ToInt) -> np.float64: ...
@overload
def sinc(x: complex) -> np.float64 | np.complex128: ...
@overload
def sinc(x: onp.ToIntND) -> onp.ArrayND[np.float64]: ...
@overload
def sinc(x: onp.ToFloatND) -> onp.ArrayND[np.floating[Any]]: ...
@overload
def sinc(x: onp.ToComplexND) -> onp.ArrayND[np.inexact[Any]]: ...

#
def diric(x: onp.ToFloat | onp.ToFloatND, n: onp.ToInt) -> onp.ArrayND[np.floating[Any]]: ...
def jnjnp_zeros(nt: onp.ToInt) -> _tuple4[onp.Array1D[_f8], onp.Array1D[_i4]]: ...
def jnyn_zeros(n: onp.ToInt, nt: onp.ToInt) -> _tuple4[onp.Array1D[_f8], onp.Array1D[_f8]]: ...
def jn_zeros(n: onp.ToInt, nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def jnp_zeros(n: onp.ToInt, nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def yn_zeros(n: onp.ToInt, nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def ynp_zeros(n: onp.ToInt, nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def y0_zeros(nt: onp.ToInt, complex: op.CanBool = False) -> _tuple2[onp.Array1D[_c16]]: ...
def y1_zeros(nt: onp.ToInt, complex: op.CanBool = False) -> _tuple2[onp.Array1D[_c16]]: ...
def y1p_zeros(nt: onp.ToInt, complex: op.CanBool = False) -> _tuple2[onp.Array1D[_c16]]: ...
def jvp(v: onp.ToFloat | onp.ToFloatND, z: onp.ToComplex, n: onp.ToInt = 1) -> _ArrayOrScalar[_f4 | _f8 | _c8 | _c16]: ...
def yvp(v: onp.ToFloat | onp.ToFloatND, z: onp.ToComplex, n: onp.ToInt = 1) -> _ArrayOrScalar[_f4 | _f8 | _c8 | _c16]: ...
def kvp(v: onp.ToFloat | onp.ToFloatND, z: onp.ToComplex, n: onp.ToInt = 1) -> _ArrayOrScalar[_f4 | _f8 | _c8 | _c16]: ...
def ivp(v: onp.ToFloat | onp.ToFloatND, z: onp.ToComplex, n: onp.ToInt = 1) -> _ArrayOrScalar[_f4 | _f8 | _c8 | _c16]: ...
def h1vp(v: onp.ToFloat | onp.ToFloatND, z: onp.ToComplex, n: onp.ToInt = 1) -> _ArrayOrScalar[_f4 | _f8 | _c8 | _c16]: ...
def h2vp(v: onp.ToFloat | onp.ToFloatND, z: onp.ToComplex, n: onp.ToInt = 1) -> _ArrayOrScalar[_f4 | _f8 | _c8 | _c16]: ...
def riccati_jn(n: onp.ToInt, x: onp.ToFloat) -> _tuple2[onp.Array1D[_f8]]: ...
def riccati_yn(n: onp.ToInt, x: onp.ToFloat) -> _tuple2[onp.Array1D[_f8]]: ...
def erf_zeros(nt: onp.ToInt) -> onp.Array1D[_c16]: ...
def fresnelc_zeros(nt: onp.ToInt) -> onp.Array1D[_c16]: ...
def fresnels_zeros(nt: onp.ToInt) -> onp.Array1D[_c16]: ...
def fresnel_zeros(nt: onp.ToInt) -> onp.Array1D[_c16]: ...
def assoc_laguerre(
    x: onp.ToComplex | onp.ToComplexND,
    n: onp.ToInt,
    k: onp.ToFloat = 0.0,
) -> _ArrayOrScalar[_f4 | _f8 | _c8 | _c16]: ...
def polygamma(n: onp.ToInt | onp.ToIntND, x: onp.ToFloat | onp.ToFloatND) -> _ArrayOrScalar[_f8]: ...
def mathieu_even_coef(m: onp.ToInt, q: onp.ToFloat) -> onp.Array1D[_f8]: ...
def mathieu_odd_coef(m: onp.ToInt, q: onp.ToFloat) -> onp.Array1D[_f8]: ...
def lqmn(m: onp.ToInt, n: onp.ToInt, z: onp.ToFloat | onp.ToFloatND) -> _tuple2[onp.Array2D[_f]] | _tuple2[onp.Array2D[_c]]: ...
def bernoulli(n: onp.ToInt) -> onp.Array1D[_f8]: ...
def euler(n: onp.ToInt) -> onp.Array1D[_f8]: ...
def lqn(n: onp.ToInt, z: onp.ToComplex | onp.ToComplexND) -> _tuple2[onp.Array1D[_f8]] | _tuple2[onp.Array1D[_c16]]: ...
def ai_zeros(nt: onp.ToInt) -> _tuple4[onp.Array1D[_f8], onp.Array1D[_f8]]: ...
def bi_zeros(nt: onp.ToInt) -> _tuple4[onp.Array1D[_f8], onp.Array1D[_f8]]: ...
def lmbda(v: onp.ToFloat, x: onp.ToFloat) -> _tuple2[onp.Array1D[_f8]]: ...
def pbdv_seq(v: onp.ToFloat, x: onp.ToFloat) -> _tuple2[onp.Array1D[_f8]]: ...
def pbvv_seq(v: onp.ToFloat, x: onp.ToFloat) -> _tuple2[onp.Array1D[_f8]]: ...
def pbdn_seq(n: onp.ToInt, z: onp.ToComplex) -> _tuple2[onp.Array1D[_c16]]: ...
def ber_zeros(nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def bei_zeros(nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def ker_zeros(nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def kei_zeros(nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def berp_zeros(nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def beip_zeros(nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def kerp_zeros(nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def keip_zeros(nt: onp.ToInt) -> onp.Array1D[_f8]: ...
def kelvin_zeros(nt: onp.ToInt) -> _tuple8[onp.Array1D[_f8], onp.Array1D[_f8]]: ...
def pro_cv_seq(m: onp.ToInt, n: onp.ToInt, c: onp.ToFloat) -> onp.Array1D[_f8]: ...
def obl_cv_seq(m: onp.ToInt, n: onp.ToInt, c: onp.ToFloat) -> onp.Array1D[_f8]: ...

#
@deprecated(
    "This function is deprecated as of SciPy 1.15.0 and will be removed in SciPy 1.17.0. "
    "Please use `scipy.special.legendre_p_all` instead."
)
def lpn(n: onp.ToInt, z: onp.ToFloat) -> _tuple2[onp.Array1D[_f]] | _tuple2[onp.Array1D[_c]]: ...  # the dtype propagates
@deprecated(
    "This function is deprecated as of SciPy 1.15.0 and will be removed in SciPy 1.17.0. "
    "Please use `scipy.special.assoc_legendre_p_all` instead."
)
def lpmn(m: onp.ToInt, n: onp.ToInt, z: onp.ToFloat | onp.ToFloatND) -> _tuple2[onp.Array2D[_f8]]: ...
@deprecated(
    "This function is deprecated as of SciPy 1.15.0 and will be removed in SciPy 1.17.0. "
    "Please use `scipy.special.assoc_legendre_p_all` instead."
)
def clpmn(m: onp.ToInt, n: onp.ToInt, z: onp.ToComplex | onp.ToComplexND, type: L[2, 3] = 3) -> _tuple2[onp.Array2D[_c16]]: ...

#
@overload
def comb(
    N: onp.ToInt | onp.Array0D[_i],
    k: onp.ToInt | onp.Array0D[_i],
    *,
    exact: Truthy,
    repetition: op.CanBool = False,
) -> int: ...
@overload
def comb(
    N: onp.ToFloat | onp.ToFloatND,
    k: onp.ToFloat | onp.ToFloatND,
    *,
    exact: L[False, 0] = False,
    repetition: op.CanBool = False,
) -> _ArrayOrScalar[_f4 | _f8]: ...

#
@overload
def perm(N: onp.ToInt | onp.Array0D[_i], k: onp.ToInt | onp.Array0D[_i], exact: Truthy) -> int: ...
@overload
def perm(N: onp.ToFloat | onp.ToFloatND, k: onp.ToFloat | onp.ToFloatND, exact: Falsy = False) -> _ArrayOrScalar[_f4 | _f8]: ...

#
@overload
def factorial(n: onp.ToInt, exact: Truthy, extend: _Extend0 = "zero") -> _i: ...
@overload
def factorial(n: onp.ToIntND, exact: Truthy, extend: _Extend0 = "zero") -> onp.ArrayND[np.int_]: ...
@overload
def factorial(n: onp.ToFloat, exact: Falsy = False, extend: _Extend = "zero") -> _f8: ...
@overload
def factorial(n: onp.ToFloatND, exact: Falsy = False, extend: _Extend = "zero") -> onp.ArrayND[_f8]: ...
@overload
def factorial(n: onp.ToComplex, exact: Falsy, extend: _ExtendZ) -> _f8 | _c16: ...
@overload
def factorial(n: onp.ToComplexND, exact: Falsy, extend: _ExtendZ) -> onp.ArrayND[_f8 | _c16]: ...
@overload
def factorial(n: onp.ToComplex, exact: Falsy = False, *, extend: _ExtendZ) -> _f8 | _c16: ...
@overload
def factorial(n: onp.ToComplexND, exact: Falsy = False, *, extend: _ExtendZ) -> onp.ArrayND[_f8 | _c16]: ...

#
@overload
def factorial2(n: onp.ToInt, exact: Truthy, extend: _Extend0 = "zero") -> _i: ...
@overload
def factorial2(n: onp.ToIntND, exact: Truthy, extend: _Extend0 = "zero") -> onp.ArrayND[np.int_]: ...
@overload
def factorial2(n: onp.ToFloat, exact: Falsy = False, extend: _Extend = "zero") -> _f8: ...
@overload
def factorial2(n: onp.ToFloatND, exact: Falsy = False, extend: _Extend = "zero") -> onp.ArrayND[_f8]: ...
@overload
def factorial2(n: onp.ToComplex, exact: Falsy, extend: _ExtendZ) -> _f8 | _c16: ...
@overload
def factorial2(n: onp.ToComplexND, exact: Falsy, extend: _ExtendZ) -> onp.ArrayND[_f8 | _c16]: ...
@overload
def factorial2(n: onp.ToComplex, exact: Falsy = False, *, extend: _ExtendZ) -> _f8 | _c16: ...
@overload
def factorial2(n: onp.ToComplexND, exact: Falsy = False, *, extend: _ExtendZ) -> onp.ArrayND[_f8 | _c16]: ...

#
@overload
def factorialk(n: onp.ToInt, k: onp.ToInt, exact: Truthy, extend: _Extend0 = "zero") -> _i: ...
@overload
def factorialk(n: onp.ToIntND, k: onp.ToInt, exact: Truthy, extend: _Extend0 = "zero") -> onp.ArrayND[np.int_]: ...
@overload
def factorialk(n: onp.ToFloat, k: onp.ToInt, exact: Falsy = False, extend: _Extend = "zero") -> _f8: ...
@overload
def factorialk(n: onp.ToFloatND, k: onp.ToInt, exact: Falsy = False, extend: _Extend = "zero") -> onp.ArrayND[_f8]: ...
@overload
def factorialk(n: onp.ToComplex, k: onp.ToInt, exact: Falsy, extend: _ExtendZ) -> _f8 | _c16: ...
@overload
def factorialk(n: onp.ToComplexND, k: onp.ToInt, exact: Falsy, extend: _ExtendZ) -> onp.ArrayND[_f8 | _c16]: ...
@overload
def factorialk(n: onp.ToComplex, k: onp.ToInt, exact: Falsy = False, *, extend: _ExtendZ) -> _f8 | _c16: ...
@overload
def factorialk(n: onp.ToComplexND, k: onp.ToInt, exact: Falsy = False, *, extend: _ExtendZ) -> onp.ArrayND[_f8 | _c16]: ...

#
@overload
def stirling2(N: onp.ToInt, K: onp.ToInt, *, exact: Truthy) -> int: ...
@overload
def stirling2(N: onp.ToInt, K: onp.ToIntND, *, exact: Truthy) -> onp.ArrayND[np.object_]: ...
@overload
def stirling2(N: onp.ToIntND, K: onp.ToInt | onp.ToIntND, *, exact: Truthy) -> onp.ArrayND[np.object_]: ...
@overload
def stirling2(N: onp.ToInt, K: onp.ToInt, *, exact: Falsy = False) -> _f8: ...
@overload
def stirling2(N: onp.ToInt, K: onp.ToIntND, *, exact: Falsy = False) -> onp.ArrayND[_f8]: ...
@overload
def stirling2(N: onp.ToIntND, K: onp.ToInt | onp.ToIntND, *, exact: Falsy = False) -> onp.ArrayND[_f8]: ...

#
@overload
def zeta(x: onp.ToComplexND, q: onp.ToFloatND | None, out: _ArrayT) -> _ArrayT: ...
@overload
def zeta(x: onp.ToComplexND, q: onp.ToFloatND | None = None, *, out: _ArrayT) -> _ArrayT: ...
@overload
def zeta(x: onp.ToFloat, q: onp.ToFloat | None = None, out: None = None) -> _f8: ...
@overload
def zeta(x: onp.ToFloat, q: onp.ToFloatND, out: None = None) -> onp.ArrayND[_f8]: ...
@overload
def zeta(x: onp.ToFloatND, q: onp.ToFloat | onp.ToFloatND | None = None, out: None = None) -> onp.ArrayND[_f8]: ...
@overload
def zeta(x: onp.ToComplex, q: onp.ToFloat | None = None, out: None = None) -> _f8 | _c16: ...
@overload
def zeta(x: onp.ToComplex, q: onp.ToFloatND, out: None = None) -> onp.ArrayND[_f8 | _c16]: ...
@overload
def zeta(x: onp.ToComplexND, q: onp.ToFloat | onp.ToFloatND | None = None, out: None = None) -> onp.ArrayND[_f8 | _c16]: ...

#
@overload
def softplus(x: onp.ToFloat | onp.ToFloatND, *, out: _ArrayT, dtype: None = None, **kwds: Unpack[_KwBase]) -> _ArrayT: ...
@overload
def softplus(x: float, *, out: None = None, dtype: None = None, **kwds: Unpack[_KwBase]) -> np.float64: ...
@overload
def softplus(x: _SCT_f, *, out: None = None, dtype: None = None, **kwds: Unpack[_KwBase]) -> _SCT_f: ...
@overload
def softplus(x: onp.ToFloat, *, out: None, dtype: npt.DTypeLike | None = None, **kwds: Unpack[_KwBase]) -> np.floating[Any]: ...
@overload
def softplus(x: Sequence[float], *, out: None = None, dtype: None = None, **kwds: Unpack[_KwBase]) -> onp.Array1D[np.float64]: ...
@overload
def softplus(
    x: Sequence[Sequence[float]],
    *,
    out: None = None,
    dtype: None = None,
    **kwds: Unpack[_KwBase],
) -> onp.Array2D[np.float64]: ...
@overload
def softplus(
    x: Sequence[Sequence[Sequence[float]]],
    *,
    out: None = None,
    dtype: None = None,
    **kwds: Unpack[_KwBase],
) -> onp.Array3D[np.float64]: ...
@overload
def softplus(
    x: onp.SequenceND[float],
    *,
    out: None = None,
    dtype: None = None,
    **kwds: Unpack[_KwBase],
) -> onp.ArrayND[np.float64]: ...
@overload
def softplus(
    x: onp.CanArrayND[_SCT_f, _ShapeT],
    *,
    out: None = None,
    dtype: None = None,
    **kwds: Unpack[_KwBase],
) -> onp.ArrayND[_SCT_f, _ShapeT]: ...
@overload
def softplus(
    x: onp.SequenceND[_SCT_f] | onp.SequenceND[onp.CanArrayND[_SCT_f]],
    *,
    out: None = None,
    dtype: None = None,
    **kwds: Unpack[_KwBase],
) -> onp.ArrayND[_SCT_f]: ...
@overload
def softplus(
    x: onp.ToFloatND,
    *,
    out: None = None,
    dtype: type[_SCT_f] | np.dtype[_SCT_f] | onp.HasDType[np.dtype[_SCT_f]],
    **kwds: Unpack[_KwBase],
) -> onp.ArrayND[_SCT_f]: ...
@overload
def softplus(
    x: onp.ToFloatND,
    *,
    out: None,
    dtype: npt.DTypeLike | None = None,
    **kwds: Unpack[_KwBase],
) -> onp.ArrayND[np.floating[Any]]: ...
