import streamlit as st
import numpy as np
from scipy.signal import find_peaks

### INITIAL POINT ###
def ini_finder (wl_pos, wl_neg, vals_pos, vals_neg, wl_pos_range, wl_neg_range):

    if wl_pos_range[0] > wl_neg_range[0]:
       mask = wl_pos < 380
       if np.any(mask):
          nearest_idx_in_mask = np.argmax(wl_pos[mask])
          nearest_idx = np.where(mask)[0][nearest_idx_in_mask]
          wl_ini  = wl_pos[nearest_idx]
          vals_ini = vals_pos[nearest_idx]
       else:
          wl_ini = None
          vals_ini = None
    elif wl_neg_range[0] > wl_pos_range[0]:
       mask = wl_neg < 380
       if np.any(mask):
          nearest_idx_in_mask = np.argmax(wl_neg[mask])
          nearest_idx = np.where(mask)[0][nearest_idx_in_mask]
          wl_ini  = wl_neg[nearest_idx]
          vals_ini = vals_neg[nearest_idx]
       else:
          wl_ini = None
          vals_ini = None
         
    return wl_ini, vals_ini    
        
### MAXIMUM AND MINIMUM FINDER ###
def max_min_finder (wl, vals):
    peaks_pos, _ = find_peaks(vals)
    peaks_neg, _ = find_peaks(-vals)

    wl_pos = wl[peaks_pos]
    wl_neg = wl[peaks_neg]
    vals_pos = vals[peaks_pos]
    vals_neg = vals[peaks_neg]
    
    mask = (wl_pos >= 380) & (wl_pos <= 780)
    wl_pos_range = wl_pos[mask]
    vals_pos_range = vals_pos[mask]
    peaks_pos_range = peaks_pos[mask]

    mask = (wl_neg >= 380) & (wl_neg <= 780)
    wl_neg_range = wl_neg[mask]
    vals_neg_range = vals_neg[mask]
    peaks_neg_range = peaks_neg[mask]

    wl_ini, vals_ini = ini_finder (wl_pos, wl_neg, vals_pos, vals_neg, wl_pos_range, wl_neg_range)
    
    wl_all = np.concatenate([[wl_ini], wl_pos_range, wl_neg_range])
    vals_all = np.concatenate([[vals_ini], vals_pos_range, vals_neg_range])

    order = np.argsort(wl_all)
    wl_cast = wl_all[order]
    vals_cast = vals_all[order]

    return wl_cast, vals_cast

### LINEAR SPECTRUM GENERATOR ###
def linear_spectrum (wl_grid, vals_i, wl_maxmin, vals_maxmin):
    wl_mid = []
    vals_mid = []
    for i in range(len(wl_maxmin)-1):
        # wlの中間値から求める場合
        #wl_mid_value = 0.50 * (wl_maxmin[i] + wl_maxmin[i+1])
        #idx = np.argmin(np.abs(wl_grid - wl_mid_value))
        # valsの中間値から求める場合
        maxv = max(vals_maxmin[i], vals_maxmin[i+1])
        minv = min(vals_maxmin[i], vals_maxmin[i+1])
        vals_mid_value = minv + (0.50 * (maxv - minv))
        mask = (wl_grid >= wl_maxmin[i]) & (wl_grid <= wl_maxmin[i+1])
        idx = np.argmin(np.abs(vals_i[mask] - vals_mid_value))
        idx = np.where(mask)[0][idx]
        wl_mid += [wl_grid[idx]]
        vals_mid += [vals_i[idx]]
    wl_mid = np.array(wl_mid)
    vals_mid = np.array(vals_mid)

    ### CORRECTED SPECTRUM ###
    wl_calc = [] 
    vals_calc = []
    for ir in range(len(wl_mid)-1): 
        ### SLOPE AND INTERCEPT ###
        a = (vals_mid[ir+1] - vals_mid[ir]) / (wl_mid[ir+1] - wl_mid[ir])
        b = vals_mid[ir] - (a * wl_mid[ir])
        
        ### LINEAR SPECTRUM RANGE ###
        if ir == 0:
           wl_min = 380
           wl_max = wl_mid[1]
        elif ir == len(wl_mid) - 2:
           wl_min = wl_mid[ir]
           wl_max = 781
        else:
           wl_min = wl_mid[ir]
           wl_max = wl_mid[ir+1]
            
        ### CORRECTED SPECTRUM IN RANGE ###
        for i in range(380, 781, 1):
            if i >= wl_min and i < wl_max:
               wl_calc += [i] 
               vals_calc += [(a*i) + b] 

        ### --> wl_cast, vals_cast ###
        wl_cast = np.array(wl_calc)
        vals_cast = np.array(vals_calc)

    return wl_cast, vals_cast

### LINEAR SPECTRUM GENERATOR VER.2 2026/03/17 ###
def linear_spectrum_ver2 (wl_grid, vals_i, wl_inflect, vals_inflect, wl_maxmin, vals_maxmin):
    wl_mid = []
    vals_mid = []
    for i in range(len(wl_maxmin)-1):
        # wlの中間値から求める場合
        #wl_mid_value = 0.50 * (wl_maxmin[i] + wl_maxmin[i+1])
        #idx = np.argmin(np.abs(wl_grid - wl_mid_value))
        # valsの中間値から求める場合
        maxv = max(vals_maxmin[i], vals_maxmin[i+1])
        minv = min(vals_maxmin[i], vals_maxmin[i+1])
        vals_mid_value = minv + (0.50 * (maxv - minv))
        mask = (wl_grid >= wl_maxmin[i]) & (wl_grid <= wl_maxmin[i+1])
        idx = np.argmin(np.abs(vals_i[mask] - vals_mid_value))
        idx = np.where(mask)[0][idx]
        wl_mid += [wl_grid[idx]]
        vals_mid += [vals_i[idx]]
    wl_mid = np.array(wl_mid)
    vals_mid = np.array(vals_mid)

    # INFLECTION 2026/03/17 START
    wl_inflect = np.array(wl_inflect)
    vals_inflect = np.array(vals_inflect)
    filtered = wl_inflect[wl_inflect < 380]
    if len(filtered) > 0:
       wl_target = filtered.max()
       idx = np.where(wl_inflect == wl_target)[0][0]
    else:
       # fallback（380に一番近い値）
       idx = np.abs(wl_inflect - 380).argmin()
       wl_target = wl_inflect[idx]
    vals_target = vals_inflect[idx]
    wl_mid[0] = wl_target
    vals_mid[0] = vals_target
    # INFLECTION 2026/03/17 END
    
    ### CORRECTED SPECTRUM ###
    wl_calc = [] 
    vals_calc = []
    for ir in range(len(wl_mid)-1): 
        ### SLOPE AND INTERCEPT ###
        a = (vals_mid[ir+1] - vals_mid[ir]) / (wl_mid[ir+1] - wl_mid[ir])
        b = vals_mid[ir] - (a * wl_mid[ir])
        
        ### LINEAR SPECTRUM RANGE ###
        if ir == 0:
           wl_min = 380
           wl_max = wl_mid[1]
        elif ir == len(wl_mid) - 2:
           wl_min = wl_mid[ir]
           wl_max = 781
        else:
           wl_min = wl_mid[ir]
           wl_max = wl_mid[ir+1]
            
        ### CORRECTED SPECTRUM IN RANGE ###
        for i in range(380, 781, 1):
            if i >= wl_min and i < wl_max:
               wl_calc += [i] 
               vals_calc += [(a*i) + b] 

        ### --> wl_cast, vals_cast ###
        wl_cast = np.array(wl_calc)
        vals_cast = np.array(vals_calc)

    return wl_cast, vals_cast

# MODULE ERROR MESSAGE
if __name__ == "__main__":
   raise RuntimeError("Do not run this file directly; use it as a module.")
