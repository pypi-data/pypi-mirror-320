"""
.. autosummary::

    add_frequency_offset
    add_phase_noise
    set_snr    
    
"""

import numpy as np


def set_snr(samples, snr_dB=10, sps=1.0, seed=None):
    """
    Add noise to an array according to a given SNR (in dB).
    
    CAUTION: this function assumes the input signal to be noise free!
    
    If input signal is of type "real" only real noise (with noise power according to 
    SNR) is generated, if signal is of complex type also complex noise (with noise
    power according to SNR/2 in each quadrature) is added.

    Parameters
    ----------
    samples : numpy array, real or complex
        input signal.
    snr_dB : float, optional
        The desired SNR per symbol in dB. The default is 10.
    sps : float, optional
        samples per symbol of the input signal. The default is 1.0
    seed : int, optional
        random seed of the generated noise samples. The default is None.

   
    Returns
    -------
    samples_out : numpy array, real or complex
        output singal with desired SNR (input signal plus random noise samples).

    """
    
    if samples.ndim > 1:
        raise ValueError('number of dimensions of samples should be <= 1')        
        
    snr = 10**(snr_dB/10)
    
    power_samples = np.mean(np.abs(samples)**2, axis=-1)
    power_noise = (power_samples / snr * sps)
    
    rng = np.random.default_rng(seed=seed)
    
    # check, if samples are of complex type to decide if noise should also be complex
    if samples.dtype == complex:
        noise = np.sqrt(power_noise/2) * (rng.standard_normal(size=samples.shape) + 
                                          1j * rng.standard_normal(size=samples.shape))        
    else:
        noise = np.sqrt(power_noise) * rng.standard_normal(size=samples.shape)
        
    samples_out = samples + noise
    
    return samples_out

def add_phase_noise(samples, s_rate=1.0, linewidth=1.0, seed=None):
    """
    Add laser phase noise to complex signal in 1D ndarray 'samples'.
    
    See https://github.com/htw-ikt-noelle/OptischeKommunikationssysteme/blob/master/LaserPhaseNoise.ipynb
    
    TODO:
    expand to two polatizations (or higher dimension signals)!!!

    Parameters
    ----------
    samples : numpy array, complex
        complex signal.
    s_rate : float, optional
        sample rate of the incoming singal. The default is 1.0.
    linewidth : float, optional
        3 dB bandwidth of the generated phase noise in Hz. The default is 1.0.
    seed : int, optional
        seed of the random number generator. The default is None.

    Returns
    -------
    results : dict containing following keys
        samples : numpy array, complex
            complex singal including phase noise.
        phaseAcc : numpy array, real
            phase noise vector in rad.
        varPN : float
            variance of generated phase noise in rad**2.
    """          
    # helper calculations
    dt = 1/s_rate   # [s] sample interval for discrete phase noise model
    varPN = 2*np.pi*linewidth*dt; #[rad²] phase variance increase after time-step dt;   proportional to linewidth and observation time dt [Barry1990]/eq.(112)
    # phase noise (Wiener) processes
    np.random.seed(seed=seed)
    phaseInc = np.sqrt(varPN)*np.random.normal(loc=0,scale=1,size=np.size(samples,0)); # [rad] ensemble of Gaussian i.i.d. phase increments with variance varPN
    phaseAcc = np.cumsum(phaseInc,0); # [rad] accumulated phase = random walks
    phaseAcc = phaseAcc - phaseAcc[0]    # [rad] rotate (shift) all phase processes back to initial zero phase

    samples = samples * np.exp(1j*phaseAcc); 
    
    results = dict()
    results['samples'] = samples
    results['phaseAcc'] = phaseAcc
    results['varPN'] = varPN
    
    return results

def add_frequency_offset(samples, sample_rate=1.0, f_offset = 100e6):
    """
    Add frequency offset to complex signal in 1D ndarray 'samples'.
    
    Parameters
    ----------
    samples : numpy array, complex
        complex signal.
    sample_rate : float, optional
        sample rate of the incoming singal. The default is 1.0.
    f_offset : float, optional
        frequency deviation / frequency offset in Hz. The default is 100 MHz.

    Returns
    -------
    samples : numpy array, complex
        complex singal containing frequency offset.
    """  
    
    #Creating time axis
    t = np.arange(0, np.size(samples)) / sample_rate
    
    #Adding frequency offset   
    samples = samples *  np.exp(1j*2*np.pi*f_offset*t)            
    
    return samples

def rotatePol_pdm(samples_X:np.ndarray, samples_Y:np.ndarray, theta:float=0.0, psi:float=0.0, phi:float=0.0)->dict:
    """
    Applies a polarization rotation (a unitary matrix transformation) in 2-D complex Jones space [1] to
    the input signal, which is given as the two (optical) field components :math:`E_X` (1-D array ``samples_X``) and
    :math:`E_Y` (1-D array ``samples_Y``) of the Jones vector, spanned in Jones space by pair of orthogonal unit 
    vectors :math:`\overrightarrow{e}_X` and :math:`\overrightarrow{e}_Y`, corresponding to the X- and Y-polarization 
    basis vectors, respectively. The matrix relation (on a sample-by-sample basis) is given as follows:
    
    :math:`\overrightarrow{E}_{out}[n] = \mathbf{U} \cdot \overrightarrow{E}_{in}[n]`

    where :math:`\overrightarrow{E}_{out}[n]` and :math:`\overrightarrow{E}_{in}[n]` are :math:`2\\times1` vectors
    (at sample instant :math:`n`) with an X-polarization sample in the first row and a Y-polarization sample in the
    second row, and :math:`\mathbf{U}(\\theta,\psi,\phi)` is a 2⨯2 (unitary) Jones rotation matrix with elements [2]:
    
    
    :math:`\mathbf{U}(\\theta,\psi,\phi) = \\begin{bmatrix}\cos(\\theta)·e^{-j\cdot\psi} & -\sin(\\theta)·e^{j\cdot\phi}\\\ \sin(\\theta)·e^{-j\cdot\phi} & \cos(\\theta)·e^{j\cdot\psi}\end{bmatrix}`

    
    The polarization rotation can be reversed by applying the Hermitian conjugate :math:`\mathbf{U}^{\dagger}` to the
    output signal.

    There are three dedicated parameterizations of the matrix :math:`\mathbf{U}` that lead to elementary polarization
    rotations of the signal Stokes vector around the :math:`S_1`-, :math:`S_2`- and :math:`S_3`-axes in Stokes space
    [2/Table 1], [3], respectively:
    

    :math:`S_1: \mathbf{U}(0,\psi,0)` rotates around the :math:`S_1`-axis by :math:`2\cdot\psi`\n
    :math:`S_2: \mathbf{U}(\\theta,0,\pi/2)` rotates around the :math:`S_2`-axis by :math:`2\cdot\\theta`\n
    :math:`S_3: \mathbf{U}(\\theta,0,0)` rotates around the :math:`S_3`-axis by :math:`2\cdot\\theta`

    Parameters
    ----------
    samples_X:
        Input signal samples in X-polarization. Must be of same size as 'samples_Y'.
    samples_Y:
        Input signal samples in Y-polarization. Must be of same size as 'samples_X'.
    theta:
        Rotational parameter :math:`\\theta` (in rad) for the matrix :math:`\mathbf{U}(\\theta,\psi,\phi)`. Defaults to 0.0.
    psi:
        Rotational parameter :math:`\\psi` (in rad) for the matrix :math:`\mathbf{U}(\\theta,\psi,\phi)`. Defaults to 0.0.
    phi:
        Rotational parameter :math:`\\phi` (in rad) for the matrix :math:`\mathbf{U}(\\theta,\psi,\phi)`. Defaults to 0.0.

    Returns
    -------

    results the containing following keys
        * samples_X : np.ndarray[np.complex128 | np.float64]
            Output signal samples after rotation in X-polarization.
        * samples_Y : np.ndarray[np.complex128 | np.float64]
            Output signal samples after rotation in Y-polarization.
        * U : np.ndarray[np.complex128 | np.float64]
            :math:`2\\times2` Jones (rotation) matrix :math:`\mathbf{U}`, which was applied to the input signal.
        * U_inv : np.ndarray[np.complex128 | np.float64]
            The inverse (Hermitian conjugate) of the Jones (rotation) matrix :math:`\mathbf{U}`.

    References
    -----------
    .. [1] `Jones vector (Wikipedia) <https://en.wikipedia.org/wiki/Jones_calculus#Jones_vector>`_

    .. [2] J.P. Gordon and H. Kogelnik, "PMD fundamentals: polarization mode dispersion in optical fibers",
           Proc. Natl. Acad. Sci. U.S.A., vol. 97, no. 9, pp. 4541-4550, Apr. 2000 `(DOI) <https://www.pnas.org/doi/full/10.1073/pnas.97.9.4541>`_
    
    .. [3] `Stokes parameters (Wikipedia) <https://en.wikipedia.org/wiki/Stokes_parameters>`_

    See Also
    --------
    :meth:`skcomm.rx.stokesEQ_pdm()`
    :meth:`skcomm.utils.jones2stokes_pdm()`
    """
    
    # input argument checks
    if (not isinstance(theta,(float,int))) or (not isinstance(phi,(float,int))) or (not isinstance(psi,(float,int))):
        raise TypeError('theta, phi and psi must be real-valued scalar parameters of type float or int!')

    if (not isinstance(samples_X,np.ndarray)) or (not isinstance(samples_Y,np.ndarray)) or (samples_X.ndim!=1) or (samples_Y.ndim!=1):
        raise TypeError('samples_X and samples_Y must be 1-D Numpy arrays!')

    if samples_X.shape != samples_Y.shape:
        raise ValueError('samples_X and samples_Y must be of same size!')

    # definition of the rotation matrix [2]
    U = np.array(( [np.cos(theta.real)*np.exp(-1j*psi), -np.sin(theta)*np.exp( 1j*phi)],
                   [np.sin(theta.real)*np.exp(-1j*phi),  np.cos(theta)*np.exp( 1j*psi)]))
    
    # matrix multiplication with input Jones vector (sample-by-sample)
    output = U @ np.vstack((samples_X.flatten(),samples_Y.flatten()))

    results = {
    "samples_X": output[0],
    "samples_Y": output[1],
    "U": U,
    "U_inv": np.asarray(np.matrix(U).getH())
    }

    return results