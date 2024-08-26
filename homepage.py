import streamlit as st
import user_list
import yaml
from yaml.loader import SafeLoader


# Load the configuration file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


# save all the conversation of all the user(prefer to save in yaml file instead)
@st.cache_resource
def conversation_with():
    credentials = config.get('credentials', {}).get('usernames', {})
    all_conv = {}    # all the conversation
    for user in credentials:
        all_conv[user] = {'talk to yourself': []}
    return all_conv


# not save twice same data (use only once for any trio)
@st.cache_data
def the_order(username, other_user, all_conv):
    if other_user in all_conv[username]:
        return username, other_user
    else:
        return other_user, username


def run(authenticator, username):
    col1, col2 = st.columns([1, 1], vertical_alignment="top", gap="small")
    col1.title('welcome: ' + username)
    authenticator.logout('Logout', 'main')
    other_user = user_list.run(username, config)
    st.session_state.messages = conversation_with()
    x, y = the_order(username, other_user, st.session_state.messages)

    # Display chat messages from history on app rerun
    for message in st.session_state.messages[x][y]:
        if message["role"] == username:     # if the user write
            with st.chat_message("user"):
                st.markdown(message["content"])
                if "download" in message and message["download"] is not None:
                    st.download_button(label="Download", data=message["download"], file_name=message["content"])
        else:   # if the other user write
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "download" in message and message["download"] is not None:
                    st.download_button(label="Download", data=message["download"], file_name=message["content"])

    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message('user'):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages[x][y].append({"role": username, "content": prompt})

    with col2.form("chat"):
        # Create a file uploader widget
        uploaded_file = st.file_uploader("Choose a file",label_visibility="collapsed")
        submitted = st.form_submit_button("upload")
    # press upload
    if submitted:
        # Check if a file has been uploaded in the first time
        if uploaded_file is not None and not any(msg['content'] == uploaded_file.name for msg in st.session_state.messages[x][y]):
            # add option to download the file
            with st.chat_message('user'):
                st.markdown(uploaded_file.name)
                to_download = st.download_button(label="Download", data=uploaded_file, file_name=uploaded_file.name)
            # Add user message to chat history
            st.session_state.messages[x][y].append({"role": username, "content": uploaded_file.name,
                                                    "download": uploaded_file})
        elif uploaded_file is None:
            st.warning("you need upload some file")
        else:
            st.warning("This file has already been uploaded.")




