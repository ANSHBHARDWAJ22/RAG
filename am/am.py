import streamlit as st
import requests
from requests_oauthlib import OAuth2Session
from urllib.parse import urlparse, parse_qs

# LinkedIn App credentials
CLIENT_ID = '77clzmpsyx0sro'
CLIENT_SECRET = 'WPL_AP1.MoWK2bERUJMiwVA8.AK59XQ=='
REDIRECT_URI = 'https://www.linkedin.com/developers/tools/oauth/redirect'

# OAuth 2.0 endpoints for LinkedIn
AUTHORIZATION_URL = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
API_URL = 'https://api.linkedin.com/v2/ugcPosts'

# Scope of permissions required (to post on behalf of user)
SCOPE = ["r_liteprofile", "r_emailaddress", "w_member_social"]

# This is your LinkedIn User ID: dhruv-singh-94340b28a
USER_ID = 'dhruv-singh-94340b28a'


# Step 1: Generate authorization URL
def get_oauth2_authorization_url():
    linkedin = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    authorization_url, state = linkedin.authorization_url(AUTHORIZATION_URL)
    return authorization_url

# Step 2: Get access token after authorization
def get_access_token(authorization_response):
    linkedin = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    token = linkedin.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=authorization_response)
    return token

# Step 3: Post an update to LinkedIn
def post_linkedin_update(access_token, message):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'x-li-format': 'json'
    }
    
    post_data = {
        "author": f"urn:li:person:{USER_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": message
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=post_data)
    if response.status_code == 201:
        st.success(f"Post successfully created!")
        st.write(f"Your LinkedIn post message: {message}")
    else:
        st.error(f"Failed to post. Status code: {response.status_code}")
        st.write(response.text)


# Streamlit UI

st.title("LinkedIn Post Simulator")

# Input for LinkedIn URL (simulated, but not used for the real post request)
st.subheader("Enter LinkedIn Profile URL (Simulated)")
linkedin_url = st.text_input("LinkedIn URL", placeholder="https://www.linkedin.com/in/your-profile/")

# Input for new post message
st.subheader("Create a New LinkedIn Post")
post_message = st.text_area("Post Content", placeholder="What's on your mind?")

# If access token is not in session, initiate OAuth login
if 'access_token' not in st.session_state:
    st.subheader("Login to LinkedIn to Post")

    # Generate the authorization URL
    auth_url = get_oauth2_authorization_url()
    st.markdown(f"[Click here to log in to LinkedIn]({auth_url})")

    # Capture the redirected URL after authentication
    auth_response = st.text_input("Paste the full redirect URL here:")

    if auth_response:
        # Exchange the authorization code for an access token
        token = get_access_token(auth_response)
        st.session_state.access_token = token['access_token']
        st.success("You are now logged in!")
else:
    # If logged in, display the post functionality
    st.subheader("Create a New LinkedIn Post")

    # Post button to make an update
    if st.button("Post Update"):
        if post_message:
            # Post the update via LinkedIn API
            post_linkedin_update(st.session_state.access_token, post_message)
        else:
            st.error("Please provide a post message.")
