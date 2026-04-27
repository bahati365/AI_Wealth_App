import streamlit as st
from src.ui import render_sidebar, render_recommendation

st.set_page_config(page_title="Wealth Advisor", layout="wide")

st.title("AI Wealth Advisor")
st.write("Answer a few questions to generate a sample portfolio recommendation.")

profile, generate = render_sidebar()

if "generated_profile" not in st.session_state:
    st.session_state.generated_profile = None

if generate:
    st.session_state.generated_profile = profile

if st.session_state.generated_profile is not None:
    render_recommendation(st.session_state.generated_profile)
else:
    st.info("Fill out the sidebar and click Generate Portfolio.")
    