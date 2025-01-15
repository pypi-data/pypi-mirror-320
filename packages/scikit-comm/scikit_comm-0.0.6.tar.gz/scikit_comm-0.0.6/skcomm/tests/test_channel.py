import unittest

import numpy as np
from numpy.testing import (
        assert_, assert_raises, assert_equal, assert_warns, assert_allclose,
        assert_no_warnings, assert_array_equal, assert_array_almost_equal,
        suppress_warnings
        )

from .. import channel

class TestSetSNR(unittest.TestCase):
    """
    Test class for set_snr
    """
    
    def test_high_snr(self):
        sig_in = np.array([1, 1, 1, 1])
        sig_out = channel.set_snr(sig_in, snr_dB=100)
        assert_array_almost_equal(sig_in, sig_out, decimal=2)
        
class TestAddPhaseNoise(unittest.TestCase):
    """
    Test class for add_phase_noise
    """
    
    def test_low_pn(self):
        sig_in = np.array([1+0.j, 1+0.j, 1+0.j, 1+0.j])
        sig_out = channel.add_phase_noise(sig_in, linewidth=0.0)['samples']
        assert_array_equal(sig_in, sig_out)
        
    def test_no_amp_change(self):
        sig_in = np.array([1+0.j, 1+0.j, 1+0.j, 1+0.j])
        sig_out = channel.add_phase_noise(sig_in, linewidth=1.0)['samples']
        assert_array_almost_equal(np.abs(sig_in), np.abs(sig_out), decimal=10)

class TestRotatePol(unittest.TestCase):
    """
    Test class for channel.rotatePol_pdm():
        test correct polarization rotations of (Jones space) pol-mux samples
    """
    def test_rotatePol_pdm(self):
        # create some test samples in X- and Y-polarization in 6 distinct SOPs
        samples_X = np.asarray([1+1j, 0+0j, 1+1j, 1+1j, 1+1j, 1+1j])
        samples_Y = np.asarray([0+0j, 1+1j, 1+1j,-1-1j,-1+1j, 1-1j])
        
        sq2 = np.sqrt(2)

        # no pol. rotation
        THETA = 0.0;  PSI = 0.0; PHI = 0.0
        result = channel.rotatePol_pdm(samples_X, samples_Y, theta=THETA, psi=PSI, phi=PHI)
        assert_allclose(result["samples_X"], np.asarray([1+1j, 0+0j, 1+1j, 1+1j, 1+1j, 1+1j]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["samples_Y"], np.asarray([0+0j, 1+1j, 1+1j,-1-1j,-1+1j, 1-1j]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["U"],     np.asarray([[1+0j, 0+0j], [0+0j, 1+0j]]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["U_inv"], np.asarray([[1+0j, 0+0j], [0+0j, 1+0j]]), rtol=1e-15, atol=1e-15)

        # pol. rotation around S1-axis by +pi/2
        THETA = 0.0;  PSI = np.pi/2 /2; PHI = 0.0
        result = channel.rotatePol_pdm(samples_X, samples_Y, theta=THETA, psi=PSI, phi=PHI)
        assert_allclose(result["samples_X"]/sq2, np.asarray([1+0j, 0+0j, 1+0j, 1+0j, 1+0j, 1+0j]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["samples_Y"]/sq2, np.asarray([0+0j, 0+1j, 0+1j, 0-1j,-1+0j, 1+0j]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["U"]*sq2,     np.asarray([[1-1j, 0+0j], [0+0j, 1+1j]]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["U_inv"]*sq2, np.asarray([[1+1j, 0+0j], [0+0j, 1-1j]]), rtol=1e-15, atol=1e-15)

        # pol. rotation around S2-axis by +pi/2
        THETA = np.pi/2 /2;  PSI = 0.0; PHI = np.pi/2
        result = channel.rotatePol_pdm(samples_X, samples_Y, theta=THETA, psi=PSI, phi=PHI)
        assert_allclose(result["samples_X"]*sq2, np.asarray([1+1j, 1-1j, 2+0j, 0+2j, 2+2j, 0+0j]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["samples_Y"]*sq2, np.asarray([1-1j, 1+1j, 2+0j, 0-2j, 0+0j, 2-2j]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["U"]*sq2,     np.asarray([[1+0j, 0-1j], [0-1j, 1+0j]]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["U_inv"]*sq2, np.asarray([[1+0j, 0+1j], [0+1j, 1+0j]]), rtol=1e-15, atol=1e-15)

        # pol. rotation around S3-axis by +pi/2
        THETA = np.pi/2 /2 + 2*np.pi;  PSI = 0.0; PHI = 0.0
        result = channel.rotatePol_pdm(samples_X, samples_Y, theta=THETA, psi=PSI, phi=PHI)
        assert_allclose(result["samples_X"]*sq2, np.asarray([1+1j,-1-1j, 0+0j, 2+2j, 2+0j, 0+2j]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["samples_Y"]*sq2, np.asarray([1+1j, 1+1j, 2+2j, 0+0j, 0+2j, 2+0j]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["U"]*sq2,     np.asarray([[1+0j,-1+0j], [ 1+0j, 1+0j]]), rtol=1e-15, atol=1e-15)
        assert_allclose(result["U_inv"]*sq2, np.asarray([[1+0j, 1+0j], [-1-0j, 1+0j]]), rtol=1e-15, atol=1e-15)
