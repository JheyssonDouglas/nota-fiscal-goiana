import streamlit as st
from dashboard.app import main

st.set_page_config(
    page_title="Nota Fiscal Goiana | Análise de Sorteios",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded",
)
main()
