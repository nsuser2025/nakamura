import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
#from mkslide.main import mkslide_gui
from cielab.main import cielab_gui
from visco.kdvisco import kdvisco_gui
#from pic2xlsx.main import pic2xlsx_gui

st.image("zkanics_cute_logo.png", caption="Supported by Zkanics F. P. S. since 2024", width=250)
st.markdown("---")

select = ["MKSLIDE", "CIELAB", "KDVISCO", "PIC2XLSX"]
page = st.selectbox("計算を選択してください", select)
#if page == "MKSLIDE":
#   mkslide_gui ()
#elif page == "CIELAB":
if page == "CIELAB":
   cielab_gui ()
elif page == "KDVISCO":
   kdvisco_gui ()   
#elif page == "PIC2XLSX":
#   pic2xlsx_gui ()
else:
   pass
