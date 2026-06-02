import streamlit as st
import io
import pandas as pd
import numpy as np
from typing import List
from PIL import Image
from .mkcsv import mkcsv_gui
from .mkcsv import sanitize_for_csv_injection
from .cielab import cielab_core
from .document import cielab_overview

def cielab_gui():

    # EXPLANATIONS
    st.markdown("#### CIE Lab変換")
    st.markdown(r"""透過率/反射率スペクトルのCIE L$^{*}$a$^{*}$b$^{*}$変換アプリです.
    標準光源D65およびCIE1931等色関数に基づき, 透過光/反射光の知覚色を近似的に表示します.
    表示色は実際の観察条件下で見える色を正確に再現するものではありません.
    アップロードするエクセルファイルは, 奇数列には波長, 偶数列にはスペクトルデータを記載してください.
    ヘッダー行や文字列が含まれていたり, 列数が奇数の場合は正しく実行されません.
    黄色度の計算も可能ですが, 透過率スペクトルでは黄色度は意味を持たないため, 反射率スペクトルの場合のみ計算されます.
    このアプリにアップロードした情報は全てメモリ上に保存されます.
    セッションの終了と同時にサーバー上のスペクトル情報は完全に消去されます.
    また, 出力されるCSVにはコードインジェクションの無効化処理が施されています.
    安心してダウンロードしてください.""") 
    cielab_overview()
    st.markdown("---")
    
    # INITIALIZE SESSIONS
    if 'data_df' not in st.session_state:
        st.session_state.data_df = None
    if 'condition_count' not in st.session_state:
        st.session_state.condition_count = 1
        
    # CSV FILE READER
    uploaded_file = st.file_uploader("透過率スペクトルのExcel/CSVファイルをアップロード", 
                    type=["xlsx", "xls", "xlsm", "csv"])
    
    st.markdown("---")
    bool_maxmin = st.radio("最大値・最小値を表示しますか？", ["on", "off"], horizontal=True)
    YI_option = st.radio("黄色度式", ["D65光源", "C光源"], horizontal=True)
    st.markdown("---")

    if uploaded_file:
       df = mkcsv_gui(uploaded_file)
       ### ERROR MESSAGES ###
       if df.shape[1] < 2:
          st.error("波長・スペクトルのペアになっていません")
          st.stop()
       if df.shape[1] % 2 != 0:
          st.error("列数が奇数です（波長・スペクトルのペアになっていません）")
          st.stop()
       ### CIELAB ### 
       st.session_state.data_df = df
       st.markdown("---")
       L_w, a_w, b_w = 100, 0, 0 
       name_vals = [] 
       L_vals = []
       a_vals = []
       b_vals = []
       YI_vals = []
       for i in range(0, df.shape[1], 2):
           name = df.columns[i+1]
           st.markdown(f"<div style='font-size:1.0rem; font-weight:600; margin-bottom:0.3rem;'>"
                       f"実測スペクトル: {name}</div>",unsafe_allow_html=True)
           wl = df.iloc[:, i]
           spec = df.iloc[:, i+1]
           df_pair = pd.DataFrame({"wl": wl,"spec": spec})
           Li, ai, bi, YI, = cielab_core (bool_maxmin, YI_option, df_pair)
           name_vals += [name]
           L_vals += [Li]
           a_vals += [ai]
           b_vals += [bi]
           YI_vals += [YI]
       st.markdown("---")
       name_vals = np.array(name_vals)    
       L_vals = np.array(L_vals)
       a_vals = np.array(a_vals)
       b_vals = np.array(b_vals) 
       YI_vals = np.array(YI_vals) 
       DYI_vals = YI_vals-YI_vals[0] 
       dist_w = np.sqrt((L_vals - L_w)**2 + (a_vals - a_w)**2 + (b_vals - b_w)**2)
       df_lab = pd.DataFrame({"name": name_vals, "L*": L_vals, "a*": a_vals, "b*": b_vals,
                              "YI": YI_vals, "Delta YI": DYI_vals, 
                              "Distance_to_ideal_white": dist_w})
       df_lab_safe = sanitize_for_csv_injection(df_lab) 
       st.dataframe(df_lab_safe) 
    
    df = st.session_state.data_df
    if df is None:
       st.info("データファイル（CSV）をアップロードしてください。")
       return
    
    st.markdown("---")

# MODULE ERROR MESSAGE
if __name__ == "__main__":
   raise RuntimeError("Do not run this file directly; use it as a module.")
