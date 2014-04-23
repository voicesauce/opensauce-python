from __future__ import division
__author__ = 'kate'
import numpy as np
import scipy.optimize as scio


def fminsearchbnd(fxn, x0, LB, UB, options=None):
    exitflag, output = 0, 0
    xsize = len(x0)
    x0 = x0[:]
    n = len(x0)
    assert n == len(LB)
    assert n == len(UB)

# "optimset"
    options = {"FunValCheck": "off",
               "MaxFunEvals": 400,
               "MaxIter": 400,
               "OutputFcn": [],
               "TolFun": 1.0*(10**(-7)),
               "TolX": 1.0*(10**(-4)) }

    params = {}
    params["LB"] = LB
    params["UB"] = UB
    params["fxn"] = fxn
    params["n"] = n
    params["OutputFcn"] = []
    params["BoundClass"] = np.zeros(n)

    output = {}

    for i in range(n):
        k = np.isfinite(LB[i]) + 2 * np.isfinite(UB[i])
        params["BoundClass"][i] = k
        if k == 3 and LB[i] == UB[i]:
            params["BoundClass"][i] = 4

    x0u = x0
    k = 1
    for i in range(n):
        switch = params["BoundClass"][i]

        if switch == 1:
            if x0[i] <= LB[i]:
                x0u[k] = 0
            else:
                x0u[k] = np.sqrt(x0[i] - LB[i])
            k += 1

        elif switch == 2:
            if x0[i] >= UB[i]:
                x0u[k] = 0
            else:
                x0u[k] = np.sqrt(UB[i] - x0[i])
            k += 1

        elif switch == 3:
            if x0[i] <= LB[i]:
                x0u[k] = -1 * np.pi / 2
            elif x0[i] >= UB[i]:
                x0u[k] = np.pi / 2
            else:
                x0u[k] = 2 * (x0[i] - LB[i])/(UB[i] - LB[i]) - 1
                x0u[k] = 2 * np.pi + np.arcsin(max(-1, min(1, x0u[k])))
            k += 1

        elif switch == 0:
            x0u[k] = x0[i]
            k += 1

        elif switch == 4:
            pass

        else:
            print "bad switch?"

    if k <= n:
        x0u[k:n] = []

    if len(x0u) == 0:
        x = xtransform(x0u, params)
        x = np.reshape(x, xsize)
        fval = feval(params["fxn"], x, params.keys()[:])
        exitflag = 0
        output["iterations"] = 0
        output["funcount"] = 1
        output["algorithm"] = "fminsearch"
        output["message"] = "all variables were held fixed"

    if options.has_key("OutputFcn"):
        print "should be unreachable??"

    # options = {"FunValCheck": "off",
    #            "MaxFunEvals": 400,
    #            "MaxIter": 400,
    #            "OutputFcn": [],
    #            "TolFun": 1.0*(10**(-7)),
    #            "TolX": 1.0*(10**(-4)) }

    xtol = options["TolX"]
    ftol = options["TolFun"]
    maxiter = options["Maxiter"]
    (xu, fval, iters, funcalls, warnflag, allvecs) = scio.fminsearch(intrafun, x0u, xtol=xtol, ftol=ftol, maxiter=maxiter)
    x = xtransform(xu, params)
    x = np.reshape(x, xsize)

    # TODO outfun_wrapper






def feval(funcName, *args):
    return eval(funcName)(*args)

def intrafun(x, params):
    xtrans = xtransform(x, params)
    fval = feval(params["fxn"], xtrans, params.keys()[:])

def xtransform(x, params):
    xtrans = np.zeros((1, params["n"]))
    k = 1
    for i in range(params["n"]):
        switch = params["BoundClass"]
        if switch == 1:
            k += 1
        elif switch == 2:
            k += 1
        elif switch == 3:
            xtrans[i] = np.sin(x[k]+1)/2
            xtrans[i] = xtrans[i] * (params["UB"][i] - params["LB"][i]) + params["LB"][i]
            xtrans[i] = max(params["LB"][i], min(params["UB"][i], xtrans[i]))
            k += 1
        elif switch == 4:
            k += 1
        else:
            k += 1





# def xtransform(x, params):
#     xtrans = np.zeros((1, params["n"]))








