import streamlit as st

def cielab_overview():
    
    with st.expander("CIE L$^{*}$a$^{*}$b$^{*}$変換の概要"):
         st.markdown(r"""色の見え方を定量的に扱うために, 色を色空間上の座標として表す方法が用いられます.  
                         CIE L$^{*}$a$^{*}$b$^{*}$空間では「座標間距離 $\approx$ 人間が感じる色差」
                         が成り立つように設計されています（知覚均等色空間）.""")
         st.markdown(r"""L$^{*}$（明度）: 0–100  
                         a$^{*}$：赤（＋）$\leftrightarrow$ 緑（−）  
                         b$^{*}$：黄（＋）$\leftrightarrow$ 青（−）""")
         st.markdown(r"""L$^{*}$=0 $\cdots$ 完全な黒  
                         L$^{*}$=100, a$^{*}$=b$^{*}$=0 $\cdots$ 理論上の最大明度（理想的な白）  
                         L$^{*}$=100, a$^{*}$, b$^{*}$≠0 $\cdots$ 理論上の最大明度（色味が残る）""")
         st.markdown(r"""本アプリでは透過率/反射率スペクトルの波長領域を380–780 nmに限定しています.  
                         これは, 380 nm未満, 780 nmを超える波長は人間が色として知覚できないためです.""")
         st.markdown(r"""参考として刺激値色空間の座標X, Y, Zも出力しますが, CIE L$^{*}$a$^{*}$b$^{*}$空間とは対照的に  
                        「座標間距離 $\approx$ 人間が感じる色差」は成り立ちません.""")

    with st.expander("CIE XYZ変換の計算式"):
         st.latex(r"L^{\ast} = 116 F(Y/Y_{\rm n}) - 16")
         st.latex(r"a^{\ast} = 500 ( F(X/X_{\rm n}) - F(Y/Y_{\rm n}))")
         st.latex(r"b^{\ast} = 200 ( F(Y/Y_{\rm n}) - F(Z/Z_{\rm n}))")
        
    with st.expander("CIE L$^{*}$a$^{*}$b$^{*}$変換の計算式"):
         st.latex(r"L^{\ast} = 116 F(Y/Y_{\rm n}) - 16")
         st.latex(r"a^{\ast} = 500 ( F(X/X_{\rm n}) - F(Y/Y_{\rm n}))")
         st.latex(r"b^{\ast} = 200 ( F(Y/Y_{\rm n}) - F(Z/Z_{\rm n}))")
         st.latex(r"""F(t) =
                  \begin{cases}
                         t^{1/3}, & t > \delta^{3} \\
                         \frac{1}{3\delta^{2}} t + \frac{4}{29}, & t \leq \delta^{3}
                  \end{cases}""")
         st.latex(r"\delta \equiv (6/29)")
    
    with st.expander("黄色度（Yellow Index, YI）の計算式"):
         st.markdown(r"""D65光源""")
         st.latex(r"YI = 100 (1.3013X - 1.1498Z) / Y")
         st.markdown(r"""C光源""") 
         st.latex(r"YI = 100 (1.2985X - 1.1335Z) / Y")
              
        
# MODULE ERROR MESSAGE
if __name__ == "__main__":
   raise RuntimeError("Do not run this file directly; use it as a module.")
