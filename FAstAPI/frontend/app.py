import os
import logging

import pandas as pd
import requests
import streamlit as st


st.set_page_config(page_title="Task Desk", page_icon="T", layout="wide")

logger = logging.getLogger(__name__)


def api_request(
    base_url: str,
    method: str,
    path: str,
    payload: dict | None = None,
    authenticated: bool = True,
):
    # Log the route and result only; never log request bodies or bearer tokens.
    logger.debug("API request started: %s %s", method, path)
    token = st.session_state.get("access_token") if authenticated else None
    headers = {"Authorization": f"Bearer {token}"} if token else None
    try:
        response = requests.request(
            method,
            f"{base_url}{path}",
            json=payload,
            headers=headers,
            timeout=10,
        )
    except requests.RequestException as error:
        logger.warning("API request could not connect (%s)", type(error).__name__)
        return None, f"Could not reach the FastAPI server: {error}"

    if response.status_code == 401 and authenticated:
        logger.warning("API returned 401; clearing the expired frontend session")
        st.session_state.pop("access_token", None)
        st.session_state["flash_error"] = "Your session expired. Please sign in again."
        st.rerun()

    if not response.ok:
        logger.warning("API request failed with status %s", response.status_code)
        try:
            details = response.json().get("detail", response.text)
        except ValueError:
            details = response.text or response.reason
        return None, f"Request failed ({response.status_code}): {details}"

    if response.status_code == 204:
        logger.info("API request succeeded: %s %s (204)", method, path)
        return None, None

    try:
        result = response.json()
        logger.info("API request succeeded: %s %s (%s)", method, path, response.status_code)
        return result, None
    except ValueError:
        logger.error("API returned invalid JSON for %s %s", method, path)
        return None, "The API returned a response that was not valid JSON."


def show_success(message: str) -> None:
    logger.info("Displaying successful action in the frontend")
    st.session_state["flash_message"] = message
    st.rerun()


st.title("Task Desk")

with st.sidebar:
    st.subheader("Backend")
    entered_url = st.text_input(
        "FastAPI URL",
        value=os.getenv("FASTAPI_BASE_URL", "http://127.0.0.1:8000"),
        help="Enter the API root. The /docs suffix is removed automatically.",
    ).strip()
    base_url = entered_url.removesuffix("/docs").rstrip("/")
    if base_url:
        st.link_button("Open API docs", f"{base_url}/docs")

    st.divider()
    st.subheader("Account")
    access_token = st.session_state.get("access_token")
    if access_token:
        current_user, user_error = api_request(base_url, "GET", "/auth/me")
        if user_error:
            st.error(user_error)
        elif current_user:
            st.caption(f"Signed in as {current_user['name']}")

        if st.button("Sign out", use_container_width=True):
            _, logout_error = api_request(base_url, "POST", "/auth/logout")
            if logout_error:
                st.error(logout_error)
            else:
                st.session_state.pop("access_token", None)
                show_success("You have signed out.")
    else:
        auth_mode = st.radio("Account action", ["Sign in", "Register"], horizontal=True)
        with st.form("authentication_form"):
            if auth_mode == "Register":
                account_name = st.text_input("Name")
            account_email = st.text_input("Email")
            account_password = st.text_input("Password", type="password")
            auth_submitted = st.form_submit_button(
                auth_mode,
                type="primary",
                use_container_width=True,
            )

        if auth_submitted:
            if auth_mode == "Register":
                _, register_error = api_request(
                    base_url,
                    "POST",
                    "/auth/register",
                    {
                        "name": account_name.strip(),
                        "email": account_email.strip(),
                        "password": account_password,
                    },
                    authenticated=False,
                )
                if register_error:
                    st.error(register_error)
                else:
                    login_payload = {
                        "email": account_email.strip(),
                        "password": account_password,
                    }
                    token_response, login_error = api_request(
                        base_url,
                        "POST",
                        "/auth/login",
                        login_payload,
                        authenticated=False,
                    )
                    if login_error:
                        st.success("Account created. Sign in to continue.")
                    else:
                        st.session_state["access_token"] = token_response["access_token"]
                        show_success("Account created and signed in.")
            else:
                token_response, login_error = api_request(
                    base_url,
                    "POST",
                    "/auth/login",
                    {
                        "email": account_email.strip(),
                        "password": account_password,
                    },
                    authenticated=False,
                )
                if login_error:
                    st.error(login_error)
                else:
                    st.session_state["access_token"] = token_response["access_token"]
                    show_success("Signed in.")

access_token = st.session_state.get("access_token")
if not base_url:
    tasks, load_error = None, "Enter the FastAPI server URL to load tasks."
elif access_token:
    tasks, load_error = api_request(base_url, "GET", "/tasks")
else:
    tasks, load_error = [], None

if load_error:
    st.error(load_error)
elif not isinstance(tasks, list):
    st.error("The API response for GET /tasks was not a task list.")
    tasks = []

flash_message = st.session_state.pop("flash_message", None)
if flash_message:
    st.success(flash_message)
flash_error = st.session_state.pop("flash_error", None)
if flash_error:
    st.error(flash_error)

if tasks is None:
    tasks = []

task_by_id = {task["id"]: task for task in tasks if "id" in task}
task_ids = list(task_by_id)

list_tab, create_tab, update_tab, delete_tab = st.tabs(
    ["Tasks", "Create", "Update", "Delete"]
)

with list_tab:
    if not access_token:
        st.info("Sign in to view your tasks.")
    else:
        st.metric("Tasks", len(tasks))
    if access_token and tasks:
        st.dataframe(
            pd.DataFrame(tasks),
            hide_index=True,
            use_container_width=True,
        )
    elif access_token and not load_error:
        st.info("No tasks found.")

with create_tab:
    with st.form("create_task_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        status = st.text_input("Status", value="pending")
        create_submitted = st.form_submit_button(
            "Create task", type="primary", disabled=not access_token
        )

    if create_submitted:
        if not title.strip():
            st.error("A task title is required.")
        else:
            _, error = api_request(
                base_url,
                "POST",
                "/tasks",
                {
                    "title": title.strip(),
                    "description": description.strip() or None,
                    "status": status.strip() or "pending",
                },
            )
            if error:
                st.error(error)
            else:
                show_success("Task created.")

with update_tab:
    if not task_ids:
        message = "Sign in to manage tasks." if not access_token else "Create or load a task before updating it."
        st.info(message)
    else:
        selected_id = st.selectbox(
            "Task",
            task_ids,
            format_func=lambda task_id: (
                f"#{task_id} - {task_by_id[task_id].get('title', '')}"
            ),
            key="update_task_id",
        )
        selected_task = task_by_id[selected_id]
        update_mode = st.radio(
            "Update type",
            ["Replace all fields", "Change selected fields"],
            horizontal=True,
        )

        if update_mode == "Replace all fields":
            with st.form("replace_task_form"):
                updated_title = st.text_input(
                    "Title", value=selected_task.get("title", "")
                )
                updated_description = st.text_area(
                    "Description", value=selected_task.get("description") or ""
                )
                updated_status = st.text_input(
                    "Status", value=selected_task.get("status", "pending")
                )
                update_submitted = st.form_submit_button(
                    "Save all fields", type="primary", disabled=not access_token
                )

            if update_submitted:
                if not updated_title.strip():
                    st.error("A task title is required.")
                else:
                    _, error = api_request(
                        base_url,
                        "PUT",
                        f"/tasks/{selected_id}",
                        {
                            "title": updated_title.strip(),
                            "description": updated_description.strip() or None,
                            "status": updated_status.strip() or "pending",
                        },
                    )
                    if error:
                        st.error(error)
                    else:
                        show_success(f"Task #{selected_id} updated.")
        else:
            with st.form("partial_update_task_form"):
                partial_title = st.text_input(
                    "New title", placeholder="Leave blank to keep current"
                )
                partial_status = st.text_input(
                    "New status", placeholder="Leave blank to keep current"
                )
                clear_description = st.checkbox("Clear description")
                partial_description = st.text_area(
                    "New description",
                    placeholder="Leave blank to keep current",
                    disabled=clear_description,
                )
                patch_submitted = st.form_submit_button(
                    "Save selected fields", type="primary", disabled=not access_token
                )

            if patch_submitted:
                payload = {}
                if partial_title.strip():
                    payload["title"] = partial_title.strip()
                if partial_status.strip():
                    payload["status"] = partial_status.strip()
                if clear_description:
                    payload["description"] = None
                elif partial_description.strip():
                    payload["description"] = partial_description.strip()

                if not payload:
                    st.warning("Enter a field to change first.")
                else:
                    _, error = api_request(
                        base_url,
                        "PATCH",
                        f"/tasks/{selected_id}",
                        payload,
                    )
                    if error:
                        st.error(error)
                    else:
                        show_success(f"Task #{selected_id} partially updated.")

with delete_tab:
    if not task_ids:
        message = "Sign in to manage tasks." if not access_token else "Create or load a task before deleting it."
        st.info(message)
    else:
        delete_id = st.selectbox(
            "Task to delete",
            task_ids,
            format_func=lambda task_id: (
                f"#{task_id} - {task_by_id[task_id].get('title', '')}"
            ),
            key="delete_task_id",
        )
        with st.form("delete_task_form"):
            confirm_delete = st.checkbox("Confirm deletion")
            delete_submitted = st.form_submit_button(
                "Delete task", disabled=not access_token
            )

        if delete_submitted:
            if not confirm_delete:
                st.error("Confirm deletion before continuing.")
            else:
                _, error = api_request(
                    base_url,
                    "DELETE",
                    f"/tasks/{delete_id}",
                )
                if error:
                    st.error(error)
                else:
                    show_success(f"Task #{delete_id} deleted.")