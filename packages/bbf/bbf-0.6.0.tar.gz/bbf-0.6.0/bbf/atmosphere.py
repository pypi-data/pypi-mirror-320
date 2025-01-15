"""Tools to compute atmospheric contribution."""

import importlib.resources

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from pyifu.spectroscopy import Spectrum


def _airmass_refactor(atmspec, stellarlib, airmass):
    """Return transmission function refactoring due to airmass."""
    # Is now broadcastable but very slow :(
    # waveeff = integ(basis, n=1) / integ(basis, n=0)
    return atmspec.get_atm_extinction(
        np.atleast_1d(stellarlib.waveeff)[:, None],
        np.atleast_1d(airmass))


class ExtinctionSpectrum(Spectrum):
    """ converting atmospheric extinction in mags/airmass to
        a scaling factor that is a function of airmass and wavelength.
        An interpolator is stored once for all.
        Takes in a pyifu spectrum object.
    """
    def create(self, *args, kind='cubic', **kwargs):
        Spectrum.create(self, *args, **kwargs)
        self._interpolator = interp1d(self.lbda, self.data, kind=kind)

    def get_atm_extinction(self, lbda, airmass):
        return 10 ** (self._interpolator(lbda) * airmass / 2.5)



def get_airmass_extinction(source="palomar"):
    """Creates a temporary pyifu spectrum object from atmospheric model

    Return
    ------
    ExtinctionSpectrum

    """

    PALOMAR_EXTINCTION = np.asarray([
        (3000, 1.058), (3200, 1.058),
        (3250, 0.911), (3300, 0.826),
        (3350, 0.757), (3390, 0.719),
        (3448, 0.663), (3509, 0.617),
        (3571, 0.575), (3636, 0.537),
        (3704, 0.500), (3862, 0.428),
        (4036, 0.364), (4167, 0.325),
        (4255, 0.302), (4464, 0.256),
        (4566, 0.238), (4785, 0.206),
        (5000, 0.183), (5263, 0.164),
        (5556, 0.151), (5840, 0.140),
        (6055, 0.133), (6435, 0.104),
        (6790, 0.084), (7100, 0.071),
        (7550, 0.061), (7780, 0.055),
        (8090, 0.051), (8370, 0.048),
        (8708, 0.044), (9832, 0.036),
        (10255, 0.034), (10610, 0.032),
        (10795, 0.032), (10870, 0.031),
        (11000, 0.031)])
    #Brodie note - extrapolated 3000-3200 and 10870-11000

    spec = ExtinctionSpectrum(None)
    if source.lower() == "palomar":
        spec.create(
            lbda=PALOMAR_EXTINCTION.T[0],
            data=PALOMAR_EXTINCTION.T[1],
            variance=None,
            header=None)
        spec._source = "Hayes & Latham 1975"

        return spec
    if source.lower() == "buton":
        data_file = importlib.resources.files(__package__) / 'data' / 'Buton_Atmo.dat'
        if not data_file.is_file():
            raise FileNotFoundError(f'file not found: {data_file}')

        df = pd.read_csv(data_file, sep=r'\s+')
        spec.create(
            lbda=df["Wavelength"],
            data=df["Extinction"],
            variance=None,
            header=None)
        spec._source = "Buton et al. 2013"
        return spec

    raise ValueError("Did not provide valid airmass extinction model")
