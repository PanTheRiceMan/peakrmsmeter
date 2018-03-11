# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 19:34:43 2018

@author: PanTheRiceMan
"""

from __future__ import division
import librosa
import matplotlib
import numpy as np
from numpy import pi, polymul
from scipy.signal import bilinear, lfilter
import os
import time
import warnings
import argparse

#==============================================================================
# data cursor, optional dependency
#==============================================================================
cursor=True
try:
    from mpldatacursor import datacursor
except:
    cursor=False

#==============================================================================
# ignore warnings. Only for divide by zero in numpy.log10
#==============================================================================
warnings.filterwarnings("ignore")

def AWeights(fs):
    """Design of an A-weighting filter.
    b, a = A_weighting(fs) designs a digital A-weighting filter for
    sampling frequency `fs`. Usage: y = scipy.signal.lfilter(b, a, x).
    Warning: `fs` should normally be higher than 20 kHz. For example,
    fs = 48000 yields a class 1-compliant filter.
    References:
       [1] IEC/CD 1672: Electroacoustics-Sound Level Meters, Nov. 1996.
    Source: https://gist.github.com/endolith/148112
    """
    # Definition of analog A-weighting filter according to IEC/CD 1672.
    f1 = 20.598997
    f2 = 107.65265
    f3 = 737.86223
    f4 = 12194.217
    A1000 = 1.9997

    NUMs = [(2*pi * f4)**2 * (10**(A1000/20)), 0, 0, 0, 0]
    DENs = polymul([1, 4*pi * f4, (2*pi * f4)**2],
                   [1, 4*pi * f1, (2*pi * f1)**2])
    DENs = polymul(polymul(DENs, [1, 2*pi * f3]),
                                 [1, 2*pi * f2])

#==============================================================================
#     Use the bilinear transformation to get the digital filter.
#==============================================================================
    return bilinear(NUMs, DENs, fs)

def reduceToPeak(a, fs, windowsize=200, forwardsize=50):
    """
    Reduced array with max peak pooling within <windowsize> ms. Calculated every 
    <forwardsize> milliseconds.
    
    Parameters
    ----------
    a : numpy.array
        Input array containing the data
    fs : int
        Sampling rate
    windowsize : int, optional
        Window size for peak pooling in [ms], default=200 ms
    forwardsize : int, optional
        Forward size. Calculate a window every <forwardsize> ms. Default=50 ms
    
    Returns
    -------
    reduced : np.array
        Reduced arrary containing max pooled peaks
    """
    reduced = []
    window = int((windowsize/1000) * fs)
    windowfwd = int((forwardsize/1000) * fs)
    cursor = 0
    while len(a) >= cursor + windowfwd:
        reduced.append(np.max(np.abs(a[max(0,int(cursor-window/2)):int(cursor+window/2)])))
        cursor += windowfwd
    return np.array(reduced)

def toRms(a, fs, windowsize=2000, forwardsize=50):
    """
    Calculate RMS within a window of <windowsize> ms. Calculated every 
    <forwardsize> milliseconds. A window of 2000 ms is used by default.
    A empirically determinded tradeoff between smoothness / accuraccy.
    
    Parameters
    ----------
    a : numpy.array
        Input array containing the data
    fs : int
        Sampling rate
    windowsize : int, optional
        Window size RMS calculation in [ms], default=2000 ms
    forwardsize : int, optional
        Forward size. Calculate a window every <forwardsize> ms. Default=50 ms
    
    Returns
    -------
    rms : np.array
        Array containing RMS values
    """
    rms = []
    window = int((windowsize/1000) * fs)
    windowfwd = int((forwardsize/1000) * fs)
    cursor = 0
    while len(a) >= cursor + windowfwd:
        rms.append(np.sqrt(np.mean(np.absolute(a[max(0,int(cursor-window/2)):int(cursor+window/2)])**2)))
        cursor += windowfwd
    return np.array(rms)

def toDb(a):
    return 20*np.log10(a)

if __name__ == "__main__":

#==============================================================================
# argument parser for input
#==============================================================================
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("path", metavar="<path>", type=str,\
                        help="Path to audio file")
    parser.add_argument("--noplot", action="store_const",\
                        const=True, default=False,\
                        help="Don't show plots.")
    parser.add_argument("--silent", action="store_const",\
                        const=True, default=False,\
                        help="Don't show plots.")
    parser.add_argument("--hist", action="store_const",\
                        const=True, default=False,\
                        help="Show histograms for RMS and peak")
    parser.add_argument("--datacursor", action="store_const",\
                        const=True, default=False,\
                        help="Add datacursor, enabling display of values on click")
    parser.add_argument("--savefig", action="store_const", const=True,\
                        default=False,\
                        help="Save figure. Default name=figure.pdf")
    parser.add_argument("--out", metavar="<path>", type=str, default="figure.pdf",\
                        help="Output path and file name with extension for pictures.")
    args = parser.parse_args()
    if cursor:
        cursor = args.datacursor

#==============================================================================
#    use Agg backend when not drawing plots but saving only
#    works when no display output is available, like one a server without X
#    or Wayland (Linux).
#==============================================================================
    if args.noplot:
        matplotlib.use('Agg')

#==============================================================================
#     import pyplot after choosing the backend so it will work without visual
#     output, too
#==============================================================================
    import matplotlib.pyplot as plt
    
#==============================================================================
#     use a dark background, because fancy and professional
#==============================================================================
    plt.style.use('dark_background')

#==============================================================================
#     basename for display in plot titles
#==============================================================================
    bn = os.path.basename(args.path)

#==============================================================================
# load audio file
#==============================================================================
    y, sr = librosa.load(args.path, sr=None, mono=True)

#==============================================================================
#     calculate peaks in dB
#==============================================================================
    yPeak = reduceToPeak(y, sr)
    yDb = toDb(np.abs(yPeak))
    
#==============================================================================
#     calculate RMS in dB
#==============================================================================
    rms = toRms(y, sr)
    rmsDb = toDb(rms)
    
    b, a = AWeights(sr)
    yA = lfilter(b, a, y)
    rmsA = toRms(yA, sr)
    rmsADb = toDb(rmsA)
    
#==============================================================================
#     calculate times for display
#==============================================================================
    x = np.linspace(0, len(y)/sr, len(yDb))
    xrms = np.linspace(0, len(y)/sr, len(rms))
    
#==============================================================================
#     formatter for time and dB
#==============================================================================
    formatterDB = matplotlib.ticker.FuncFormatter(lambda x, s: round(toDb(x),2))
    formatterTime = matplotlib.ticker.FuncFormatter(lambda x, s: time.strftime('%M:%S', time.gmtime(x)))

#==============================================================================
#     histogram of peaks and rms
#==============================================================================
    if args.hist and not args.noplot:
        plt.figure(figsize = (21.3,12))
        ax = plt.subplot(111)
        plt.title("Peaks: {}".format(bn))
        plt.hist(yPeak, bins = 512, normed=True)
        plt.xlim(0,1)
        ax.xaxis.set_major_formatter(formatterDB)
        plt.xlabel("dBFS")
        plt.ylabel("Density [percent]")
        
        plt.figure(figsize = (21.3,12))
        ax = plt.subplot(111)
        plt.title("RMS, a-weighted: {}".format(bn))
        plt.hist(rmsA, bins = 512, normed=True)
        plt.xlim(0,0.5)
        ax.xaxis.set_major_formatter(formatterDB)
        plt.xlabel("dBFS")
        plt.ylabel("Density [percent]")
    
#==============================================================================
#     calculation of percentiles for rough estimate of peak to average values
#==============================================================================
    rmsPercentileLower = np.percentile(rmsA, 25)
    rmsPercentileUpper = np.percentile(rmsA, 50)
    
    peakPercentileUpper = np.percentile(yPeak, 80)
    
    meanRms50Percent = toDb(np.mean(rmsA[np.where(np.logical_and(rmsA>rmsPercentileLower,\
                                        rmsA<=rmsPercentileUpper))]))
    meanPeak80Percent = toDb(np.mean(yPeak[np.where(yPeak >= peakPercentileUpper)]))
    
    meanRmsA = toDb(np.mean(rmsA))
    meanPeak = toDb(np.mean(yPeak))
    
#==============================================================================
#   some additional information, my own interpretation on a peak to average
#   meter. Can not be compared to any other meter.
#   Since the histograms of peaks are no default distribution, except the peak
#   histogram, which can be something like laplacian, percentiles are used to
#   determine the mean rms. Everything above or equal to the 80% percentile
#   is used for peaks.
#==============================================================================
    if not args.silent:
        print("mean Peak:                    ",meanPeak, "dB")
        print("mean Peak 80%:                ", meanPeak80Percent, "dB")
        print("mean rmsA:                    ",meanRmsA, "dB")
        print("mean rmsA 50%:                ", meanRms50Percent, "dB")
        print("peak to average:              ",meanPeak - meanRmsA, "dB A-weighted")
        print("peak to average (percentiles):",meanPeak80Percent-meanRms50Percent, "dB A-weighted")

#==============================================================================
#    peak and rms meter    
#==============================================================================
    plt.figure(figsize = (21.3,12))
    ax = plt.subplot(111)
    plt.title(bn)
    linesPeak = plt.plot(x, yDb, label="peaks [dB]", linewidth=0.5)
    linesRms = plt.plot(xrms, rmsDb, label="rms, unweighted", linewidth=2.0)
    linesRmsA = plt.plot(xrms, rmsADb, label="rms, A-weighted", linewidth=2.0)
    plt.ylim(-40,1)
    plt.xlabel("Time [MM:SS]")
    plt.ylabel("dBFS")
    plt.legend()
    ax.xaxis.set_major_formatter(formatterTime)
    plt.grid()
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95,\
                wspace=None, hspace=None)

#==============================================================================
#     cursor, because fancy
#==============================================================================
    if cursor:
        datacursor(display='multiple', draggable=False)
    
    if not args.noplot:
        plt.show()
        
    if args.savefig:
        plt.savefig(args.out)
    
    
