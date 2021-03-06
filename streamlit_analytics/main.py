from __future__ import annotations
import streamlit as st
import sys
import uuid

from contextlib import contextmanager
from datetime import datetime, timezone
from functools import partial
from objprint import op
from typing import Any, Callable, Final

from .constants import *
from .custom_logger import logger
from .firestore_utils import *
from .db_utils import *


_DO_NOTHING: Final[Callable] = lambda: None


def _serialize(d: dict[str, Any]) -> dict[str, Any]:
    for k, v in d.items():
        if type(v).__module__ != "builtins" and not isinstance(v, datetime):
            d[k] = str(v)
    return d


class StreamlitAnalytics:
    def __init__(
        self,
        application_name: str,
        namespace_key: str = DEFAULT_NAMESPACE_KEY,
        print_analytics: bool = False,
        default_vals: dict[str, Any] | None = None,
        db_uri: str = None,
        json_file_path: str = None,
        firestore_collection_name: str = None,
    ) -> None:
        self.application_name = application_name
        self.namespace_key = namespace_key
        self.print_analytics = print_analytics
        self.default_vals = default_vals
        self.sync_query_params = self.default_vals is not None
        if self.sync_query_params:
            self.query_param_keys = set(default_vals.keys())

        self.json_file_path = json_file_path
        self.db_adapter = None
        if isinstance(db_uri, str):
            self.db_uri = db_uri
            self.db_adapter = DbAdapter(db_uri)
            logger.debug(f"Initialized DB client")

        self.firestore_adapter = None
        if isinstance(firestore_collection_name, str):
            self.firestore_collection_name = firestore_collection_name
            firestore_config = st.secrets["firestore"]
            self.firestore_adapter = FirestoreAdapter(
                firestore_config, firestore_collection_name
            )
            logger.debug(f"Initialized firebase")

    def sync_query_params_to_session_state(self) -> None:
        query_params = st.experimental_get_query_params()

        # Get the relevant values
        sync_vals = {}
        for k, v in query_params.items():
            if k in self.default_vals:
                target_type = type(self.default_vals[k])
                sync_vals[k] = [
                    target_type(query_param) for query_param in query_params
                ]

        # Set rest of the default values
        sync_vals = self.default_vals | sync_vals
        for key, val in sync_vals.items():
            st.session_state[key] = val

    def sync_session_state_to_query_params(self) -> None:
        sync_values = {
            k: st.session_state[k]
            for k in st.session_state.keys() & self.query_param_keys
        }

        st.experimental_set_query_params(**sync_values)

    def sync_widget_state(self, widget_key: str, on_change_func: Callable) -> None:
        if self.sync_query_params:
            self.sync_session_state_to_query_params()
        logger.info(f"On {widget_key} changed")
        st.session_state[self.namespace_key]["interactions"].append(
            {widget_key: st.session_state[widget_key]}
        )
        on_change_func()

    def get_on_change_func(
        self, widget_key: str, on_change_func: Callable = _DO_NOTHING
    ) -> Callable:
        return partial(self.sync_widget_state, widget_key, on_change_func)

    def track_new_session_run(self) -> None:
        """
        Track new session and new run
        """
        current_timestamp = datetime.now(timezone.utc)
        try:
            if self.namespace_key not in st.session_state:
                st.session_state[self.namespace_key] = {}
                st.session_state[self.namespace_key][runs_key] = []
                st.session_state[self.namespace_key]["interactions"] = []
                current_session_id = str(uuid.uuid4())
                st.session_state[self.namespace_key]["session_id"] = current_session_id
                st.session_state[self.namespace_key][
                    "start_timestamp"
                ] = current_timestamp
            else:
                current_session_id = st.session_state[self.namespace_key]["session_id"]
                logger.info(
                    f"New fresh session: {current_session_id}",
                )

            if current_run_key in st.session_state[self.namespace_key]:
                st.session_state[self.namespace_key][
                    current_run_key
                ] = st.session_state[self.namespace_key][current_run_key].copy()
                st.session_state[self.namespace_key][current_run_key]["run_number"] += 1
                logger.info(
                    f"{st.session_state[self.namespace_key][current_run_key]['run_number']}th run"
                )
            else:
                logger.info("New fresh run")
                st.session_state[self.namespace_key][current_run_key] = {}
                st.session_state[self.namespace_key][current_run_key]["run_number"] = 1
                if self.sync_query_params:
                    self.sync_query_params_to_session_state()

            st.session_state[self.namespace_key][current_run_key][
                "start_timestamp"
            ] = current_timestamp
        except Exception as e:
            logger.exception(f"Failed: {e}")

    def start_tracking(self) -> None:
        try:
            logger.info("Started tracking run")
            self.track_new_session_run()
            # st.session_state[session_key][
            #     "query_params"
            # ] = st.experimental_get_query_params()
        except Exception as e:
            logger.exception(f"Failed: {e}")

    def stop_tracking(self) -> None:
        try:
            current_timestamp = datetime.now(timezone.utc)
            st.session_state[self.namespace_key]["end_timestamp"] = current_timestamp
            st.session_state[self.namespace_key][current_run_key][
                "end_timestamp"
            ] = current_timestamp
            st.session_state[self.namespace_key][runs_key].append(
                st.session_state[self.namespace_key][current_run_key]
            )

            st_session_state_dict = st.session_state.to_dict()
            # Only write the necessary keys
            session_state_dict = st_session_state_dict[self.namespace_key].copy()
            current_run = session_state_dict.pop(current_run_key, None)
            session_state_dict = _serialize(session_state_dict)
            session_state_dict["interactions"] = [
                _serialize(interaction)
                for interaction in session_state_dict["interactions"]
            ]

            if self.print_analytics:
                op(session_state_dict)

            if self.json_file_path is not None:
                with open(self.json_file_path, "a") as f:
                    f.write(f"{json.dumps(session_state_dict, sort_keys=True)}\n")

            if self.firestore_adapter is not None:
                self.firestore_adapter.insert_doc(
                    session_state_dict["session_id"],
                    session_state_dict,
                )

            if self.db_adapter is not None:
                self.db_adapter.insert_row(session_state_dict)
            logger.info("Stopped tracking run")
        except Exception as e:
            logger.exception(f"Failed: {e}")

    @contextmanager
    def track(self):
        self.start_tracking()
        yield
        self.stop_tracking()

    @property
    def session_id(self) -> str:
        return st.session_state[self.namespace_key]["session_id"]


def track(
    application_name: str,
    default_vals: dict[str, Any] | None = None,
    db_uri: str = None,
    json_file_path: str = None,
    firestore_key_file: str = None,
    firestore_collection_name: str = None,
):
    sa = StreamlitAnalytics(
        application_name,
        default_vals,
        db_uri,
        json_file_path,
        firestore_key_file,
        firestore_collection_name,
    )
    return sa.track
