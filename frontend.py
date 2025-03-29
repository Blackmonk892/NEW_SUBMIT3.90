import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Blood Donation Gamification Platform", layout="wide")

# Initialize session state variables.
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "username" not in st.session_state:
    st.session_state.username = None

# Utility function to return headers.
def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

# Helper to extract error details from response.
def get_error_detail(response):
    try:
        # Try parsing as JSON and getting the "detail" key.
        return response.json().get("detail", "Unknown error")
    except ValueError:
        # Fallback to plain text if response isn't JSON.
        return f"Server returned non-JSON response: {response.text}"

# Authentication UI
def login():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            res = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
            if res.status_code == 200:
                st.session_state.access_token = res.json()["access_token"]
                st.session_state.username = username
                st.success("Logged in!")
                st.rerun()
            else:
                error_detail = get_error_detail(res)
                st.error(f"Login failed: {error_detail}")

def register():
    st.title("Register")
    with st.form("register_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Register")
        if submitted:
            res = requests.post(
                f"{API_URL}/register",
                params={"email": email, "username": username, "password": password}
            )
            if res.status_code == 200:
                st.success("Registered! Please log in.")
            else:
                error_detail = get_error_detail(res)
                st.error(f"Registration failed: {error_detail}")

def auth_screen():
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login()
    with tab2:
        register()

def show_profile():
    st.subheader("Profile")
    res = requests.get(f"{API_URL}/profile", headers=get_headers())
    if res.status_code == 200:
        data = res.json()
        st.text(f"Username: {data['username']}")
        st.text(f"Email: {data['email']}")
        st.text(f"Hearts: {data['hearts']}")
        st.text(f"Donations: {data['donations']}")
        st.write("Messages:")
        for msg in data.get("messages", []):
            st.success(msg)
    else:
        error_detail = get_error_detail(res)
        st.error(f"Failed to fetch profile: {error_detail}")

def donate():
    st.subheader("Donate Blood")
    if st.button("🩸 Donate Now"):
        res = requests.post(f"{API_URL}/donate", headers=get_headers())
        if res.status_code == 200:
            data = res.json()
            st.balloons()
            st.success(data.get("message", "Donation successful!"))
        else:
            error_detail = get_error_detail(res)
            st.error(f"Donation failed: {error_detail}")

def show_leaderboard():
    st.subheader("Leaderboard")
    res = requests.get(f"{API_URL}/leaderboard")
    if res.status_code == 200:
        data = res.json()
        for i, user in enumerate(data):
            st.markdown(f"**{i+1}. {user['username']} - ❤️ {user['hearts']} ({user['donations']} donations)**")
    else:
        error_detail = get_error_detail(res)
        st.error(f"Failed to fetch leaderboard: {error_detail}")

def show_campaigns():
    st.subheader("Live Campaigns")
    res = requests.get(f"{API_URL}/campaigns")
    if res.status_code == 200:
        data = res.json()
        for item in data:
            st.info(f"📍 {item['name']} at {item['location']} - {item['time']} [{item['status']}]")
    else:
        error_detail = get_error_detail(res)
        st.error(f"Failed to fetch campaigns: {error_detail}")

def show_rewards():
    st.subheader("Your Rewards")
    res = requests.get(f"{API_URL}/rewards", headers=get_headers())
    if res.status_code == 200:
        rewards = res.json()
        if rewards:
            for r in rewards:
                st.success(r)
        else:
            st.warning("No rewards yet. Keep donating!")
    else:
        error_detail = get_error_detail(res)
        st.error(f"Failed to fetch rewards: {error_detail}")

# App Navigation
if not st.session_state.access_token:
    auth_screen()
else:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Profile", "Donate", "Leaderboard", "Campaigns", "Rewards"])

    if page == "Profile":
        show_profile()
    elif page == "Donate":
        donate()
    elif page == "Leaderboard":
        show_leaderboard()
    elif page == "Campaigns":
        show_campaigns()
    elif page == "Rewards":
        show_rewards()

    if st.sidebar.button("Logout"):
        st.session_state.access_token = None
        st.session_state.username = None
        st.rerun()

