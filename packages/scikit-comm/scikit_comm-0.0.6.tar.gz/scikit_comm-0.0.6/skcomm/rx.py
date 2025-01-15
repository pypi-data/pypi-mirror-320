""" 
.. autosummary::

    blind_adaptive_equalizer
    carrier_phase_estimation_VV
    carrier_phase_estimation_bps
    combining
    count_errors
    decision
    demapper
    deskew
    frequency_offset_correction
    sampling_clock_adjustment
    sampling_phase_adjustment
    symbol_sequence_sync

"""

import warnings

import numpy as np
import scipy.signal as ssignal
from scipy import interpolate
import matplotlib.pyplot as plt

from . import utils
from . import filters
from . import signal
from . import channel
try:
    from .cython_mods import rx_cython
    cython_available = True
except ImportError:
    cython_available = False

def demapper(samples, constellation):
    """    
    Demap samples to bits using a given constellation alphabet.

    samples are compared to a given constellation alphabet and the index
    of the corresponding constellation (integer) is
    converted to the corresponding bit value.   
    
    The resulting bit sequence is therefore of length: 
    np.log2(constellation.size)*samples.size.

    Parameters
    ----------
    samples : 1D numpy array, real or complex
        sampled input signal.
    constellation : 1D numpy array, real or complex
        possible constellation points of the input signal.    

    Returns
    -------
    bits : 1D numpy array, bool
        converted bit sequence.

    """
    samples = np.asarray(samples)
    constellation = np.asarray(constellation)

    if constellation.ndim > 1:
        raise ValueError('number of dimensions of constellation must not exceed 1!')

    if samples.ndim > 1:
        raise ValueError('number of dimensions of samples must not exceed 1!')

    decimals = np.full_like(samples.real, np.nan)
    bps = int(np.log2(constellation.size))    
    
    for const_idx, const_point in enumerate(constellation):
        decimals[samples == const_point] = const_idx
    
    # convert constellation index (decimal) to bits
    bits = utils.dec_to_bits(decimals, bps)        
  
    return bits

def decision(samples, constellation, norm=True):
    """
    Decide samples to a given constellation alphabet.

    Find for every sample the closest constellation point in a
    constellations array and return this value.    

    Parameters
    ----------
    samples : 1D numpy array, real or complex
        sampled input signal.
    constellation : 1D numpy array, real or complex
        possible constellation points of the input signal.
    norm : bool
        should the samples be normalized (to mean maginitude of constellation)
        before decision?        

    Returns
    -------
    dec_symbols : 1D numpy array, real or complex
        clostest constellation point for every input sample.

    """    
    if constellation.ndim > 1:
        raise ValueError('number of dimensions of constellation must not exceed 1!')

    # if samples.ndim > 2:
    #     raise ValueError('number of dimensions of samples should be <= 2')
    if samples.ndim > 1:
        raise ValueError('number of dimensions of samples must not exceed 1!')        
    
    if norm:
        # normalize samples to mean magnitude of original constellation
        mag_const = np.mean(abs(constellation))
        # mag_samples = np.mean(abs(samples), axis=-1).reshape(-1,1)
        mag_samples = np.mean(abs(samples))
        samples_norm = samples * mag_const / mag_samples
    else:
        samples_norm = samples

    idx = np.argmin(np.abs(samples_norm - constellation.reshape(-1,1)), axis=0)
    dec_symbols = constellation[idx]
    return dec_symbols

def count_errors(bits_tx, bits_rx):
    """
    Count bit errors.
    
    Count the bit error rate (BER) by comparing two bit sequences. Additionally
    also the position of the bit errors is returned as a bool array of size
    bits_tx.size, where True indicates a bit error.
    
    If the bit sequence bits_rx is longer than the sent sequency, the sent sequence
    is repeated in order to match both lengths.
     

    Parameters
    ----------
    bits_tx : 1D numpy array, bool
        first bits sequence.
    bits_rx : 1D numpy array, bool
        first bits sequence.


    Returns
    -------
    results : dict containing following keys
        ber : float
            bit error rate (BER)
        err_idx : 1D numpy array, bool
            array indicating the bit error positions as True.

    """
    if (bits_rx.ndim > 1) | (bits_tx.ndim > 1):
        raise ValueError('number of dimensions of bits must not exceed 1!')
        
    if bits_tx.size > bits_rx.size:
        raise ValueError('number of bits transmitted must not exceed number of received bits!')
    
    # if bit sequences are of unequal length, repeat bits_tx accordingly
    if bits_tx.size < bits_rx.size:
        ratio_base = bits_rx.size // bits_tx.size
        ratio_rem = bits_rx.size % bits_tx.size        
        bits_tx = np.concatenate((np.tile(bits_tx, ratio_base), bits_tx[:ratio_rem]), axis=0)
    
    # count errors
    err_idx = np.not_equal(bits_tx, bits_rx)
    ber = np.sum(err_idx) / bits_tx.size
    
    # generate output dict
    results = dict()
    results['ber'] = ber
    results['err_idx'] = err_idx
    return results

def sampling_phase_adjustment(samples:np.ndarray, sample_rate:float=1.0, symbol_rate:float=2.0, shift_dir:str='both',delay:float=0.0, compensate:bool=True)->dict:
    """
    Estimate the sampling phase offset and compensate for it.
    
    The sampling phase offset is estimated by finding the phase of the oszillation
    with the frequency of the symbol rate in the signal abs(samples)**2. This offset
    is compensated for by a temporal cyclic shift of the input signal.
    
    To contain this frequency component, the signal has to be sampled at least 
    with a rate of three times the symbol rate. If the input signal is sampled
    with lower frequency, the signal is temporally upsampled.    

    Parameters
    ----------
    samples : 1D numpy array, real or complex
        input signal.        
    sample_rate : float, optional
        sample rate of input signal in Hz. The default is 1.0.
    symbol_rate : float, optional
        symbol rate of input signal in Hz. The default is 2.0.
    shift_dir : string, optional
        defines the bahaviour of the compensation of the found temporal shift. Can be 
        either 'delay', 'advance' or 'both'. 
        'delay' / 'advance' will only compensate for the time shift by exclusively 
        shifting the signal to the right / left. This means that the time shift 
        can be in the range between [-1/symbol_rate, 0] or [0, 1/symbol_rate], respectively. 
        The option 'both' will shift the signal either to the left or to the 
        right, depending on the minimum amount of time shift. The time shift will 
        therefore be in the range between [-0.5/symbol_rate, 0.5/symbol_rate].
    delay : float, optional
        additional delay in seconds to apply on the signal after timing compensation. The dafault value is 0.0
    compensate : bool, optional
        should the sampling skew compensation and additional delay be applied? The default is True.

    Returns
    -------
    results : dict containing following keys
        samples_out : 1D numpy array, real or complex
            cyclic shifted output signal.
        est_shift : float
            estimated (and inversely applied) temporal shift.

    """    
    # do all dsp on a copy of the samples
    samples_tmp = samples
    # sample rate of dsp (must be at least 3 time symbol rate)
    sr_dsp = sample_rate
    
    # if signal has less than three samples per symbol --> oszillation with
    # symbol rate not present in spectrum of abs(signal)
    if sample_rate < (3 * symbol_rate):
        # upsample to 3 samples per symol
        sr_dsp = symbol_rate * 3
        # watch out, that this is really an integer
        len_dsp = sr_dsp / sample_rate * np.size(samples_tmp, axis=0)
        if len_dsp % 1:
            #hotfix 
            for i in range(np.size(samples_tmp, axis=0)):
                samples_tmp = samples_tmp[:-1]
                len_dsp = sr_dsp / sample_rate * np.size(samples_tmp, axis=0)
                if len_dsp % 1:
                    #raise ValueError('DSP samplerate results in asynchronous sampling of the data symbols')
                    pass
                else:
                    break

        samples_tmp = ssignal.resample(samples_tmp, num=int(len_dsp), window=None)
    
    # calc length of vector so that spectrum exactly includes the symbol rate
    tmp = np.floor(symbol_rate * np.size(samples_tmp, axis=0) / sr_dsp)
    n_sam = int(tmp / symbol_rate * sr_dsp)
    
    
    # cut vector to size and take amplitude square
    samples_tmp = np.abs(samples_tmp[:n_sam])**2
    
    # calc phase of frequency component with frequency equal to the symbol rate
    t_tmp = np.arange(n_sam) / sr_dsp
    est_phase = np.angle(np.sum(samples_tmp * np.exp(1j * 2 * np.pi * symbol_rate * t_tmp)))
    
    # ensure to only advance the signal (shift to the left)
    if (shift_dir == 'advance') and (est_phase < 0.0):
        est_phase += 2 * np.pi        
    
    # ensture to only delay the singal (shift to the right)
    if (shift_dir == 'delay') and (est_phase > 0.0):
        est_phase -= 2 * np.pi        
    
    est_shift = est_phase / 2 / np.pi / symbol_rate
    
    # # for debugging purpose
    # sps = int(sample_rate / symbol_rate)
    # visualizer.plot_eye(samples, sample_rate=sample_rate, bit_rate=symbol_rate)
    # plt.plot(np.abs(samples[:10*sps]), 'C0')
    
    if compensate==True:
        # compensate for found sample phase offset
        samples = filters.time_shift(samples, sample_rate, -est_shift + delay)
    
    # # for debugging purpose
    # visualizer.plot_eye(samples, sample_rate=sample_rate, bit_rate=symbol_rate)
    # plt.plot(np.abs(samples[:10*sps]), 'C1')
    
    # generate results dict
    results = dict()
    results['samples_out'] = samples
    results['est_shift'] = est_shift
    
    return results

def sampling_clock_adjustment(samples, sample_rate=1.0, symbol_rate=2.0, block_size=500):
    """
    Estimate sampling frequency offset and correct for it.
    
    This function estimates the sampling frequency offset between nominal (given) 
    and actual (sample rate of samples) sampling frequency and corrects for the
    found value.
    This is done by splitting the singal into blocks of block_size SYMBOLS and 
    estimating the sampling time offset for each of the blocks (see skcomm.rx.sampling_phase_adjustment).
    Then, the sampling time offest is corrected for by cyclic time shift of the individual blocks.
    Longer block sizes enhance the accuracy of the time offset estimatin, but cause the sampling
    clock offset to be larger within one block.
    CAUTION: method will fail for large sampling clock (frequency) offsets and if the sampling frequency
    offset leads to a timing error larger than +- 1/symbol_rate over the whole samples.
    

    Parameters
    ----------
    samples : 1D numpy array, real or complex
        input signal.        
    sample_rate : float, optional
        sample rate of input signal in Hz. The default is 1.0.
    symbol_rate : float, optional
        symbol rate of input signal in Hz. The default is 2.0.
    block_size : int, optional
        signal is split into blocks of block_size SYMBOLS. The default is 500.

    Returns
    -------
    results : dict containing following keys
        samples_out : 1D numpy array, real or complex
            output signal.
        est_shift : float or 1D numpy array of floats
            estimated (and inversely applied) temporal shift per block.

    """
    
    # if only one block is questioned -> do only time shift
    if block_size == -1:
        results = sampling_phase_adjustment(samples, sample_rate=sample_rate,
                                                         symbol_rate=symbol_rate, 
                                                         shift_dir='both')
        return results
    # otherwise, do time shift for every block
    else:
        n_samples = np.size(samples, axis=0)    
        sps = int(sample_rate / symbol_rate)
        s_per_block = block_size * sps    
        
        # cut signal, to an integer number of blocks and create array
        n_samples_new = int(np.floor(n_samples / s_per_block) * s_per_block)
        samples_array = np.reshape(samples[:n_samples_new], (-1, s_per_block))
        
        tmp = list()
        # run sampling_phase_adjustment once per block
        for idx, block in enumerate(samples_array):
            tmp.append(sampling_phase_adjustment(block, sample_rate=sample_rate,
                                                             symbol_rate=symbol_rate, 
                                                             shift_dir='both'))
            
        # Warning in case samples have to be dropped due to non-ideal block size
        if n_samples_new < n_samples:
            warnings.warn('Due to n_samples not being a multiple of the samples_per_block, {}  samples had to be dropped!'.format((n_samples - n_samples_new)))

            
    # generate output dict containing samples and estimated time shifts per block
    results = dict()
    results['samples_out'] = np.asarray([block['samples_out'] for block in tmp]).reshape(-1)
    results['est_shift'] = np.asarray([block['est_shift'] for block in tmp])
    return results



    ########### MULTIPLE, DIFFERENT METHODS TO COMPENSATE SAMPLING CLOCK OFFSETS (have to be tested) ######################
    """
    These could be used instead of the above implemented method (within the "else" branch)
    
    METHOD 1: "sample dropping", prabably better for real time implementation, but not better in first tests
    
        n_blocks = np.size(samples_array, axis=0)        
        correction  = 0
        tmp = list()
        # run sampling_phase_adjustment multiple times
        for block in np.arange(n_blocks):
            # shift estimation, "dry run"
            samples_tmp = samples[block*s_per_block + correction:block*s_per_block + s_per_block + correction]
            tmp = sampling_phase_adjustment(samples_tmp, sample_rate=sample_rate, symbol_rate=symbol_rate, shift_dir='advance')
            # "sample dropping"
            correction += int(tmp['est_shift']//(1/sample_rate))
            # actual phase adjustemnt
            samples_block = samples[block*s_per_block + correction:block*s_per_block + s_per_block + correction]
            tmp.append(sampling_phase_adjustment(samples_block, sample_rate=sample_rate, symbol_rate=symbol_rate, shift_dir='advance'))
            
            
    METHOD 2: estimate slope of sampling clock offset over blocks and do resampling (only works in case of almost constant sampling frequency missmatch)
        
        tmp = list()
        # run sampling_phase_adjustment multiple times, once for every block
        for idx, block in enumerate(samples_array):
            tmp.append(sampling_phase_adjustment(block, sample_rate=sample_rate, symbol_rate=symbol_rate, shift_dir='both'))
            # print(results[-1]['est_shift'])
        # generate shifts as ndarrays    
        shifts = np.asarray([block['est_shift'] for block in tmp])
        # do unwrap of shifts (has to be converted in rad???), and shifts have to be fftshifted, because of current filter implementation...can be changed in the future???
        shifts = np.unwrap(np.fft.fftshift(shifts) / (0.5/symbol_rate) * 2 * np.pi) * (0.5/symbol_rate) / 2 / np.pi
        # estimate mean sample time offset per block
        sample_time_offset = np.mean(np.diff(shifts))
        
        t_block = s_per_block / sample_rate
        # ratio between nominal and actual sampling frequency
        ratio = t_block / (t_block + sample_time_offset)
        
        t_old = np.arange(n_samples) / sample_rate
        # interpolate signal at different timing / sampling instants, but keep start and end time the same
        n_samples_new = int(np.round(ratio * n_samples))
        t_new = np.linspace(start=t_old[0], stop=t_old[-1], num=n_samples_new, endpoint=True)        
        f = sinterp.interp1d(t_old, samples, kind='cubic')
        samples = f(t_new)
        
        # do clock phase adjumstemnt once after resampling        
        results = sampling_phase_adjustment(samples, sample_rate=sample_rate, symbol_rate=symbol_rate, shift_dir='both')
    """
    #####################################################################################

def deskew(samples_1:np.ndarray[np.complex128 | np.float64], samples_2:np.ndarray[np.complex128 | np.float64], sample_rate:float=1.0, symbol_rate:float=2.0, cm_delay:float=0.0, compensate:bool=True)->dict:
    """
    Finds the skew between two signals (and compensates for it).

    The delay (sampling phase offset) to the ideal sampling instant within the range of [0, 1/symbol_rate] is found
    for each of the signals. For more information see :meth:`skcomm.rx.sampling_phase_adjustment()`.

    The found delay can be compensated for for each signal individually, and therefore performing a deskewing.

    Parameters
    ---------- 
    samples_1: 
        input signal 1.
    samples_2: 
        input signal 2.        
    sample_rate: 
        sample rate of input signals in Hz. 
    symbol_rate:
        symbol rate of input signals in Hz.
    cm_delay: 
        common delay in seconds to apply on both signals after skew compensation.
    compensate: 
        should skew compensation and cm_delay be applied?
    
    Returns
    ------- 
    
    results with following keys
        * 'samples_out_1' : np.ndarray[np.complex128 | np.float64] 
            output signal 1, if parameter compensate==False, the output signal 1 is equal to the input singal 1.
        * 'samples_out_2'  : np.ndarray[np.complex128 | np.float64] 
            output signal 2, if parameter compensate==False, the output signal 2 is equal to the input singal 2.
        * 'est_shift_1' : float 
            estimated (and inversely applied) temporal shift in seconds for signal 1.
        * 'est_shift_2' : float 
            estimated (and inversely applied) temporal shift in seconds for signal 2.
    
    See Also
    --------
    :meth:`skcomm.rx.sampling_phase_adjustment()`
    :meth:`skcomm.filters.time_shift()`


    """

    result_1 = sampling_phase_adjustment(samples_1, sample_rate=sample_rate, symbol_rate=symbol_rate, shift_dir='both', compensate=False)
    
    samples_2 = filters.time_shift(samples_2, sample_rate=sample_rate, tau = -result_1['est_shift'])
    result_2 = sampling_phase_adjustment(samples_2, sample_rate=sample_rate, symbol_rate=symbol_rate, shift_dir='both', compensate=False)
    
    if compensate:
        samples_1 = filters.time_shift(samples_1,sample_rate=sample_rate,tau=-result_1['est_shift'] + cm_delay) 
        samples_2 = filters.time_shift(samples_2,sample_rate=sample_rate,tau=-result_2['est_shift'] + cm_delay)

    result_2['est_shift'] = result_2['est_shift'] + result_1['est_shift']
    print(f"estimated shift 1: {result_1['est_shift']*symbol_rate:.2f} UI, esimated shift 2: {result_2['est_shift']*symbol_rate:.2f} UI, estimated skew (1-2): {(result_1['est_shift']-result_2['est_shift'])*symbol_rate:.2f} UI")

    results = dict()
    results['samples_out_1'] = samples_1
    results['samples_out_2'] = samples_2
    results['est_shift_1'] = result_1['est_shift']
    results['est_shift_2'] = result_2['est_shift']
    return results

def carrier_phase_estimation_VV(symbols, n_taps=31, filter_shape='wiener', mth_power=4, mag_exp=0, rho=0.1):
    """
    Viterbi-Viterbi carrier phase estimation and recovery.
    
    This function estimates the phase noise of the carrier using the Viterbi-Viterbi
    method [1]. Either a rectangular or a Wiener filter shape can be applied for
    phase averaging.    
    

    Parameters
    ----------
    symbols :  1D numpy array, real or complex
        input symbols.  
    n_taps : int, optional
        Number of taps of the averaging filter. Must be an odd number.
        The default is n_taps = 31.
    filter_shape : string, optional
        Specifies the averaging filter shape (window function): either 'rect', 
        'wiener', 'hyperbolic' or 'lorentz'.
        The default is filter_shape = 'wiener'.
    mth_power:  int, optional
        Specifies the power to which the symbols are raised to remove the data 
        modulation (i.e., the number of equidistant modulation phase states).
        The default is mth_power = 4 (corresponding to QPSK).
    mag_exp : optional
        Specifies the exponent, to which the symbol magnitudes are raised before 
        averaging the phasors. A value > 0 leads to the preference of the outer 
        symbols in the averaging process, while a value <0 accordingly leads to 
        a preference of inner symbols. 
        For mag_exp = 0, the symbol magnitudes are ignored in the phase estimation
        process (For more information see [1]).
        The default value is mag_exp = 0.
    rho : float, optional, rho>0
        Shape parameter for 'wiener', 'hyperbolic' and 'lorentz' filter. 
        For larger rho, the filter shape becomes narrower.
        For 'wiener' filter shape,  rho is the ratio between the magnitude of
        the frequency noise variance σ²_ϕ and the (normalized) AWGN variance σ²_n' 
        (for more information see [2],[3]). σ²_ϕ is related to the laser 
        linewidth LW as σ²_ϕ = 2*π*LW/symbol_rate.
        For 'hyperbolic' and 'lorentz' filter shape (aka Cauchy or Abel window), 
        1/rho is the FWHM parameter of the filter shape.
        The default is rho = 0.1.

    Returns
    -------
     results : dict containing following keys
        rec_symbols : 1D numpy array, real or complex
            recovered symbols.
        phi_est : 1D numpy array, real
            estimated phase noise random walk
        cpe_window: 1D numpy array, real
            applied CPE slicing-average window ()
    
    References
    ----------
    [1] A. Viterbi, "Nonlinear estimation of PSK-modulated carrier phase with 
    application to burst digital transmission," in IEEE Transactions on 
    Information Theory, vol. 29, no. 4, pp. 543-551, July 1983, doi: 10.1109/TIT.1983.1056713.
    
    [2] Ezra Ip, Alan Pak Tao Lau, Daniel J. F. Barros, and Joseph M. Kahn, 
    "Coherent detection in optical fiber systems," Opt. Express 16, 753-791 (2008)
    
    [3] E. Ip and J. M. Kahn, "Feedforward Carrier Recovery for Coherent 
    Optical Communications," in Journal of Lightwave Technology, vol. 25, 
    no. 9, pp. 2675-2692, Sept. 2007, doi: 10.1109/JLT.2007.902118.
    
    [4]  Wolfram Language & System Documentation Center, 
    https://reference.wolfram.com/language/ref/CauchyDistribution.html,
    https://en.wikipedia.org/wiki/Cauchy_distribution
    """    
    # TODO: change input argument 'symbols' to class Signal()
    
    # input sanitization (using only real value of first element)
    n_taps = np.real(np.atleast_1d(n_taps)[0])
    filter_shape = np.atleast_1d(filter_shape )[0]
    mth_power = np.real(np.atleast_1d(mth_power)[0])
    mag_exp = np.real(np.atleast_1d(mag_exp)[0])
    rho = np.real(np.atleast_1d(rho)[0])
        
    if n_taps < 1  or n_taps%1 != 0  or  n_taps%2==0:
        raise ValueError('The number of CPE taps n_taps must be an odd integer ≥1.')
    
    if symbols.size <= 4*n_taps:
        raise ValueError('The number of symbols must exceed 4×n_taps in CPE averaging filter!')
        
    if mth_power < 1 or mth_power%1:
        raise ValueError('The parameter mth_power must be an integer ≥1')
        
    if not rho > 0:
        raise ValueError('The parameter rho must be >0')
    
    # for all filter_shapes: remove modulation of symbols (suitable only for MPSK formats with equidistant symbol-phase allocation)
    # raise unit-magnitude symbols to m-th power
    raised_symbols = np.exp(1j*np.angle(symbols)*mth_power)
    if mag_exp != 0: # exponentiate also the symbol magnitude (i.e. weighting of symbol phasors prior to filtering)
        raised_symbols = (np.abs(symbols)**mag_exp) * raised_symbols

    # smooth (slicing average) exponentiated symbols with non-causal FIR filter and estimate phase-noise random-walk
    wn = np.zeros(symbols.shape) # template impulse response for phase avg. filter
    
    # postive-time part of truncated window function (filter impulse response)
    if filter_shape == 'rect': # rectangular slicing filter
        wn[0: (n_taps//2 + 1)] = 1
    elif filter_shape == 'wiener':
        a = 1 + rho / 2 - np.sqrt( ( 1 + rho / 2)**2 - 1) # helper variable alpha
        wn[0: (n_taps//2 + 1)] = a * rho / (1 - a**2) * a**np.arange(n_taps // 2 + 1)
    elif filter_shape == 'hyperbolic':
        #wn[0: (n_taps//2 + 1)] = 1/(1+np.arange(n_taps//2+1))
        b = 2*rho
        wn[0: (n_taps//2 + 1)] = 1/(1 + b*np.arange(n_taps//2+1))
    elif filter_shape == 'lorentz':
        b = 0.5/rho
        wn[0: (n_taps//2 + 1)] = 1/(b*np.pi*(1 + np.arange(n_taps//2+1)**2/b**2))
    else:
        raise TypeError("filter_shape '" + filter_shape + "' not implemented yet")

    # negative-time part (symmetrical to positive-time part)
    wn[-n_taps//2+1::] = np.flip(wn[1:(n_taps//2 + 1)])
    wn = wn / np.sum(wn) # optional: normalize to unit-sum (make unbiased estimator)

    # apply averaging filter in frequency domain (no group delay)
    symb_filtered = filters.filter_samples(raised_symbols, np.fft.fftshift(np.fft.fft(wn)) , domain='freq')
    # extract phase, unwrap and rescale
    phi_est = 1/mth_power * np.unwrap(np.angle(symb_filtered))
    
    # for QPSK: rotate recovered constellation by pi/4 (as usual in context of digital communication)
    if mth_power == 4:
        phase_correction = np.pi/4
    else:
        phase_correction = 0
    
    # phase recovery: subract estimated phase-noise from input symbols
    rec_symbols = symbols * np.exp(-1j*(phi_est + phase_correction))
    # crop start and end (due to FIR induced delay)
    rec_symbols = rec_symbols[1*n_taps+1:-n_taps*1]
    phi_est = phi_est[1*n_taps+1:-n_taps*1]
    
    # for plotting / return
    cpe_window = np.concatenate((wn[-n_taps//2+1::],wn[0: (n_taps//2 + 1)]), axis=0)
    # for debugging
    if False:
        plt.figure()
        plt.stem(np.arange(-cpe_window.size//2+1,cpe_window.size//2+1),cpe_window)
        plt.title('applied CPE window function'); plt.xlabel('tap number');
        plt.ylabel('tap value'); ax = plt.gca(); ax.grid(axis='y'); plt.show()
    
    # generate output dict containing recovered symbols, estimated phase noise and CPE filter taps
    results = dict()
    results['rec_symbols'] = rec_symbols[1*n_taps+1:-n_taps*1]
    results['phi_est'] = phi_est # units [rad]
    results['cpe_window'] = cpe_window # center tap = zero-delay (t=0)
    return results

def _cpe_bps_loop(samples_norm, samples_out, dec_samples, est_phase_noise, errors, n_blocks, n_taps, rotations, constellation):
    """
    Helper function which implements the actual loop for the blind phase search
    carrier phase estimation (CPE).
    
    For explanation and help regarding the input and output parameters see
    docu of comm.rx.carrier_phase_estimation_bps().
    """
    
    for block in range(n_blocks):
        for idx, rotation in enumerate(rotations):
            # rotate block by test phases
            rotated_samples = samples_norm[block*n_taps:(block+1)*n_taps] * rotation
            # decide nearest constellation points for each sample in block for particular test phase
            dec_samples[:,idx] =  constellation[np.argmin(np.abs(rotated_samples - constellation.reshape(-1,1)), axis=0)]    
            # calc error for particular test phase
            errors[idx] = np.sum(np.abs(rotated_samples - dec_samples[:,idx])**2)                
        samples_out[block, :] = dec_samples[:,np.argmin(errors)]        
        est_phase_noise[block] = np.angle(rotations[np.argmin(errors)])
    
    return samples_out, est_phase_noise

def  carrier_phase_estimation_bps(samples, constellation, n_taps=15, n_test_phases=15, const_symmetry=np.pi/2, exec_mode='auto'):
    """
    "Blind phase search" carrier phase estimation and recovery.
    
    This method implements a slight modification of the carrier phase estimation
    and recovery method proposed in [1].
    
    A block of n_taps samples of the input signal (at 1 sample per symbol) is 
    rotated by n_test_phases individual, equally spaced phases between 
    -const_symmetry/2 and const_symmetry.
    
    The rotation phase producing a smallest squared error between these rotated 
    samples and the decided constellation points of the original constellation
    is assumed to be the phase error produced by the channel (or laser(s)).
    
    Additional to the decided (ideal) constellation per block (as proposed in [1]),
    also the unwraped estimated random phase walk is calculated and interpolated.
    This estimated phase walk is subtracted from the phases of the input samples
    and therefore used to recover the carrier phase of the signal.        

    Parameters
    ----------
    samples : 1D numpy array, real or complex
        input symbols.
    constellation : 1D numpy array, real or complex
        constellation points of the sent (original) signal.
    n_taps : int, optional
        numer of samples processed in one block. The default is 15.
    n_test_phases : int, optional
        number of phases which are tested. Defines the accuracy of the phase
        estimation method. The default is 15.
    const_symmetry : float, optional
        symmetry (ambiguity) of the original constellation points. 
        The default is pi/2.
    exec_mode: string
        Controls if Python or os-specific Cython implementation is used. 
        'auto': use Cython module if available, otherwise use Python implementation.
        'python': force to use Python implementation, even if a Cython module is available.
        'cython': force to use the Cython module, might cause an error if Cython module is not available.
        The default is 'auto'.

    Returns
    -------
     results : dict containing following keys
        samples_out : 1D numpy array, real or complex
            decided constellation points of the signal closest to the estimated
            random phase walk.
        samples_corrected : 1D numpy array, real or complex
            input symbols with recovered carrier phase.
        est_phase_noise : 1D numpy array, real
            estimated (unwraped) random phase walk.
            
    References
    ----------
    [1] T. Pfau, S. Hoffmann and R. Noe, "Hardware-Efficient Coherent Digital 
    Receiver Concept With Feedforward Carrier Recovery for M -QAM Constellations," 
    in Journal of Lightwave Technology, vol. 27, no. 8, pp. 989-999, April15, 2009, 
    doi: 10.1109/JLT.2008.2010511.
    """

    if exec_mode=='auto':
        if cython_available:
            exec_mode = 'cython'
        else:
            exec_mode = 'python'

    # normalize samples to constellation    
    mag_const = np.mean(abs(constellation))
    mag_samples = np.mean(abs(samples))
    samples_norm = samples * mag_const / mag_samples
    
    n_blocks = samples_norm.size // n_taps
    
    # generate all requested rotation phases
    rotations = np.exp(1j*np.arange(-const_symmetry/2, const_symmetry/2, const_symmetry/n_test_phases))
    
    errors = np.full(n_test_phases,fill_value=np.nan, dtype=np.float64)
    dec_samples = np.full((n_taps,n_test_phases), fill_value=np.nan, dtype=np.complex128)    
    samples_out = np.zeros([n_blocks, n_taps], dtype=np.complex128)
    est_phase_noise = np.zeros(n_blocks)
    
    if exec_mode=='cython':
        samples_out, est_phase_noise = rx_cython._cpe_bps_loop(samples_norm, samples_out, dec_samples, est_phase_noise, errors, n_blocks, n_taps, rotations, constellation)
    elif exec_mode=='python':
        samples_out, est_phase_noise = _cpe_bps_loop(samples_norm, samples_out, dec_samples, est_phase_noise, errors, n_blocks, n_taps, rotations, constellation)
    
    samples_out = np.asarray(samples_out).reshape(-1)
    
    # interpolate phase nosie between blocks onto symbols        
    unwrap_limit = 2 * np.pi / const_symmetry
    est_phase_noise = np.unwrap(np.asarray(est_phase_noise)*unwrap_limit)/unwrap_limit
    f_int = interpolate.interp1d(np.arange(n_blocks)*n_taps, est_phase_noise, kind='linear', bounds_error=False, fill_value='extrapolate')
    est_phase_noise_int = f_int(np.arange(n_blocks*n_taps))

    if n_blocks == 1:
        est_phase_noise_int = np.full(est_phase_noise_int.shape, fill_value=est_phase_noise)
    
    samples_corrected = samples_norm[:n_blocks*n_taps] * np.exp(1j * est_phase_noise_int)
    
    # generate output dict containing recoverd symbols and estimated phase noise
    results = dict()
    results['samples_out'] = samples_out
    results['samples_corrected'] = samples_corrected
    results['est_phase_noise'] = np.asarray(est_phase_noise_int)
    return results

def symbol_sequence_sync(sig, dimension=-1):
    """
    Estimate and compensate delay and phase shift between reference symbol / bit sequence and physical samples.
    
    The sig.samples have to be sampled at a rate of one sample per symbol. 
    
    A complex correlation between sig.samples and sig.symbols is performed in 
    order to find the delay and the phase shift between both signals. 
    
    Further also a complex correlation between conj(sig.samples) and sig.symbols 
    is performed in order to detect a flip (inversion) of the imaginary part.
    
    The found dalay is compensated for by cyclic shift (roll) of the reference symbol
    and bit sequence (sig.symobls and sig.bits, respectively) while the ambiguity 
    (phase shift and flip of imaginary part) is compensated for by manipulating
    the physical samples (sig.samples).
    
    This operation can be performed to one specific dimension of the signal or 
    to all dimensions of the signal independently.
    

    Parameters
    ----------
    sig : skcomm.signal.Signal
        signal containing the sequences to be synced.

    dimension : int
        dimension of the signal to operate on. If -1 the synchronization is performed
        to all dimensions of the signal. The default is -1.

    Returns
    -------
    return_dict : dict containing following keys
        number of dimension of signal : dict containing following keys
            phase_est : float
                estimated phase offset of specified signal dimension
            symbol_delay_est : int
                estimated symbol offset of specified signal dimension
        sig :  sskcomm.signal.Signal
            signal containing the synced sequences (all signal dimensions)

    """    
    if type(sig) != signal.Signal:
        raise TypeError("input parameter must be of type 'skcomm.signal.Signal'")
        
    if dimension == -1:
        dims = range(sig.n_dims)
    elif (dimension >= sig.n_dims) or (dimension < -1):
        raise ValueError("-1 <= dimension < sig.n_dims")
    else:
        dims = [dimension]
    
    # init dict for return values
    return_dict = {}

    # iterate over specified signal dimensions
    for dim in dims:
    
        # use only one symbol sequence for correlation
        corr_len = sig.symbols[dim].size
        
        # complex correlation of received, sampled signal and referece symbole sequence
        corr_norm = utils.find_lag(sig.samples[dim][:corr_len], sig.symbols[dim], period_length=None)
        # complex correlation of received, sampled and conjugated signal and referece symbole sequence
        corr_conj = utils.find_lag(np.conj(sig.samples[dim][:corr_len]), sig.symbols[dim], period_length=None)
        
        # decide which of the correlations is larger and determine delay index and phase from it
        if np.abs(corr_norm['max_correlation']) > np.abs(corr_conj['max_correlation']):
            symbols_conj = False
            symbol_delay_est = corr_norm['estimated_lag']
            phase_est = np.angle(corr_norm['max_correlation'])
        else:
            symbols_conj = True
            symbol_delay_est = corr_conj['estimated_lag']
            phase_est = np.angle(corr_conj['max_correlation'])   
        
        # quantize phase to mulitples of pi/2, because large noise can alter the phase of the correlation peak...
        # quantization therefore ensures phase rotations to be only multiples of pi/2 
        # TODO:CHECK if this is reasonable for every modulation format, if not, add a case decision here depending on modulation format!!!
        phase_est = np.round(phase_est / (np.pi/2)) * (np.pi/2)
        
        # for debugging purpose
        # print('conjugated:{}, delay in symbols={}, phase={}'.format(symbols_conj, symbol_delay_est, phase_est))
        # plt.plot(np.abs(corr_norm))
        # plt.plot(np.abs(corr_conj))
        # plt.show()
        
        # manipulate logical reference symbol sequence and bit sequences in order to compensate 
        # for delay 
        bps = np.log2(sig.constellation[dim].size)
        sig.symbols[dim] = np.roll(sig.symbols[dim], int(symbol_delay_est)) 
        sig.bits[dim] = np.roll(sig.bits[dim], int(symbol_delay_est*bps)) 
        
        # return symbol delay est & init nested dict
        return_dict[dim] = {"symbol_delay_est": int(symbol_delay_est)}  

        # manipulate physical samples in order to compensate for phase rotations and inversion 
        # of real and / or imaginary part (optical modulator ambiguity)
        if symbols_conj:    
            sig.samples[dim] = np.conj(sig.samples[dim] * np.exp(1j*phase_est))
            return_dict[dim]["phase_est"] = phase_est        
        else:        
            sig.samples[dim] = sig.samples[dim] * np.exp(-1j*phase_est)
            return_dict[dim]["phase_est"] = -phase_est   

    # return signal object
    return_dict["sig"] = sig
    
    return return_dict 

def _bae_loop(samples_in, samples_out, h, n_taps, sps, n_CMA, mu_cma, n_RDE, 
              mu_rde, radii, mu_dde, stop_adapting, sig_constellation, r, 
              shift, return_info, h_tmp, eps_tmp):
    """
    Helper function which implements the actual loop for the blind 
    adaptive equalizer (bae).
    
    For explanation and help regarding the input and output parameters see
    docu of comm.rx.blind_adaptive_equalizer().
    """
    
    n_update = 0
    
    # equalizer loop
    for sample in range(0, samples_out.size, shift):        
        # filter the signal for each desired output sample (convolution)
        # see [1], eq. (5)
        samples_out[sample] = np.sum(h * samples_in[n_taps+sample:sample:-1])        
        
        # for each symbol, calculate error signal... 
        if (sample % sps == 0):            
            # in CMA operation case
            if sample <= n_CMA:
                # calc error, see [1], eq. (26)
                eps = samples_out[sample] * (np.abs(samples_out[sample])**2 - r) 
                mu = mu_cma
            # in DDE operation case
            elif sample > (n_CMA + n_RDE):
                # decision (find closest point of original constellation)                    
                idx = np.argmin(np.abs(samples_out[sample] - sig_constellation))
                const_point = sig_constellation[idx]
                eps = (samples_out[sample] - const_point)
                mu = mu_dde
            # in RDE operation case
            else:
                # decision (find closest radius of original constellation)                    
                r_tmp = radii[np.argmin(np.abs(np.abs(samples_out[sample])**2 - radii))]
                eps = samples_out[sample] * (np.abs(samples_out[sample])**2 - r_tmp)                         
                mu = mu_rde
            
            # ...and update impulse response, if necessary
            if (int(sample/sps) <= stop_adapting):
                # update impulse response, see [1], eq (28)
                h -= mu * np.conj(samples_in[n_taps+sample:sample:-1]) * eps
            
            # save return info, if necessary
            if return_info:                
                # h_tmp.append(h.copy())
                # eps_tmp.append(eps)
                h_tmp[n_update,:] = h.copy()
                eps_tmp[n_update] = eps
            
            n_update += 1
                
    return samples_out, h_tmp, eps_tmp

def blind_adaptive_equalizer(sig, n_taps=111, mu_cma=5e-3, mu_rde=5e-3, mu_dde=0.5, decimate=False, 
                             return_info=True, stop_adapting=-1, start_rde=5000, 
                             start_dde=5000, exec_mode='auto'):    
    """
    Equalize the signal using a blind adaptive equalizer filter.
    
    A complex valued filter is initialized with a dirac impulse as impulse 
    response of length n_taps samples. Then the first signal sample is filtered.
    
    There exist tree operation modes:
        
        * constant modulus algorithm (CMA) operation [1]:
             Once each SYMBOL, the error (eps) to the desired output radius is calculated 
             and the filter impulse response is updated using the steepest gradient descent method [1]. 
             A step size parameter (mu_cma) is used to determine the adaptation speed. 
        * radially directed equalizer (RDE) operation [2]:
            Once each SYMBOL, the output signal is decided to ONE  of the desired radii (the nearest one) [2] and [3].
            The error (eps) between the output signal and this decided radius is calculated 
            and the filter impulse response is updated using the steepest gradient descent method. 
            A step size parameter (mu_rde) is used to determine the adaptation speed. 
        * decision directed equalizer (DDE) [2]:
            Once each SYMBOL, the output signal is decided to ONE, the nearest constellation point.
            The error (eps) between the output signal and this decided constellation point is calculated 
            and the filter impulse response is updated using the steepest gradient descent method. 
            A step size parameter (mu_dde) is used to determine the adaptation speed. CAUTION: this option
            works only very unreliable in case of phase noise!!!
            
    All three modes are in general run sequentially in the order CMA, RDE and DDE. 
    The parameters start_rde and start_dde control when the modes are switched.
    start_rde defines after how many SYMBOLS the RDE mode ist started after the 
    start of CMA mode. start_rde=0 does not start this mode at all.
    
    start_dde defines after how many SYMBOLS the DDE mode is started AFTER the 
    RDE mode has started. However, if the RDE mode is switched off (start_rde=0)
    the parameter start_dde defindes after how many SYMBOLS the DDE mode is 
    started AFTER the CMA mode has started. start_dde=0 does not start this mode at all.
    
    EXAMPLES:
    
        * start_rde=10e3, start_dde=0     -->     10e3 symbols CMA, rest RDE
        * start_rde=0, start_dde=0        -->     all samples filterd with CMA
        * start_rde=0, start_dde=10e3     -->    10e3 symbols CMA, rest DDE
        * start_rde=0, start_dde=1        -->    1 symbol CMA, rest DDE
        * start_rde=5e3, start_dde=10e3   -->     5e3 symbols CMA, 10e3 sybmosl RDE, rest DDE
    
    The equalizer can output every filtered SAMPLE or only every filtered 
    SYMBOL, which is controlled with the parameter decimate. 
    
    Further, the adaptation of the impulse response / equalizer can be stopped after 
    stop_adapting SYMBOLS.
    
    The equalizer operates on each signal dimension independently. The parameters
    can be passed as 
    
    * singular values [int, float or bool], which are broadcasted to every dimension, or
    * lists of length n_dims to specify independent parameters for each signal dimension
       
        
    Parameters
    ----------
    sig : skcomm.signal.Signal
        input signal to be equalized.
    n_taps : int or list of ints, optional
        length of the equalizers impulse response in samples for each dimension. Has to be odd. 
        The default is 111.
    mu_cma : float or list of floats, optional
        adaptation step size of the steepest gradient descent method for CMA operation for each dimension. 
        The default is 5e-3.
    mu_rde : float or list of floats, optional
        adaptation step size of the steepest gradient descent method for RDE operation for each dimension. 
        The default is 5e-3.
    mu_dde : float or list of floats, optional
        adaptation step size of the steepest gradient descent method for DDE operation for each dimension. 
        The default is 0.5.
    decimate : bool or list of bools, optional
        output every SAMPLE or every SYMBOL. The default is False.
    return_info : bool or list of bools, optional
        should the evolution of the impulse response and the error be recorded 
        and returned. The default is True.
    stop_adapting : int or list of ints, optional
        equaliter adaptation is stopped after stop_adapting SYMBOLS. -1 results 
        in a continous adaptation untill the last symbol of the input signal. 
        The default is -1.
    start_rde :  int or list of ints, optional
        defines after how many CMA SYMBOLS the RDE mode is started. start_rde=0 means 
        RDE mode does not start at all. See also examples above. The default is 5000.
    start_dde :  int or list of ints, optional
        defines after how many RDE SYMBOLS the DDE mode is started. start_rde=0 means 
        DDE mode does not start at all. See also examples above. The default is 5000.
    exec_mode: string
        Controls if Python or os-specific Cython implementation is used.
        'auto': use Cython module if available, otherwise use Python implementation.
        'python': force to use Python implementation, even if a Cython module is available.
        'cython': force to use the Cython module, might cause an error if Cython module is not available.
        The default is 'auto'.
    
    Returns
    -------
    results :  dict containing following keys
        sig : skcomm.signal.Signal
            equalized output signal.
        h : list of np.arrays 
            each list element consists of either a np.array of shape 
            (n_output_samples, n_taps) in case of return_info==True which
            documents the evolution of the equalizers impulse response or of an
            empty np.array in case of return_info==False
        eps : list of np.arrays
            each list element consists of either a np.array of shape 
            (n_output_samples,) in case of return_info==True which
            documents the evolution of the error signal or of an
            empty np.array in case of return_info==False.
            
    References
    ----------
    [1] D. Godard, “Self-recovering equalization and carrier tracking in twodimensional data communication systems,” IEEE Trans. Commun., vol. 28, no. 11, pp. 1867–1875, Nov. 1980.
    
    [2] S. Savory, "Digital Coherent Optical Receivers: Algorithms and Subsystems", IEEE STQE, vol 16, no. 5, 2010
    
    [3] P. Winzer, A. Gnauck, C. Doerr, M. Magarini, and L. Buhl, “Spectrally efficient long-haul optical networking using 112-Gb/s polarizationmultiplexed16-QAM,” J. Lightw. Technol., vol. 28, no. 4, pp. 547–556, Feb. 15, 2010.
    """

    if exec_mode=='auto':
        if cython_available:
            exec_mode = 'cython'
        else:
            exec_mode = 'python'

    if type(sig) != signal.Signal:
        raise TypeError("input parameter must be of type 'skcomm.signal.Signal'")
    
    # parameter cheching
    if type(n_taps) == list:
        if len(n_taps) != sig.n_dims:
            raise ValueError('if parameters are given as lists, their length has to match the number of dimensions of the signal (n_dims)')
    else:
        n_taps = [n_taps] * sig.n_dims
        
    if type(mu_cma) == list:
        if len(mu_cma) != sig.n_dims:
            raise ValueError('if parameters are given as lists, their length has to match the number of dimensions of the signal (n_dims)')
    else:
        mu_cma = [mu_cma] * sig.n_dims
    
    if type(mu_rde) == list:
        if len(mu_rde) != sig.n_dims:
            raise ValueError('if parameters are given as lists, their length has to match the number of dimensions of the signal (n_dims)')
    else:
        mu_rde = [mu_rde] * sig.n_dims
        
    if type(mu_dde) == list:
        if len(mu_dde) != sig.n_dims:
            raise ValueError('if parameters are given as lists, their length has to match the number of dimensions of the signal (n_dims)')
    else:
        mu_dde = [mu_dde] * sig.n_dims
        
    if type(decimate) == list:
        if len(decimate) != sig.n_dims:
            raise ValueError('if parameters are given as lists, their length has to match the number of dimensions of the signal (n_dims)')
    else:
        decimate = [decimate] * sig.n_dims
        
    if type(return_info) == list:
        if len(return_info) != sig.n_dims:
            raise ValueError('if parameters are given as lists, their length has to match the number of dimensions of the signal (n_dims)')
    else:
        return_info = [return_info] * sig.n_dims
        
    if type(stop_adapting) == list:
        if len(stop_adapting) != sig.n_dims:
            raise ValueError('if parameters are given as lists, their length has to match the number of dimensions of the signal (n_dims)')
    else:
        stop_adapting = [stop_adapting] * sig.n_dims
        
    if type(start_rde) == list:
        if len(start_rde) != sig.n_dims:
            raise ValueError('if parameters are given as lists, their length has to match the number of dimensions of the signal (n_dims)')
    else:
        start_rde = [start_rde] * sig.n_dims
        
    if type(start_dde) == list:
        if len(start_dde) != sig.n_dims:
            raise ValueError('if parameters are given as lists, their length has to match the number of dimensions of the signal (n_dims)')
    else:
        start_dde = [start_dde] * sig.n_dims
    
    # generate lists for return info (evolution of impulse response and eps)
    h_tmp = []
    eps_tmp = []
    
    # iterate over dimensions
    for dim in range(sig.n_dims):        
    
        if n_taps[dim] % 2 == 0:
            raise ValueError('n_taps need to be odd')       
        
        # samples per symbol 
        sps = int(sig.sample_rate[dim] / sig.symbol_rate[dim])
        
        # init equalizer impulse response to delta
        # TODO: add option to set impulse response from outside
        h = np.zeros(n_taps[dim], dtype=np.complex128)
        h[n_taps[dim]//2] = 1.0
        
        # generate sample arrays
        samples_in = sig.samples[dim]
        samples_out = np.full(samples_in.size-n_taps[dim], np.nan, dtype=np.complex128)        
        
        # desired modulus for CMA for p=2, see [1], eq. (28) + 1    
        r = np.mean(np.abs(sig.constellation[dim])**4) / np.mean(np.abs(sig.constellation[dim])**2) 
        
        # desired radii for RDE, enhancement of [2], eq. (44)
        if start_rde[dim] > 0:
            radii = np.unique(np.abs(sig.constellation[dim]))**2
        else:
            radii = np.asarray([0.0])
        
        # convert symbols to samples
        start_rde[dim] = start_rde[dim] * sps
        start_dde[dim] = start_dde[dim] * sps
        # calc number of CMA symbols               
        if start_rde[dim] == start_dde[dim] == 0:
            n_CMA = samples_out.size
        else:
            n_CMA = start_rde[dim] if start_rde[dim] != 0 else start_dde[dim]
        # calc number of DDE symbols:
        n_DDE = 0 if start_dde[dim] == 0 else samples_out.size - (n_CMA + start_dde[dim])
        n_DDE = n_DDE if start_rde[dim] != 0 else samples_out.size - (n_CMA)
        # calc number of RDE symbols
        n_RDE = samples_out.size - (n_CMA + n_DDE)
       
        # # DEBUG PRINTS
        # print('samples_out:{}, start_rde: {}, start_dde:{}'.format(samples_out.size, start_rde[dim], start_dde[dim]))
        # print('n_CMA:{}, n_RDE: {}, n_DDE:{}\n'.format(n_CMA, n_RDE, n_DDE))
            
        # is output caluculated for each sample or only for each symbol?
        if decimate[dim]:
            shift = sps
        else:
            shift = 1
        # will the equalizer stop adapting
        if stop_adapting[dim] == -1:
            stop_adapting[dim] = int(samples_out.size/sps)
        
        # generate new list element for each dimension and initialize return values
        if return_info[dim]:            
            h_tmp.append(np.full((int(np.ceil((samples_in.size-n_taps[dim])/shift)), n_taps[dim]), 
                                 np.nan, dtype=np.complex128())) 
            eps_tmp.append(np.full(int(np.ceil((samples_in.size-n_taps[dim])/shift)), 
                                   np.nan, dtype=np.complex128()))
        else:
            h_tmp.append(np.asarray([[]],dtype=np.complex128()))
            eps_tmp.append(np.asarray([],dtype=np.complex128()))
        
        # use compiled Cython code for EQ loop...
        if exec_mode=='cython':
            samples_out, h_tmp[dim], eps_tmp[dim] = rx_cython._bae_loop(samples_in, 
                                                                        samples_out, 
                                                                        h, n_taps[dim], 
                                                                        sps, n_CMA, 
                                                                        mu_cma[dim], 
                                                                        n_RDE, mu_rde[dim], 
                                                                        radii, mu_dde[dim], 
                                                                        stop_adapting[dim], 
                                                                        sig.constellation[dim], 
                                                                        r, shift, return_info[dim], 
                                                                        h_tmp[dim], eps_tmp[dim])            
        # ... or use Python code
        elif exec_mode=='python':
            samples_out, h_tmp[dim], eps_tmp[dim] = _bae_loop(samples_in, samples_out, 
                                                              h, n_taps[dim], sps, 
                                                              n_CMA, mu_cma[dim], 
                                                              n_RDE, mu_rde[dim], 
                                                              radii, mu_dde[dim], 
                                                              stop_adapting[dim], 
                                                              sig.constellation[dim], 
                                                              r, shift, return_info[dim], 
                                                              h_tmp[dim], eps_tmp[dim])
        
        # only take "valid" (actually calculated) output samples
        if decimate[dim]:
            samples_out = samples_out[::sps]
            sig.sample_rate[dim] = sig.symbol_rate[dim]
        
        # generate output signal and return_info np.arrays
        sig.samples[dim] = samples_out
        
    # generate result dict
    results = dict()
    results['sig'] = sig
    results['h'] = h_tmp
    results['eps'] = eps_tmp
    return results

def combining(sig, comb_method='EGC', weights=None, combine_upto=None):
    """
    Performs Diversity Combining of the rows of a passed n-dimensional signal-
    class object, where each row represents the signal captured by an antenna 
    of a SIMO system, according to the passed SNR values per dimension 
    if comb_method == MRC. If comb_method == EGC, because of equal gain, there 
    is no need for know SNR of the signals.

    Parameters
    ----------
    sig : signal-class object
        n-dimensional signal object with list of sample arrays in the 'samples'
        attribute.
    comb_method : str, optional
        Combining method. MRC, EGC, and SDC are available. The default is 'MRC'.
    weigths : 1d numpy array, optional for comb_method == EGC
        array of weigthing values matching the number of signal dimensions of  
        the sig object for combination. 
    combine_upto : int, optional
        Combine just first n sample arrays togheter. If None, all sample arrays 
        are combined. Default is None.

    Returns
    -------
    sig_comb : signal object
        one-dimensional signal object after combining. The sample attribute now 
        has the combined sample array in the 'samples' attribute of its only 
        dimension.

    """
    # error checks
    if len(sig.samples) < 2:
        print("Signal object only has one dimension. No combining was performed.")
        return sig

    if comb_method == "MRC":
        weigths = np.array(weights)
        if sig.n_dims != weigths.size:
            raise ValueError("Number of signal dimensions must match length of SNR value array.")
        
    # create new object with one dimension
    sig_comb = signal.Signal(n_dims=1)
    for key in vars(sig):
        if key == '_n_dims':
            pass
        else:
            vars(sig_comb)[key] = vars(sig)[key][0]
    
    # scaling           
    if comb_method == 'MRC':
        for i in range(len(sig.samples)):
            sig.samples[i] = sig.samples[i] * weights[i] 
    elif comb_method == 'EGC':
        pass
    elif comb_method == 'SDC':
        mask = np.where(weights == np.max(weights),1,0)
        for i in range(len(sig.samples)):
            sig.samples[i] = sig.samples[i] * mask[i]
    else:
        raise ValueError("Combining method not implemented. Available options are MRC, EGC, and SDC.")
        
    if combine_upto != None:
        combine_range = int(combine_upto)
    else: 
        combine_range = len(sig.samples)

    # combination
    sig_comb.samples = np.sum(sig.samples[:combine_range],axis=0)
    # normalize samples to mean power of 1
    sig_comb.samples = sig_comb.samples[0] / (np.sqrt(np.mean(np.abs(sig_comb.samples[0])**2)))
    
    return sig_comb

def frequency_offset_correction(samples, sample_rate=1.0, symbol_rate=1.0, matched_filter=None, roll_off=None, max_FO_expected=None, debug=False):
    """
    Frequency offset estimation and correction (FOE and FOC).
    
    This function estimates the carrier frequency offset by using a spectral
    method described in [1]. The spectral method is performed on symbols, therefore 
    a decimation is applied in case of oversampling.

    If specified, the incoming samples are filtered with a matched filter before they are raised to
    the power of 4. FFT is formed afterwards. If specified, the search range for the frequency offset is
    is limited to +-max_FO_expected. 

    For a more accurate estimation, a 2nd order polynomial is fitted to the spectrum before the maximum is determined. 
    The correction is done by multiplying the samples with a complex exponential having a frequency with same amplitude
    as the estimated frequency offset, but opposite sign.        

    Please note that only singals with an integer oversampling factor can currently be handled.
    
    Parameters
    ----------
    samples : 1D numpy array, real or complex
        input signal. It is assumed that the first sample is taken at the correct (temporal) 
        sampling instant, theefore no timing recovery needs to be performed.   
    sample_rate : float
        sample rate of input signal in Hz. The default is 1.0.
    symbol_rate : float
        symbol rate of input signal in Hz. The default is 1.0.
    matched_filter : string
        if not None, matched filter specified by string is applied.
        Currently only a 'root raised cosine' filter ('rrc') is implemented. Default is None.
    roll_off : float
        roll off of the (matched) root raised cosine filter. Default is None.
    max_FO_expected : float
        if not None, search range of the frequency offset. The frequency offset is expected to 
        be in the range of +- max_FO_expected. Default is None.
    debug : bool
        Debug flag for generating debug plots. Default is False.

    Returns
    -------
    results:  dict containing following keys
        samples_corrected: 1D numpy array, real or complex
                            output signal, which is input signal multiplyied with a complex
                            exponential having a frequency with same amplitude
                            as the estimated frequency offset, but opposite sign.
        estimated_fo: 1D numpy array, real or complex. 
                    Estimated frequency offset in Hz.
                    
    References
    ----------
    [1] Savory, S. (2010, September/Oktober). Digital Coherent Optical Receivers: 
        Algorithms and Subsystems. Abgerufen von https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=5464309 
    
    [2] Dr. Lichtmann, M.. (o.J.). PySDR: A Guide to SDR and SDP using Python. 
        Abgerufen von https://pysdr.org/content/frequency_domain.html
     
    """  
    # make copy of original samples (and sample rate) for applying FOC on original samples
    samples_orig = samples
    sample_rate_orig = sample_rate

    # (matched) filtering for increasing FOC performance if specified. 
    if matched_filter != None and matched_filter == "rrc":
        samples = filters.raised_cosine_filter(samples, sample_rate=sample_rate, symbol_rate=symbol_rate, 
                                         roll_off=roll_off, length=-1, root_raised=True, domain='freq')
    elif matched_filter != None and matched_filter != "rrc":
        raise Exception("matched filter type for FOC not implemented or specified!")

    # decimate samples to 1 sps
    # for decimation, a integer oversamples (e.g. 2) is required. Otherwise, raise error
    if (sample_rate/symbol_rate)%1 != 0:
        raise Exception("integer oversampling or sps=1 required for FOC")
    samples = samples[::int(sample_rate/symbol_rate)]
    sample_rate = symbol_rate # sample rate is now symbol rate

    # Creating time and frequency axis
    t = np.arange(0, np.size(samples)) / sample_rate 
    f = np.fft.fftshift(np.fft.fftfreq(t.shape[-1], d=1/sample_rate)) 
  
    # samples to the power of order 4 and FFT
    order = 4
    samples_foe = samples**(order)
    raised_spectrum = np.fft.fftshift((np.abs(np.fft.fft(samples_foe))))
    
    # crop spectrum to expected FOE area if specified
    if max_FO_expected != None:
        search_window = np.abs(f) <= max_FO_expected*order
        raised_spectrum *= search_window        

    # Finding Index of peak of power spectrum
    max_freq_index = np.argmax(raised_spectrum) 

    # Shift frequency to baseband for numerical better polyfit 
    shift_freq = f[max_freq_index]
    f = f-shift_freq

    # Polyfit 2nd order (range of polyfit: maximum +-1 sample)
    y_res = raised_spectrum[max_freq_index-1:max_freq_index+2]
    x_res = f[max_freq_index-1:max_freq_index+2]
    poly_coeffs = np.polyfit(x_res, y_res, 2)

    # Index of maximum of polyfit = x0 = -b/(2*a)
    max_value_of_poly = -poly_coeffs[1]/(2*poly_coeffs[0])

    # shift back to original value of peak of power spectrum
    f = f+shift_freq
    
    # Estimated Frequency offset
    estimated_freq = (max_value_of_poly+shift_freq)/order

    # Frequency Offset Recovery / compensation on original data
    t_orig = np.arange(0, np.size(samples_orig)) / sample_rate_orig 
    samples_corrected = samples_orig * np.exp(-1j*2*np.pi*(estimated_freq)*t_orig)    

    # generate plots for debugging if specified
    if debug == True:
        plt.figure()
        plt.title("FOE raised spectrum")
        plt.plot(f, 20*np.log10(raised_spectrum / np.max(raised_spectrum)), label="20*np.log(spectrum / np.max(spectrum))")
        plt.xlabel("frequency [Hz]")
        plt.grid(which="both")
        plt.legend()

        fbins_old = np.fft.fftshift((np.abs(np.fft.fft(samples_orig, n=int(t.shape[-1])))))
        fbins_new = np.fft.fftshift((np.abs(np.fft.fft(samples_corrected, n=int(t.shape[-1])))))

        plt.figure()
        plt.title("FOC raised spectrum(s)")
        plt.plot(f, 20*np.log10(fbins_old / np.max(raised_spectrum)), label="before FOE/FOC")
        plt.plot(f, 20*np.log10(fbins_new / np.max(raised_spectrum)), linestyle="--", label="after FOE/FOC")
        plt.xlabel("frequency [Hz]")
        plt.grid(which="both")
        plt.legend()

        plt.show()

    # generate output dict containing recoverd symbols and estimated frequency offset
    results = dict()
    results['samples_corrected'] = samples_corrected
    results['estimated_fo'] = estimated_freq
    return results

def stokesEQ_pdm(samples_X:np.ndarray, samples_Y:np.ndarray, modformat:str='complex')->dict:
    """
    Performs blind polarization demultiplexing of polarization-multiplexd complex-modulated signals.
    The method is based on finding (in Stokes space) a symmetry plane of the incoming sampled data 
    (including symbol transitions) from a SVD-based least squares fit [1/sect.3.2].
    The normal vector of the plane identifies the two orthogonal input polarization states and is 
    used to determine the desired polarization-rotation of the input signal.
    At least 3 input samples per polarization have to be provided together that form 3 linearly
    independent Stokes vectors for plane fitting. The method does not involve data demodulation
    and thus should work independent of the modulation format.
    
    Parameters
    ----------
    samples_X:
        Input signal samples in X-polarization. Must be of same size as 'samples_Y'
    samples_Y:
        Input signal samples in Y-polarization. Must be of same size as 'samples_X'
    modformat: "complex", "real"
        * "complex":
            Specifies that the modulation format of the incoming signal is a complex modulation per
            polarization (PDQ-QAM).
        * "real":
            Specifies that the incoming signals modulation format is a real-valued modulation per 
            polarization (PDQ-BPSK, PDM-ASK, PDM-PAM).
        The default is "complex".

    Returns
    -------

    results containing the following keys
        * samples_X : np.ndarray[np.complex128 | np.float64]
            Output signal samples after polarization separation in X-polarization.
        * samples_Y : np.ndarray[np.complex128 | np.float64]
            Output signal samples after polarization separation in Y-polarization.
        * U : np.ndarray[np.complex128 | np.float64]
            :math:`2\\times2` Jones (rotation) matrix :math:`\mathbf{U}`, which was applied to the input signal.
        * Nv : np.ndarray[np.float64]
            :math:`3\\times1` normal vector of the fitting plane in Stokes space (w/o centroid).
        * C : np.ndarray[np.float64]
            Centroid (:math:`3\\times1` average Stokes vector) of all Stokes space samples.
    
    References
    ----------
    .. [1] B. Szafraniec, B. Nebendahl, and T. Marshall, “Polarization demultiplexing in 
        Stokes space,” Optics Express, vol. 18, no. 17, pp. 17928–17939, Aug. 2010
        `(DOI) <https://opg.optica.org/oe/fulltext.cfm?uri=oe-18-17-17928&id=204878>`_

    See Also
    --------
    :meth:`skcomm.channel.rotatePol_pdm()`
    :meth:`skcomm.utils.jones2stokes_pdm()`
    """
    # TODO: add additional parameters: 
    #   range of used input samples [start, stop]
    #   flag for only providing estimation of rotation matrix (w/o changing actual PDM signal)
    #   option to fragmentize estimation and correction to implement a dynamic polarizatioh tracker
    #   debug option : Stokes-space plot of signal & fitted plane etc.

    # 0. Input argument checks
    if (not isinstance(samples_X,np.ndarray)) or (not isinstance(samples_Y,np.ndarray)) or (samples_X.ndim!=1) or (samples_Y.ndim!=1):
        raise TypeError('samples_X and samples_Y must be 1-D Numpy arrays')
    if samples_X.shape != samples_Y.shape:
        raise ValueError('samples_X and samples_Y must be of same size!')
    
    # TODO: assign a function parameter to select the range of input samples for estimation
    N = samples_X.size # temp: use all samples for estimation
    N = np.min((N,samples_X.size)) # no. of SOPs used for pol. estimation
    
    # 1. Convert PDM signal from Jones space to Stokes space (sample-wise)
    result_j2s = utils.jones2stokes_pdm(samples_X[:N],samples_Y[:N])
    S0, S1, S2, S3 = result_j2s["S0"], result_j2s["S1"], result_j2s["S2"], result_j2s["S3"]
    # maxpow = np.max(np.abs(S0))

    # 2. Fit plane into Stokes space samples (in least squares sense):
    # https://math.stackexchange.com/questions/99299/best-fitting-plane-given-a-set-of-points
    X = np.vstack((S1,S2,S3))   # form a 3×N matrix X out of the resulting coordinates
    C = np.mean(X,axis=1) # subtract out the centroid
    X = X - C[:,np.newaxis]
    U,S,_ = np.linalg.svd(X,full_matrices=False) # calculate its singular value decomposition
    
    if modformat.lower() == 'complex':  # the normal vector of the best-fitting ellipsoid is the left
        idx = np.argmin(S)              #   singular vector corresponding to the SMALLEST singular value
    elif modformat.lower() == 'real':   # the major axis of the best-fitting 'cigar' is the left
        idx = np.argmax(S)              #   singular vector corresponding to the LARGEST singular value
    else:
        raise ValueError('The parameter "modformat" must be either "complex" or "real"')
    
    Nv = U[:,idx] # normal vector of best-fitting ellipsoid (or 'cigar')
    # print('\nAngles (deg) of normal vector of best-fitting plane:') # TODO: check!
    # print('phi_s1={0:.1f}°,  phi_s2={1:.1f}°,  phi_s3={2:.1f}°\n'.format(*np.arccos(Nv)*180/np.pi))

    # 3. Calculate from Nv the angles psi, phi and theta for the polarization-rotation function "rotatePol_pdm"
    # to rotate (in Jones space) the input samples into S2-S3 plane in Stokes space (i.e. perform polarization separation)
    # see https://de.mathworks.com/matlabcentral/answers/79296-how-to-do-a-3d-circle-in-matlab: Answer by Kye Taylor
    # see https://en.wikipedia.org/wiki/Stokes_parameters
    # ==> see PhD diss D.Sperti, Appdx. A, Fig.A.1 ()
    Theta   = 0.5*np.arctan2(Nv[1], Nv[0]) # angle 2*Theta between S1-axis and the projecton of SOP-vector onto the S1-S2-plane
    Epsilon = 0.5*np.arctan2(Nv[2], np.sqrt(Nv[0]**2 + Nv[1]**2)) # angle 2*Epsilon between SOP-vector and the S1-S2-plane

    # 4a. Rotate SOP-vector back around S3-axis: SOP now in plane S1-S3
    tmp = np.asarray([0.0]*3)
    result_rot = channel.rotatePol_pdm(tmp,tmp, theta=-Theta, phi=0.0, psi=0.0)
    U1 = result_rot["U"]
    
    # 4b. rotate back Epsilon around S2-axis: SOP gets parallel to S1 (i.e., pol. separated)
    result_rot = channel.rotatePol_pdm(tmp, tmp, theta=Epsilon, psi=0.0, phi=np.pi/2)
    U2 = result_rot["U"]

    # 4c. for real-valued mod. format (1D per pol.), rotate SOP around S3 to be parallel to S2
    U3 = np.eye(2)
    if  modformat.lower() == 'real':
        result_rot = channel.rotatePol_pdm(tmp,tmp, theta=-np.pi/4)
        U3 = result_rot["U"]
    
    # 5.matrix multiplication with input Jones vector (sample-by-sample)
    U = U3 @ U2 @ U1 # combined rotation matrix (Jones space)
    output = U @ np.vstack((samples_X.flatten(),samples_Y.flatten()))

    results = {
    "samples_X": output[0],
    "samples_Y": output[1],
    "U": U,
    "Nv": Nv, # normal vector of fitting plane (w/o centroid)
    "C":  C # centroid (mean Stokes vector)
    }
    return results