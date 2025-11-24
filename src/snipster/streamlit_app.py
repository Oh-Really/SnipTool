import requests
import streamlit as st

st.title("Snipster - Code snippet manager")


API_URL = "http://localhost:8000"


def api_list_snippets():
    response = requests.get(f"{API_URL}/snippets")
    return response.json()


def api_get_snippet(snippet_id):
    response = requests.get(f"{API_URL}/snippets/{snippet_id}")
    return response.json()


def api_add_snippet(title: str, code: str, description: str | None):
    payload = {
        "title": title,
        "code": code,
        "description": description,
    }
    resp = requests.post(f"{API_URL}/snippets", json=payload)
    resp.raise_for_status()
    return resp.json()


if "page" not in st.session_state:
    st.session_state.page = "list"  # "list" | "view" | "add"

if "snippet_id" not in st.session_state:
    st.session_state.snippet_id = None


def page_list_snippets():
    st.title("All Snippets")

    try:
        snippets = api_list_snippets()
    except requests.RequestException as e:
        st.error(f"Error talking to API: {e}")
        return

    if not snippets:
        st.info("No snippets found yet. Try adding one from the sidebar.")
        return

    for snippet in snippets:
        with st.container():
            st.subheader(snippet["title"])
            if snippet.get("description"):
                st.write(snippet["description"])
            # Small meta line
            meta = []
            if snippet.get("favourite"):
                meta.append("⭐ favourite")
            if meta:
                st.caption(" · ".join(meta))

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("View", key=f"view-{snippet['id']}"):
                    st.session_state.page = "view"
                    st.session_state.snippet_id = snippet["id"]
                    st.rerun()
            st.markdown("---")


def page_view_snippet():
    snippet_id = st.session_state.snippet_id
    if snippet_id is None:
        st.warning("No snippet selected.")
        return

    try:
        snippet = api_get_snippet(snippet_id)
    except requests.RequestException as e:
        st.error(f"Error fetching snippet: {e}")
        return

    st.title(snippet["title"])

    st.code(snippet["code"], language="python")

    if snippet.get("description"):
        st.markdown("**Description**")
        st.write(snippet["description"])

    st.markdown("---")
    if st.button("Back to all snippets"):
        st.session_state.page = "list"
        st.session_state.snippet_id = None
        st.rerun()


def page_add_snippet():
    st.title("Add New Snippet")

    with st.form("add-snippet-form"):
        title = st.text_input("Title")
        code = st.text_area("Code")
        description = st.text_area("Description (optional)", height=100)

        submitted = st.form_submit_button("Add snippet")

    if submitted:
        if not title or not code:
            st.error("Title and code are required.")
            return

        try:
            api_add_snippet(title=title, code=code, description=description or None)
        except requests.RequestException as e:
            st.error(f"Error adding snippet: {e}")
            return

        st.success("Snippet added successfully!")
        # Go back to list page
        st.session_state.page = "list"
        st.rerun()


if st.session_state.page == "list":
    page_list_snippets()
elif st.session_state.page == "view":
    page_view_snippet()
elif st.session_state.page == "add":
    page_add_snippet()
else:
    st.session_state.page = "list"
    page_list_snippets()


if st.sidebar.button("All snippets"):
    st.session_state.page = "list"
    st.session_state.snippet_id = None
    st.rerun()

if st.sidebar.button("Add new snippet"):
    st.session_state.page = "add"
    st.session_state.snippet_id = None
    st.rerun()
