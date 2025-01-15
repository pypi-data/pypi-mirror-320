import sys

import lmfit
import matplotlib.pyplot as plt
import numpy as np

import brainunit as u

VALID_METHODS = [
    'least_squares', 'differential_evolution', 'brute',
    'basinhopping', 'ampgo', 'nelder', 'lbfgsb', 'powell', 'cg',
    'newton', 'cobyla', 'bfgs', 'tnc', 'trust-ncg', 'trust-exact',
    'trust-krylov', 'trust-constr', 'dogleg', 'slsqp', 'emcee',
    'shgo', 'dual_annealing'
]


def sine_decay(x, amplitude, frequency, decay, offset):
    return offset + amplitude * np.sin(x * frequency) * np.exp(-x / decay)


# assuming we have the following input and output data
np.random.seed(2)
x = np.linspace(0, 20, 201) * u.ms
ydat = sine_decay(x.mantissa, 12.5, 2.0, 4.5, 1.25)
ydat = ydat + np.random.normal(size=len(x), scale=0.40)
ydat = ydat * u.mV

# We are trying to fit the data with the following model
method2 = 'basinhopping'
method2 = 'lbfgsb'
if len(sys.argv) > 1 and sys.argv[1] in VALID_METHODS:
    method2 = sys.argv[1]


# using `assign_units` to assign units to the input and output data
@u.assign_units(xs=u.ms, ys=u.mV, result=(u.mV, u.mV))
def fitting(xs, ys):
    model = lmfit.Model(sine_decay)
    params = model.make_params(
        amplitude={'value': 10, 'min': 0, 'max': 1000},
        frequency={'value': 2.0, 'min': 0, 'max': 6.0},
        decay={'value': 2.0, 'min': 0.001, 'max': 12},
        offset=1.0
    )

    # fit with leastsq
    result0 = model.fit(ys, params, x=xs, method='leastsq')
    print("# Fit using leastsq:")
    print(result0.fit_report())

    # fit with other method
    result = model.fit(ys, params, x=xs, method=method2)
    print(f"\n#####################\n# Fit using {method2}:")
    print(result.fit_report())

    return result0.best_fit, result.best_fit


fit1, fit2 = fitting(x, ydat)

# plot comparison
plt.plot(x, ydat, 'o', label='data')
plt.plot(x, fit1, '+', label='leastsq')
plt.plot(x, fit2, '-', label=method2)
plt.legend()
plt.show()
