from functools import partial
import streamlit as st
import sys
import uuid

from contextlib import contextmanager
from datetime import datetime, timezone
from loguru import logger
from objprint import config, op, install; install(); config(line_number=True, arg_name=True,)
from typing import Any, Callable, Final


def log_formatter(record):
    if len(record["extra"]) > 0:
        fmt = "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> |{extra}| - <level>{message}</level>"
    else:
        fmt = "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> - <level>{message}</level>"
    return fmt + "\n{exception}"


logger.remove()
logger.add(
    sys.stdout, level="INFO", colorize=False, format=log_formatter, backtrace=True
)

_current_run_key: Final[str] = "__current_run__"
_namespace_key: Final[str] = "riyad_utils"

class StreamlitAnalytics:
    def __init__(self, default_vals: dict[str, Any]) -> None:
        self.default_vals = default_vals
        self.query_param_keys = set(default_vals.keys())


    def sync_query_params_to_session_state(self) -> None:
        query_params = st.experimental_get_query_params()

        # Get the relevant values
        sync_vals = {}
        for k, v in query_params.items():
            if k in self.default_vals:
                target_type = type(self.default_vals[k])
                sync_vals[k] = target_type(query_params[k][0])

        # Set rest of the default values
        sync_vals = self.default_vals | sync_vals
        for key, val in sync_vals.items():
            st.session_state[key] = val


    def sync_session_state_to_query_params(self) -> None:
        sync_values = {
            k: st.session_state[k] for k in st.session_state.keys() & self.query_param_keys
        }

        st.experimental_set_query_params(**sync_values)


    def sync_widget_state(self, widget_key: str, on_change_func: Callable) -> None:
        self.sync_session_state_to_query_params()
        on_change_func()


    def get_on_change_func(self, widget_key: str, on_change_func: Callable) -> Callable:
        return partial(self.sync_widget_state, widget_key, on_change_func)


    def track_rerun(self) -> None:
        if _current_run_key not in st.session_state:
            logger.info("New fresh run")
            st.session_state[_namespace_key][_current_run_key] = 1
            self.sync_query_params_to_session_state()
        else:
            st.session_state[_namespace_key][_current_run_key] += 1
            logger.info(f"{st.session_state[_namespace_key][_current_run_key]}th run")


    def start_tracking(self) -> None:
        logger.info("Started tracking session")
        current_timestamp = datetime.now(timezone.utc)
        st.session_state[_namespace_key]["start_timestamp"] = current_timestamp
        st.session_state[_namespace_key]["query_params"] = st.experimental_get_query_params()
        self.track_rerun()


    def stop_tracking(self) -> None:
        current_timestamp = datetime.now(timezone.utc)
        st.session_state[_namespace_key]["end_timestamp"] = current_timestamp

        session_state_dict = st.session_state.to_dict()
        op(session_state_dict)

        # with open("session_state.json", "a") as f:
        #     f.write(f"{json.dumps(session_state_dict, sort_keys=True)}\n")

        logger.info("Stopped tracking session")


    @contextmanager
    def track(self):
        current_session_id = str(uuid.uuid4())
        st.session_state[_namespace_key] = {}
        st.session_state[_namespace_key]["session_id"] = current_session_id

        with logger.contextualize(session_id=current_session_id):
            self.start_tracking()
            yield
            self.stop_tracking()
