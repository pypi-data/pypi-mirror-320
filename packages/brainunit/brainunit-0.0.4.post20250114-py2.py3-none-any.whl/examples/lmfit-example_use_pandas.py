"""
Fit with Data in a pandas DataFrame
===================================

Simple example demonstrating how to read in the data using ``pandas`` and
supply the elements of the ``DataFrame`` to lmfit.

"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lmfit.models import LorentzianModel

import brainunit as u

###############################################################################
# We have the following data
# read the data into a pandas DataFrame, and use the ``x`` and ``y`` columns:
dframe = pd.read_csv('peak.csv')
xs = np.asarray(dframe['x']) * u.ms
ys = np.asarray(dframe['y']) * u.mV


@u.assign_units(xs=u.ms, ys=u.mV)
def fitting(xs, ys):
    model = LorentzianModel()
    params = model.guess(ys, x=xs)
    result = model.fit(ys, params, x=xs)
    return result


result = fitting(xs, ys)

###############################################################################
# and gives the fitting results:
print(result.fit_report())

###############################################################################
# and plot below:
result.plot_fit()
plt.show()
