import numpy as np
import scipy as sc
import matplotlib.pyplot as plt
import pandas as pd

import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.api import ARDL
from scipy.fftpack import rfft, irfft


def simple_LR(
    fr_ts, 
    behavior_ts, 
    behavior_name
):
    """
    Fits a simple linear regression model between neural firing rates 
    and a behavioral variable.
    
    This function performs the following steps:
    1. Truncates time series to equal lengths
    2. Creates a pandas DataFrame with the variables
    3. Removes any NA values
    4. Fits an Ordinary Least Squares regression model
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of neural firing rates
    behavior_ts : array-like
        Time series of behavioral variable to correlate with firing rates
    behavior_name : str
        Name of the behavioral variable (used for DataFrame column)
        
    Returns
    -------
    statsmodels.regression.linear_model.RegressionResultsWrapper
        Fitted OLS regression model results containing:
        - coefficients
        - standard errors
        - t-statistics
        - p-values
        - R-squared
        - other regression diagnostics
        
    Examples
    --------
    >>> firing_rates = [1.2, 3.4, 2.1, 4.5]
    >>> running_speed = [0.1, 0.3, 0.2, 0.4] 
    >>> results = simple_LR(firing_rates, running_speed, 'speed')
    >>> print(results.summary())
    """

    # make equal length
    min_session_len = min(len(fr_ts), len(behavior_ts))
    fr_ts = fr_ts[:min_session_len]
    behavior_ts = behavior_ts[:min_session_len]
    
    df_var = pd.DataFrame({'fr': fr_ts,
                          behavior_name: behavior_ts})
    df_var = df_var.dropna()
    
    df_var_endo = df_var['fr']
    df_var_exog = df_var[behavior_name]
    X = sm.add_constant(df_var_exog)
    model_OLS = sm.OLS(df_var_endo, X)
    results_OLS = model_OLS.fit()
    
    return results_OLS


###########################################################################
### NONPARAMETRIC PERMUTATION TEST ###

def session_permutation(
    fr_ts, 
    behavior_ts, 
    behavior_ts_ensemble, 
    behavior_name, 
    subsample_ensemble=None
):
    """
    Performs permutation testing to assess the statistical significance of a neuron's 
    behavioral correlation by comparing against a null distribution.
    
    This function:
    1. Calculates the t-statistic for the target session's linear regression
    2. Creates a null distribution by computing t-statistics from an ensemble of other sessions
    3. Determines the percentile rank of the target t-statistic within the null distribution
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of neural firing rates for the target session
    behavior_ts : array-like
        Time series of behavioral variable for the target session
    behavior_ts_ensemble : array-like
        Collection of behavior time series from multiple sessions used to create
        the null distribution. Shape should be (n_sessions, max_timepoints)
    behavior_name : str
        Name of the behavioral variable being analyzed
    subsample_ensemble : int, optional
        If provided, randomly subsamples this many sessions from behavior_ts_ensemble
        to reduce computation time
        
    Returns
    -------
    float
        Percentile rank (0-100) of the target session's t-statistic within the null
        distribution. Values close to 0 or 100 indicate significant correlations.
        
    Examples
    --------
    >>> fr = [1.2, 3.4, 2.1, 4.5]
    >>> behavior = [0.1, 0.3, 0.2, 0.4]
    >>> behavior_null = np.random.rand(100, 4)  # 100 random sessions
    >>> percentile = session_permutation(fr, behavior, behavior_null, 'speed')
    >>> print(f"Percentile rank: {percentile}")
    
    Notes
    -----
    - The function assumes stationarity across sessions in the null distribution
    - Time series are truncated to match the shortest length between firing rate
      and behavior
    - The underlying linear regression is performed using statsmodels OLS
    """

    # calculate tvalue for the target session
    results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
    tvalue_target = results_OLS.tvalues[behavior_name]
    
    # calculate ensemble of tvalues for null distribution
    tvalue_ensemble = []
    if subsample_ensemble is not None:
        idx = np.random.randint(len(behavior_ts_ensemble), size=subsample_ensemble)
        behavior_ts_ensemble = behavior_ts_ensemble[idx]
        
    for session_idx, behavior_ts in enumerate(behavior_ts_ensemble):
        # make sure both ts have same length
        min_session_len = min(len(fr_ts), len(behavior_ts))
        fr_ts = fr_ts[:min_session_len]
        behavior_ts = behavior_ts[:min_session_len]
        
        # OLS fit
        results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
        tvalue_ensemble.append(results_OLS.tvalues[behavior_name])
        
    percentile = sc.stats.percentileofscore(tvalue_ensemble, tvalue_target)
    return percentile


def phase_randomization(
    fr_ts, 
    behavior_ts, 
    behavior_name, 
    ensemble_size=100
):
    """
    Performs statistical testing using phase randomization to assess the significance 
    of neural-behavioral correlations while preserving the power spectrum.
    
    This function creates a null distribution by phase-randomizing the firing rate 
    time series while maintaining its power spectrum, then computes correlation 
    statistics against the original behavioral time series.
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of neural firing rates
    behavior_ts : array-like
        Time series of behavioral variable
    behavior_name : str
        Name of the behavioral variable being analyzed
    ensemble_size : int, optional (default=100)
        Number of phase-randomized time series to generate for null distribution
        
    Returns
    -------
    float
        Percentile rank (0-100) of the target correlation's t-statistic within 
        the null distribution of phase-randomized correlations
        
    Notes
    -----
    The phase randomization process:
    1. Computes FFT of the firing rate time series
    2. Preserves the power spectrum but randomizes the phase components
    3. Performs inverse FFT to generate surrogate time series
    4. Ensures non-negativity of the randomized firing rates
    """
    
    def phase_scrambled_ts(ts):
        """
        Generate a phase-randomized version of an input time series.
        
        Preserves the power spectrum of the original signal while randomizing 
        the phase components, creating a surrogate time series with similar 
        temporal structure but shuffled timing.
        
        Parameters
        ----------
        ts : array-like
            Input time series to be phase-randomized
            
        Returns
        -------
        array-like
            Phase-randomized version of the input time series
        
        Notes
        -----
        Process:
        1. Compute real FFT of time series
        2. Separate power and phase components
        3. Randomly shuffle phases while preserving power
        4. Reconstruct signal with inverse FFT
        """
        fs = rfft(ts)
        # rfft returns real and imaginary components in adjacent elements of a real array
        pow_fs = fs[1:-1:2]**2 + fs[2::2]**2
        phase_fs = np.arctan2(fs[2::2], fs[1:-1:2])
        phase_fsr = phase_fs.copy()
        np.random.shuffle(phase_fsr)
        
        # use broadcasting and ravel to interleave real and imaginary components
        # first and last elements in fourier array don't have phase information
        fsrp = np.sqrt(pow_fs[:, np.newaxis]) * np.c_[np.cos(phase_fsr), np.sin(phase_fsr)]
        fsrp = np.r_[fs[0], fsrp.ravel(), fs[-1]]
        tsr = irfft(fsrp)
        return tsr
    
    # calculate tvalue for the target session
    results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
    tvalue_target = results_OLS.tvalues[behavior_name]
    
    # calculate ensemble of tvalues for null distribution
    tvalue_ensemble = []
    for randomize_id in range(ensemble_size):
        # generate phase randomized time series, make sure non-negative
        fr_phase_randomized = phase_scrambled_ts(fr_ts)
        fr_phase_randomized -= np.min(fr_phase_randomized)
        results_OLS = simple_LR(fr_phase_randomized, behavior_ts, behavior_name)
        tvalue_ensemble.append(results_OLS.tvalues[behavior_name])
        
    percentile = sc.stats.percentileofscore(tvalue_ensemble, tvalue_target)
    return percentile


def linear_shift(
    fr_ts, 
    behavior_ts, 
    behavior_name, 
    ensemble_size=100, 
    min_shift=3
):
    """
    Tests significance of neural-behavioral correlations using cyclic time shifts 
    of the behavioral time series.
    
    This function creates a null distribution by repeatedly shifting the behavioral 
    time series forward by random amounts and computing correlation statistics with 
    the original firing rate time series. This approach breaks temporal relationships 
    while preserving the behavioral time series' statistical properties.
    
    Parameters
    ----------
    fr_ts : array-like
        Time series of neural firing rates
    behavior_ts : array-like
        Time series of behavioral variable
    behavior_name : str
        Name of the behavioral variable being analyzed
    ensemble_size : int, optional (default=100)
        Number of shifted time series to generate for null distribution
    min_shift : int, optional (default=3)
        Minimum number of time points to shift the behavioral time series
        
    Returns
    -------
    float
        Percentile rank (0-100) of the target correlation's t-statistic within 
        the null distribution of shift-based correlations
        
    Notes
    -----
    The shifting process:
    1. Randomly selects a shift amount between min_shift and half the time series length
    2. Shifts behavioral time series forward by that amount
    3. Truncates both time series to match lengths
    4. Computes correlation statistics
    
    This method:
    - Preserves the temporal structure within each signal
    - Maintains behavioral time series statistics
    - Controls for spurious correlations while being computationally efficient
    - Assumes stationarity of the behavioral signal
    
    Examples
    --------
    >>> fr = np.array([1.2, 3.4, 2.1, 4.5, 3.2, 2.8])
    >>> behavior = np.array([0.1, 0.3, 0.2, 0.4, 0.3, 0.2])
    >>> percentile = linear_shift(fr, behavior, 'speed', ensemble_size=50)
    >>> print(f"Significance percentile: {percentile}")
    """

    # calculate tvalue for the target session
    results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
    tvalue_target = results_OLS.tvalues[behavior_name]
    
    # calculate ensemble of tvalues for null distribution
    tvalue_ensemble = []
    for shift_id in range(ensemble_size):
        # generate linear shifted time series
        max_linear_shift = int(len(behavior_ts) / 2)
        shift_start_trial = np.random.randint(min_shift, high=max_linear_shift)
        behavior_ts_linear_shift = behavior_ts[shift_start_trial:]
        results_OLS = simple_LR(fr_ts[:len(behavior_ts_linear_shift)], 
                              behavior_ts_linear_shift, behavior_name)
        tvalue_ensemble.append(results_OLS.tvalues[behavior_name])
        
    percentile = sc.stats.percentileofscore(tvalue_ensemble, tvalue_target)
    return percentile


def cyclic_shift(
    fr_ts, 
    behavior_ts, 
    behavior_name, 
    ensemble_size=100, 
    min_shift=3
):
   """
   Tests significance of neural-behavioral correlations using cyclic permutations
   of the behavioral time series.
   
   This function creates a null distribution by repeatedly performing cyclic shifts
   of the behavioral time series and computing correlation statistics with the original 
   firing rate time series. Unlike linear shift, cyclic shift preserves the full 
   length of the time series by wrapping around.
   
   Parameters
   ----------
   fr_ts : array-like
       Time series of neural firing rates
   behavior_ts : array-like
       Time series of behavioral variable 
   behavior_name : str
       Name of the behavioral variable being analyzed
   ensemble_size : int, optional (default=100)
       Number of shifted time series to generate for null distribution
   min_shift : int, optional (default=3)
       Minimum number of time points to shift the behavioral time series to ensure
       sufficient temporal decorrelation
       
   Returns
   -------
   float
       Percentile rank (0-100) of the target correlation's t-statistic within 
       the null distribution of cyclically-shifted correlations
       
   Notes
   -----
   The cyclic shifting process:
   1. Randomly selects a shift amount between min_shift and length-min_shift
   2. Splits behavioral time series at that point
   3. Recombines the pieces in reversed order to create shifted series
   4. Maintains original time series length
   
   Advantages over linear shift:
   - Preserves complete behavioral time series structure
   - No data loss from truncation
   - Maintains exact length matching between signals
   - Better for periodic or continuous recordings
   
   Assumptions:
   - Behavioral signal is approximately stationary
   - Temporal correlations decay within min_shift time points
   - Time series endpoints are meaningfully related
   
   Examples
   --------
   >>> fr = np.array([1.2, 3.4, 2.1, 4.5, 3.2, 2.8])
   >>> behavior = np.array([0.1, 0.3, 0.2, 0.4, 0.3, 0.2])
   >>> percentile = cyclic_shift(fr, behavior, 'speed', ensemble_size=50)
   >>> print(f"Significance percentile: {percentile}")
   """

   # calculate tvalue for the target session
   results_OLS = simple_LR(fr_ts, behavior_ts, behavior_name)
   tvalue_target = results_OLS.tvalues[behavior_name]
   
   # calculate ensemble of tvalues for null distribution  
   tvalue_ensemble = []
   for shift_id in range(ensemble_size):
       # generate cyclic shifted time series
       shift_start_trial = np.random.randint(min_shift, high=len(behavior_ts)-min_shift)
       behavior_ts_cyclic_shift = np.concatenate((behavior_ts[shift_start_trial:],
                                                behavior_ts[:shift_start_trial]))
       results_OLS = simple_LR(fr_ts, behavior_ts_cyclic_shift, behavior_name)
       tvalue_ensemble.append(results_OLS.tvalues[behavior_name])
       
   percentile = sc.stats.percentileofscore(tvalue_ensemble, tvalue_target)
   return percentile


###########################################################################
### PARAMETRIC ERROR CORRECTION MODELS ###

def ARMA_model(
    fr_ts, 
    behavior_ts, 
    behavior_name, 
    AR_p=3, 
    MA_q=0
):
   """
   Fits an ARIMA (Autoregressive Integrated Moving Average) model to analyze the 
   relationship between neural firing rates and behavioral variables while accounting 
   for temporal autocorrelation.
   
   This function fits an ARIMA(p,0,q) model (equivalent to ARMA) where the firing rate 
   is the endogenous variable and behavior is the exogenous regressor. The model accounts 
   for temporal dependencies in the firing rate time series.
   
   Parameters
   ----------
   fr_ts : array-like
       Time series of neural firing rates (endogenous variable)
   behavior_ts : array-like
       Time series of behavioral variable (exogenous regressor)
   behavior_name : str
       Name of the behavioral variable being analyzed
   AR_p : int, optional (default=3)
       Order of the autoregressive component (number of AR lags)
   MA_q : int, optional (default=0)
       Order of the moving average component (number of MA lags)
       
   Returns
   -------
   statsmodels.tsa.arima.model.ARIMAResults
       Fitted ARIMA model results containing:
       - Model coefficients (AR, MA, and behavioral regression parameters)
       - Standard errors
       - Information criteria (AIC, BIC)
       - Model diagnostics
       - Residual analysis tools
       
   Notes
   -----
   The model specification:
   - Uses ARIMA(p,0,q) which is equivalent to ARMA(p,q)
   - Includes exogenous behavioral regressor
   - Default AR(3) specification based on common neural time series properties
   
   Assumptions:
   - Time series is approximately stationary
   - Temporal dependencies are captured by specified AR and MA orders
   - Residuals should be approximately white noise
   
   Examples
   --------
   >>> fr = np.array([1.2, 3.4, 2.1, 4.5, 3.2, 2.8])
   >>> behavior = np.array([0.1, 0.3, 0.2, 0.4, 0.3, 0.2])
   >>> results = ARMA_model(fr, behavior, 'speed', AR_p=2, MA_q=1)
   >>> print(results.summary())
   
   See Also
   --------
   statsmodels.tsa.arima.model.ARIMA : Underlying ARIMA model implementation
   """

   df_var_endo = pd.DataFrame({'fr': fr_ts})
   df_var_exog = pd.DataFrame({behavior_name: behavior_ts})
   X = df_var_exog
   armar_order = (AR_p, 0, MA_q)
   model_ARMA = sm.tsa.arima.ARIMA(df_var_endo, exog=X, order=armar_order)
   results_ARMA = model_ARMA.fit()
   
   return results_ARMA


def ARDL_model(fr_ts, behavior_ts, behavior_name, y_lag=5, x_order=0):
    '''
    fit ARDL model
    '''
    # make equal length
    min_session_len = min(len(fr_ts), len(behavior_ts))
    fr_ts = fr_ts[:min_session_len]
    behavior_ts = behavior_ts[:min_session_len]

    df_var_endo = pd.DataFrame({'fr': fr_ts})
    df_var_exog = pd.DataFrame({behavior_name: behavior_ts})
    X = df_var_exog

    model_ARDL = ARDL(df_var_endo, lags=y_lag, exog=X, order=x_order)
    results_ARDL = model_ARDL.fit()

    return results_ARDL

