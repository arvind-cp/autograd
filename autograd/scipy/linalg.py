from __future__ import division
import scipy.linalg

import autograd.numpy as anp
from autograd.numpy.numpy_wrapper import wrap_namespace
from autograd.extend import defvjp, defjvp

wrap_namespace(scipy.linalg.__dict__, globals())  # populates module namespace

def _vjp_sqrtm(ans, A, disp=True, blocksize=64):
    assert disp, "sqrtm vjp not implemented for disp=False"
    ans_transp = anp.transpose(ans)
    def vjp(g):
        return solve_sylvester(ans_transp, ans_transp, g)
    return vjp
defvjp(sqrtm, _vjp_sqrtm)

def _flip(a, trans):
    if anp.iscomplexobj(a):
        return 'H' if trans in ('N', 0) else 'N'
    else:
        return 'T' if trans in ('N', 0) else 'N'

def grad_solve_triangular(ans, a, b, trans=0, lower=False, **kwargs):
    tri = anp.tril if (lower ^ (_flip(a, trans) == 'N')) else anp.triu
    transpose = lambda x: x if _flip(a, trans) != 'N' else x.T
    al2d = lambda x: x if x.ndim > 1 else x[...,None]
    def vjp(g):
        v = al2d(solve_triangular(a, g, trans=_flip(a, trans), lower=lower))
        return -transpose(tri(anp.dot(v, al2d(ans).T)))
    return vjp

defvjp(solve_triangular,
       grad_solve_triangular,
       lambda ans, a, b, trans=0, lower=False, **kwargs:
       lambda g: solve_triangular(a, g, trans=_flip(a, trans), lower=lower))

def _jvp_sqrtm(dA, ans, A, disp=True, blocksize=64):
    assert disp, "sqrtm jvp not implemented for disp=False"
    return solve_sylvester(ans, ans, dA)
defjvp(sqrtm, _jvp_sqrtm)
