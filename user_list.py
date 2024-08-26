import streamlit as st
from streamlit_option_menu import option_menu


# Function to check if username already exists
def user_exists(username, config):
    credentials = config.get('credentials', {}).get('usernames', {})
    return username in credentials


# save the all users friend(prefer to save in yaml file instead)
@st.cache_resource
def all_users(username, config):
    credentials = config.get('credentials', {}).get('usernames', {})
    all_f = {}
    for user in credentials:
        all_f.update({username: ['talk to yourself']})
    return all_f


def run(username, config):
    st.session_state.all_friend = all_users(username, config)
    # Create sidebar with option menu
    with st.sidebar:
        # refresh list button (run the code up->down)
        st.button('refresh list of friend')
        # Display the menu
        app = option_menu(
            menu_title="User",
            options=st.session_state.all_friend[username],
            menu_icon='chat-text-fill',
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": 'white'},
                "icon": {"color": "black", "font-size": "23px"},
                "nav-link": {"color": "black", "font-size": "20px", "text-align": "left", "margin": "0px",
                             "--hover-color": "blue"},
                "nav-link-selected": {"background-color": "#02ab21"},
            }
        )
        # Form to add a new friend
        with st.form('add_friend_form'):
            friend = st.text_input('Enter friend name:')
            add = st.form_submit_button("Add Friend")
            if add:
                if friend and friend not in st.session_state.all_friend[username] and user_exists(friend, config) and username != friend:
                    st.session_state.all_friend[username].append(friend)
                    st.session_state.all_friend[username].sort()  # Optional: Sort the list if desired
                    if username not in st.session_state.messages[friend]:
                        st.session_state.messages[username][friend] = []
                    st.success(f"Added {friend} to friends list!")
                elif friend in st.session_state.all_friend[username]:
                    st.warning("Friend already exists.")
                elif not user_exists(friend, config):
                    st.error("Friend username not exist.")
                elif username == friend:
                    st.error("you can\'t add yourself to friends list.")
                else:
                    st.warning("Friend name cannot be empty.")

    return app

