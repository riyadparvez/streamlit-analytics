import streamlit as st
from streamlit_analytics import StreamlitAnalytics

d = {
    "G": "Green",
    "Y": "Yellow",
    "R": "Red",
    "B": "Blue",
}

application_name = "analytics-test"
sa = StreamlitAnalytics(
    application_name,
    True,
    db_uri="sqlite:////tmp/st.db",
    firestore_collection_name=application_name,
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
