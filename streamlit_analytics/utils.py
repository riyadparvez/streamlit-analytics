import streamlit as st
import sys
import uuid

from contextlib import contextmanager
from datetime import datetime, timezone
from loguru import logger
from objprint import config, op, install; install(); config(line_number=True, arg_name=True,)


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


def start_tracking() -> None:
    logger.info("Started tracking session")
    current_timestamp = datetime.now(timezone.utc)
    st.session_state["session_info"]["start_timestamp"] = current_timestamp
    st.session_state["session_info"]["query_params"] = st.experimental_get_query_params()


def stop_tracking() -> None:
    current_timestamp = datetime.now(timezone.utc)
    st.session_state["session_info"]["end_timestamp"] = current_timestamp

    session_state_dict = st.session_state.to_dict()
    op(session_state_dict)

    # with open("session_state.json", "a") as f:
    #     f.write(f"{json.dumps(session_state_dict, sort_keys=True)}\n")

    logger.info("Stopped tracking session")


@contextmanager
def track():
    current_session_id = str(uuid.uuid4())
    st.session_state["session_info"] = {}
    st.session_state["session_info"]["session_id"] = current_session_id

    with logger.contextualize(session_id=current_session_id):
        start_tracking()
        yield
        stop_tracking()
