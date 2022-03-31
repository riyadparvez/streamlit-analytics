import json
import streamlit as st
import sys

from contextlib import contextmanager
from datetime import datetime, timezone
from google.cloud import firestore
from google.oauth2 import service_account
from loguru import logger
from streamlit.script_run_context import get_script_run_ctx
from streamlit.server.server import Server

config_path = "/Users/riyad/Downloads/firestore.json"

with open(config_path) as f:
    config = json.load(f)

creds = service_account.Credentials.from_service_account_info(config)
# db = firestore.Client.from_service_account_json("/Users/riyad/Downloads/firestore.json")
db = firestore.Client(credentials=creds)

collection_ref = db.collection("usage-analytics")


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


def start():
    logger.info("Started tracking session")


def stop():
    session_state_dict = st.session_state.to_dict()
    current_timestamp = datetime.now(timezone.utc)
    session_state_dict["timestamp"] = current_timestamp.isoformat()
    print(session_state_dict)

    # with open("session_state.json", "a") as f:
    #     f.write(f"{json.dumps(session_state_dict, sort_keys=True)}\n")

    logger.info("Stopped tracking session")


@contextmanager
def track():
    report_ctx = get_script_run_ctx()
    current_session_id = report_ctx.session_id
    session_info = Server.get_current()._get_session_info(current_session_id)
    headers = (
        session_info.ws.request.headers
    )  # errors on first page load because the ws object is None
    st.session_state["session_id"] = current_session_id
    st.session_state["user_agent"] = headers["User-Agent"]

    with logger.contextualize(session_id=current_session_id):
        start()
        yield
        stop()
