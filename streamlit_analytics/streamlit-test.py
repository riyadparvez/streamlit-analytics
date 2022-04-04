import streamlit as st
from utils import StreamlitAnalytics

d = {
    "G": "Green",
    "Y": "Yellow",
    "R": "Red",
    "B": "Blue",
}

sa = StreamlitAnalytics(
    "analytics-test",
    True,
    db_uri="sqlite:////tmp/st.db",
)

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
        on_change=sa.get_on_change_func(
            "options",
        ),
    )

    st.write("You selected:", options)
    st.button(
        "Press me",
        key="button_val",
        on_click=sa.get_on_change_func(
            "button_val",
        ),
    )

    val = st.sidebar.slider(
        "select val",
        0,
        100,
        key="slider_slider",
        on_change=sa.get_on_change_func(
            "slider_slider",
        ),
    )

    if val > 50:
        file = st.file_uploader(
            "Please upload",
            key="file_uploader",
            on_change=sa.get_on_change_func(
                "file_uploader",
            ),
        )

        text_contents = st.text_input(
            "Just write something",
            key="text_contents",
            on_change=sa.get_on_change_func(
                "text_contents",
            ),
        )

        st.download_button(
            label="Download CSV",
            data=text_contents,
            mime="text/csv",
            file_name="CSV.csv",
            key="download_button",
            on_click=sa.get_on_change_func(
                "download_button",
            ),
        )
