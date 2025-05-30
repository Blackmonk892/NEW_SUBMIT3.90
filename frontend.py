import streamlit as st
import requests
<<<<<<< HEAD

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

=======
import pydeck as pdk
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from streamlit_folium import st_folium
import folium

# --- Configuration ---
BACKEND_URL = "http://localhost:8000"

# Initialize session state
if 'manual_location' not in st.session_state:
    st.session_state.manual_location = None

if 'all_blood_banks' not in st.session_state:
    st.session_state.all_blood_banks = None

# --- Helper Functions ---
def get_location():
    # First check for manual location in session state
    if st.session_state.manual_location:
        return (st.session_state.manual_location[0], st.session_state.manual_location[1])
    
    # Then try geolocation
    location = streamlit_geolocation()
    if location and 'latitude' in location and 'longitude' in location:
        return (location['latitude'], location['longitude'])
    
    # Default fallback
    return None

def show_route(start_coords, end_coords, route_data):
    if not route_data.get('paths'):
        st.error("No route found")
        return
    
    path = route_data['paths'][0]
    points = [
        [coord[0], coord[1]] 
        for coord in path['points']['coordinates']
    ]
    
    st.subheader("Route Details")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Distance", f"{path['distance']/1000:.2f} km")
    with col2:
        time_mins = path['time'] / 60000  # Convert milliseconds to minutes
        if time_mins < 60:
            time_str = f"{time_mins:.0f} min"
        else:
            time_str = f"{time_mins/60:.1f} hours"
        st.metric("Duration", time_str)
    
    # Create a map with the route
    midpoint = [(start_coords[0] + end_coords[0])/2, (start_coords[1] + end_coords[1])/2]
    
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=midpoint[0],
            longitude=midpoint[1],
            zoom=11,
            pitch=50,
        ),
        layers=[
            # Route layer
            pdk.Layer(
                'PathLayer',
                data=[{
                    "path": points,
                    "color": [255, 0, 0]
                }],
                get_color="color",
                get_width=5,
                pickable=True,
            ),
            # Start point marker
            pdk.Layer(
                'ScatterplotLayer',
                data=[{
                    "position": [start_coords[1], start_coords[0]],
                    "color": [0, 255, 0],
                    "radius": 100
                }],
                get_position="position",
                get_color="color",
                get_radius="radius",
            ),
            # End point marker
            pdk.Layer(
                'ScatterplotLayer',
                data=[{
                    "position": [end_coords[1], end_coords[0]],
                    "color": [0, 0, 255],
                    "radius": 100
                }],
                get_position="position",
                get_color="color",
                get_radius="radius",
            ),
        ]
    ))

def select_location_on_map():
    st.subheader("Select Your Location on Map")
    
    # Set default center to a reasonable location (e.g., India center)
    center_lat, center_lon = 20.5937, 78.9629
    
    # Create a map centered at the default location
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Display the map and get click information
    map_data = st_folium(m, height=400, width=700)
    
    # Check if map was clicked
    if map_data["last_clicked"]:
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lng = map_data["last_clicked"]["lng"]
        st.session_state.manual_location = (clicked_lat, clicked_lng)
        st.success(f"Location selected: {clicked_lat:.6f}, {clicked_lng:.6f}")
        return True
    
    return False

def load_all_blood_banks():
    try:
        if st.session_state.all_blood_banks is None:
            response = requests.get(f"{BACKEND_URL}/all-blood-banks")
            if response.status_code == 200:
                st.session_state.all_blood_banks = response.json()
            else:
                st.error(f"Failed to load blood banks: {response.text}")
                return None
        return st.session_state.all_blood_banks
    except Exception as e:
        st.error(f"Error loading blood bank data: {str(e)}")
        return None

def get_nearby_blood_banks(lat, lon):
    try:
        response = requests.post(
            f"{BACKEND_URL}/nearby",
            json={"latitude": lat, "longitude": lon}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error from server: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to server: {str(e)}")
        return None

# --- Main App ---
st.title("Blood Bank Locator 🩸")
st.markdown("Find the nearest blood banks and get directions to them.")

# Add tabs for different features
tab1, tab2 = st.tabs(["Find Nearby Blood Banks", "Blood Bank Map"])

with tab1:
    # Get User Location
    location = get_location()
    
    # Check if we have a location
    if location and location[0] is not None and location[1] is not None:
        st.success(f"Using location: {location[0]:.6f}, {location[1]:.6f}")
        
        # Get Nearby Blood Banks
        banks = get_nearby_blood_banks(location[0], location[1])
        
        if banks and len(banks) > 0:
            st.subheader("Nearby Blood Banks")
            selected_bank = st.selectbox(
                "Select a blood bank", 
                banks, 
                format_func=lambda x: f"{x['name']} ({x['distance']:.2f} km)"
            )
            
            if selected_bank:
                st.subheader("Blood Bank Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {selected_bank['name']}")
                    st.write(f"**Address:** {selected_bank['address']}")
                    st.write(f"**City:** {selected_bank['city']}, {selected_bank['state']}")
                with col2:
                    st.write(f"**Distance:** {selected_bank['distance']:.2f} km")
                    st.write(f"**Coordinates:** {selected_bank['latitude']:.6f}, {selected_bank['longitude']:.6f}")
                
                # Get Route Data
                if st.button("Show Route"):
                    with st.spinner("Calculating route..."):
                        route_response = requests.get(
                            f"{BACKEND_URL}/route",
                            params={
                                "start_lat": location[0],
                                "start_lon": location[1],
                                "end_lat": selected_bank['latitude'],
                                "end_lon": selected_bank['longitude']
                            }
                        )
                        
                        if route_response.status_code == 200:
                            show_route(
                                (location[0], location[1]),
                                (selected_bank['latitude'], selected_bank['longitude']),
                                route_response.json()
                            )
                        else:
                            st.error(f"Failed to get route: {route_response.text}")
                            if "API key not configured" in route_response.text:
                                st.info("The Graphhopper API key is missing. Please set the GRAPHHOPPER_API_KEY environment variable.")
        else:
            st.error("No blood banks found nearby or failed to retrieve data from server.")
    else:
        st.warning("Location not detected automatically.")
        
        # Manual location entry methods
        st.subheader("Set Your Location Manually")
        
        method = st.radio("Choose method:", ["Enter Coordinates", "Select on Map"])
        
        if method == "Enter Coordinates":
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitude", value=20.5937, format="%.6f")
            with col2:
                lon = st.number_input("Longitude", value=78.9629, format="%.6f")
            
            if st.button("Use This Location"):
                st.session_state.manual_location = (lat, lon)
                st.rerun()
        else:
            if select_location_on_map():
                st.button("Continue with Selected Location", on_click=st.rerun)

with tab2:
    st.subheader("Blood Bank Map")
    
    # Load all blood banks for map view
    all_banks = load_all_blood_banks()
    
    if all_banks:
        # Create a map centered at a middle point of India
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
        
        # Add markers for each blood bank
        for bank in all_banks:
            folium.Marker(
                location=[bank['latitude'], bank['longitude']],
                popup=f"{bank['name']}<br>{bank['address']}<br>{bank['city']}, {bank['state']}",
                tooltip=bank['name']
            ).add_to(m)
            
        # If we have a user location, add that too
        if 'manual_location' in st.session_state and st.session_state.manual_location:
            folium.Marker(
                location=st.session_state.manual_location,
                popup="Your Location",
                tooltip="Your Location",
                icon=folium.Icon(color='green')
            ).add_to(m)
            
        # Display the map
        st_folium(m, height=500, width=700)
    else:
        st.error("Unable to load blood bank data for map view")
>>>>>>> 8508803798fa3accb75b0b5e56c17fca8141897c
