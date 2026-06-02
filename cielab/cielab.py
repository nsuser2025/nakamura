import streamlit as st
import os
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d, UnivariateSpline
import matplotlib.pyplot as plt
from .nakamura import max_min_finder, linear_spectrum_ver2

### INPUT df --> wl, vals ###
def load_measurements (df):
    wl = df.iloc[:,0].to_numpy(dtype=float)
    vals = df.iloc[:,1].to_numpy(dtype=float)
    ### sort ascending by wavelength ###
    order = np.argsort(wl)
    return wl[order], vals[order]

### XYZ --> linear RGB ###
def xyz_to_linear_rgb (X, Y, Z):
    ### sRGB D65 ###
    M = np.array([[ 3.2406, -1.5372, -0.4986],
                  [-0.9689,  1.8758,  0.0415],
                  [ 0.0557, -0.2040,  1.0570]])
    XYZ = np.array([X, Y, Z]) / 100
    RGB = M.dot(XYZ) 
    return RGB

### LINEAR RGB --> sRGB ###
def linear_to_srgb (RGB):
    def compand(c):
        c = np.clip(c, 0, 1)
        return np.where(c <= 0.0031308,
                        12.92 * c,
                        1.055 * c**(1/2.4) - 0.055)
    return compand(RGB)

### DELTA FOR NUMERICAL INTEGRAL ###
def compute_deltas (wl):
    dw = np.diff(wl)
    if dw.size == 0:
        return np.array([1.0])
    if np.allclose(dw, dw[0]):
        return np.full_like(wl, dw[0], dtype=float)
    deltas = np.empty_like(wl, dtype=float)
    deltas[0] = wl[1] - wl[0]
    deltas[-1] = wl[-1] - wl[-2]
    deltas[1:-1] = 0.5 * (wl[2:] - wl[:-2])
    return deltas

### CIE F FUNCTION ###
def f_lab (t):
    delta = 6.0 / 29.0
    delta2 = delta * delta
    delta3 = delta2 * delta
    if t > delta3:
        return t**(1/3)
    else:
        return (t / (3 * delta2)) + (4.0 / 29.0)

### CIE LAB FOR REFLECTANCE ###
def spectrum_to_lab_refle (wl_vis, vals_vis, df_xyz, df_ill, assume_percent=True):
    
    ### CONVERT PERCENT 0 <= REFLECTANCE <= 1 ###
    spec = vals_vis.copy().astype(float)
    if assume_percent:
       spec = spec / 100.0
    
    # INTERPOLATE CIE FUNCTIONS
    fx_bar = interp1d (df_xyz['wl'], df_xyz['xbar'], bounds_error=False, fill_value=0.0)
    fy_bar = interp1d (df_xyz['wl'], df_xyz['ybar'], bounds_error=False, fill_value=0.0)
    fz_bar = interp1d (df_xyz['wl'], df_xyz['zbar'], bounds_error=False, fill_value=0.0)
    fs = interp1d (df_ill['wl'], df_ill['S'], bounds_error=False, fill_value=0.0)

    # --> CIE FUNCTIONS
    xbar = fx_bar (wl_vis)
    ybar = fy_bar (wl_vis) 
    zbar = fz_bar (wl_vis)
    s = fs (wl_vis)

    ### GRID SETTING ###
    deltas = compute_deltas (wl_vis)

    ### NORMALIZATION CONSTANT ###
    denom = np.sum(s * ybar * deltas)
    if denom <= 1e-12:
       st.error("ZKANICS ERROR CIELAB.py (ZERO DENOM)")
       st.stop()
    k = 100.0 / denom

    ### --> X, Y, Z
    X = k * np.sum(spec * s * xbar * deltas)
    Y = k * np.sum(spec * s * ybar * deltas)
    Z = k * np.sum(spec * s * zbar * deltas)

    ### WHITEPOINT (R=1, perfect reflecting diffuser) ###
    Xn = k * np.sum(1.0 * s * xbar * deltas)
    Yn = k * np.sum(1.0 * s * ybar * deltas)
    Zn = k * np.sum(1.0 * s * zbar * deltas)

    ### --> L*, a*, b*
    fx = f_lab (X / Xn)
    fy = f_lab (Y / Yn)
    fz = f_lab (Z / Zn)
    L = (116.0 * fy) - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)

    return {"X":X, "Y":Y, "Z":Z, "L":L, "a":a, "b":b, "k":k, "white":{"Xn":Xn,"Yn":Yn,"Zn":Zn}}

### CIE LAB FOR TRANSMITTANCE ###
def spectrum_to_lab_trans (wl_vis, vals_vis, df_xyz, df_ill, assume_percent=True):
    
    ### CONVERT PERCENT 0 <= TRANSMITTANCE <= 1 ###
    spec = vals_vis.copy().astype(float)
    if assume_percent:
       spec = spec / 100.0
    
    # INTERPOLATE CIE FUNCTIONS
    fx_bar = interp1d (df_xyz['wl'], df_xyz['xbar'], bounds_error=False, fill_value=0.0)
    fy_bar = interp1d (df_xyz['wl'], df_xyz['ybar'], bounds_error=False, fill_value=0.0)
    fz_bar = interp1d (df_xyz['wl'], df_xyz['zbar'], bounds_error=False, fill_value=0.0)
    fs = interp1d (df_ill['wl'], df_ill['S'], bounds_error=False, fill_value=0.0)

    # --> CIE FUNCTIONS
    xbar = fx_bar (wl_vis)
    ybar = fy_bar (wl_vis)
    zbar = fz_bar (wl_vis)
    s = fs (wl_vis)

    ### GRID SETTING ###
    deltas = compute_deltas (wl_vis)

    ### NORMALIZATION CONSTANT ###
    denom = np.sum(s * ybar * deltas)
    if denom <= 1e-12:
       st.error("ZKANICS ERROR CIELAB.py (ZERO DENOM)")
       st.stop()
    k = 100.0 / denom

    ### --> X, Y, Z
    X = k * np.sum(spec * s * xbar * deltas)
    Y = k * np.sum(spec * s * ybar * deltas)
    Z = k * np.sum(spec * s * zbar * deltas)

    ### WHITEPOINT (T=1, no sample) ###
    Xn = k * np.sum(s * xbar * deltas)
    Yn = k * np.sum(s * ybar * deltas)
    Zn = k * np.sum(s * zbar * deltas)

    ### --> L*, a*, b*
    fx = f_lab (X / Xn)
    fy = f_lab (Y / Yn)
    fz = f_lab (Z / Zn)
    L = (116.0 * fy) - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)

    return {"X":X, "Y":Y, "Z":Z, "L":L, "a":a, "b":b, "k":k, "white":{"Xn":Xn,"Yn":Yn,"Zn":Zn}}

### CIE MAIN PART ###
def cielab_core (bool_maxmin, YI_option, df):
   
    base_dir = os.path.dirname(__file__)
    xyz_path = os.path.join(base_dir, "CIE_xyz_1931_2deg.csv")
    ill_path = os.path.join(base_dir, "CIE_std_illum_D65.csv")
    df_xyz = pd.read_csv(xyz_path, header=None, names=["wl", "xbar", "ybar", "zbar"])
    df_ill = pd.read_csv(ill_path, header=None, names=["wl", "S"])
    
    wl, vals = load_measurements (df)

    ### RESTRICT TO 300-1000 NM ###
    mask = (wl >= 300.0) & (wl <= 1000.0)
    wl_vis = wl[mask]
    vals_vis = vals[mask]
    if wl_vis.size == 0:
       st.error("ZKANICS ERROR CIELAB.py (NO DATA IN VISIBLE RANGE)")
       st.stop()
    wl_grid = np.arange(300.0, 1001.0, 1.0)
    cs = UnivariateSpline (wl_vis, vals_vis, k=3, s=2)
    
    # ADD START 2026/03/13 START
    cs2 = cs.derivative(n=2)
    y2 = cs2(wl_grid)
    idx = np.where(np.diff(np.sign(y2)))[0]
    wl_inflect = wl_grid[idx]
    vals_inflect = cs(wl_inflect)
    # ADD END 2026/03/13 END
    
    vals_i = cs(wl_grid)
    vals_i = np.clip(vals_i, 0.0, 100.0)
    wl_maxmin, vals_maxmin = max_min_finder (wl_grid, vals_i)
    # CHANGE 2026/03/17 START
    # wl_i_clean, vals_i_clean = linear_spectrum (wl_grid, vals_i, wl_maxmin, vals_maxmin)
    wl_i_clean, vals_i_clean = linear_spectrum_ver2 (wl_grid, vals_i, wl_inflect, vals_inflect, wl_maxmin, vals_maxmin)
    # CHANGE 2026/03/17 END
    
    ### XYZ --> LAB (MAIN) ###
    res = spectrum_to_lab_trans (wl_i_clean, vals_i_clean, df_xyz, df_ill, assume_percent=True)
    
    ### XYZ --> RGB ###
    X, Y, Z = res["X"], res["Y"], res["Z"]
    linear_rgb = xyz_to_linear_rgb (X, Y, Z)
    srgb = linear_to_srgb (linear_rgb)

    ### YELLOW INDEX (D65) ###
    if YI_option == "D65光源" and Y > 1e-6:
       YI = 100 * ((1.3013 * X) - (1.1498 * Z)) / Y 
    ### ILLUMINANT C ###     
    elif YI_option == "C光源" and Y > 1e-6:
       YI = 100 * ((1.2985 * X) - (1.1335 * Z)) / Y 
    else:
       YI = None
    
    ### FIGURE PLOT ###
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axvline(380, linestyle="--", color="violet", lw=1)
    ax.axvline(780, linestyle="--", color="red", lw=1)
    ax.plot(wl_grid, vals_i, lw=2, label="Interpolated")
    ax.plot(wl_i_clean, vals_i_clean, lw=2, c="blue", label="Corrected")
    if bool_maxmin == 'on':
       ax.plot(wl_maxmin, vals_maxmin, "go", label="Max and Minimum points for Correction")
    ax.plot(wl_vis, vals_vis, lw=1, marker="o", ms=2, label="Measured") 
    # ADD START 2026/03/13
    mask = wl_inflect <= 780
    ax.plot(wl_inflect[mask], vals_inflect[mask], "ro", ms=6, label="Inflection points")
    # ADD END 2026/03/13
    ax.legend()
    ax.set_xlabel("Wavelength [nm]")
    ax.set_ylabel("Transmittance / Reflectance [%]")
    ax.set_xlim(300, 1000)
    ax.set_ylim(0, 100)
    ax.grid(True)

    ### RESULTS ###
    col_text, col_plot, col_color = st.columns([2, 1, 1])
    with col_text:
         if YI is not None:
            st.write("L*, a*, b* = {:.2f}, {:.2f}, {:.2f}".format(res["L"], res["a"], res["b"]))
            st.write("Yellow Index = {:.3f}".format(YI))
    with col_plot:
         st.pyplot(fig)
    with col_color:
         r, g, b_ = (srgb * 255).astype(int)
         st.markdown(f"""<div style="width:100%;height:150px;background-color: rgb({r},{g},{b_});
                     border: 3px solid gray;border-radius: 20px;
                     "></div>""",unsafe_allow_html=True)
    
    ### FINAL ACTION ###
    return res["L"], res["a"], res["b"], YI
    
# MODULE ERROR MESSAGE
if __name__ == "__main__":
   raise RuntimeError ("Do not run this file directly; use it as a module.")
