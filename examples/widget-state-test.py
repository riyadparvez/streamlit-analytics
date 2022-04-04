from __future__ import annotations
import streamlit as st
from loguru import logger
from typing import Any

from objprint import config, op, install
from streamlit_analytics import *

install()
config(
    line_number=True,
    arg_name=True,
)

temperature_key = "temperature"
humidity_key = "humidity"

default_vals: dict[str, Any] = {
    temperature_key: 50.0,
    humidity_key: 20.0,
}


def f():
    print("========================")
    print("boys boys")
    print("========================")


application_name = "analytics-test"
sa = StreamlitAnalytics(application_name, True, default_vals, db_uri="sqlite:////tmp/st.db", firestore_collection_name=application_name)

with sa.track():
    # with track("analytics-test", default_vals):
    temperature = st.slider(
        "Temperature",
        min_value=-100.0,
        max_value=100.0,
        key=temperature_key,
        on_change=sa.get_on_change_func(temperature_key, f),
    )

    humidity = st.slider(
        "Relative Humidity",
        min_value=0.0,
        max_value=100.0,
        key=humidity_key,
        on_change=sa.get_on_change_func(humidity_key, f),
    )
