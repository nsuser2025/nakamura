import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
from cielab.main import cielab_gui

st.image("zkanics_cute_logo.png", caption="Supported by Zkanics F. P. S. since 2024", width=250)
st.markdown("---")

select = ["CIELAB"]
page = st.selectbox("計算を選択してください", select)
if page == "CIELAB":
   cielab_gui ()
else:
   pass
