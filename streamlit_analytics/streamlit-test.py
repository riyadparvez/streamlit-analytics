import streamlit as st
from utils import StreamlitAnalytics

d = {
    "G": "Green",
    "Y": "Yellow",
    "R": "Red",
    "B": "Blue",
}

sa = StreamlitAnalytics("analytics-test",)

with sa.track():
    options = st.multiselect(
        "What are your favorite colors",
        [
            "G",
            "Y",
            "R",
            "B",
        ],
        [
            "Y",
            "R",
        ],
        format_func=lambda x: d[x],
        key="options",
    )

    st.write("You selected:", options)
    st.button("Press me", key="button_val")

    val = st.slider("select val", 0, 100, key="slider_slider")

    file = st.file_uploader("PLease upload", key="file_uploader")

    text_contents = st.text_input("Just write something")

    st.download_button(
        label="Download CSV",
        data=text_contents,
        mime="text/csv",
        file_name="CSV.csv",
        key="download_button",
    )
