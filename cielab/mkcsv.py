import streamlit as st
import string
import pandas as pd
from openpyxl import load_workbook
import os
import re

# ================================
# CSV インジェクション防止
# ================================
def sanitize_for_csv_injection(df):
    """
    CSVインジェクションを防止:
    = + - @ で始まるセルに ' を付加して無効化する
    """
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.replace(r'^([=+\-@])', r"'\1", regex=True)
            )
    return df

# ================================
# メイン GUI
# ================================
def mkcsv_gui(uploaded_file):

    # --- ファイルサイズ制限（20MB） ---
    uploaded_file.seek(0, os.SEEK_END)
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)

    if file_size > 20 * 1024 * 1024:
        st.error("⚠ ファイルサイズが20MBを超えています。処理を中止します。")
        return None

    file_name = uploaded_file.name.lower()

    is_csv = file_name.endswith(".csv")
    is_excel = file_name.endswith((".xlsx", ".xls", ".xlsm"))

    if not (is_csv or is_excel):
        st.error("対応形式は CSV または Excel ファイルのみです。")
        return None

    # ====================================
    # Excel の場合
    # ====================================
    if is_excel:
        try:
            df_orig = pd.read_excel(uploaded_file, header=None)
        except Exception as e:
            st.error(f"Pandas による Excel 読み込みエラー: {e}")
            return None

    # ====================================
    # CSV の場合
    # ====================================
    else:
        try:
            df_orig = pd.read_csv(uploaded_file, header=None, encoding="utf-8")
        except Exception:
            try:
                df_orig = pd.read_csv(uploaded_file, header=None, encoding="shift_jis")
            except Exception as e:
                st.error(f"CSV 読み込みエラー: {e}")
                return None

    # ====================================
    # 読み込んだデータの表示
    # ====================================
    df_orig.columns = list(string.ascii_uppercase[:len(df_orig.columns)])
    df_orig.index = range(1, len(df_orig) + 1)

    df_safe = sanitize_for_csv_injection(df_orig.copy())
    df_safe.columns = df_safe.columns.map(str)

    st.dataframe(df_safe)
    st.markdown("---")

    st.success("読み込み完了しました。")
    return df_orig


# MODULE ERROR MESSAGE
if __name__ == "__main__":
    raise RuntimeError("Do not run this file directly; use it as a module.")
