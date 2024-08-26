import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_authenticator import Authenticate
from yaml import SafeDumper
from yaml.loader import SafeLoader
import re
import dns.resolver
import homepage


# Save the configuration file
def save_config(file_path, config):
    with open(file_path, 'w') as file:
        yaml.dump(config, file, Dumper=SafeDumper)


# Add new user to the configuration
def add_user_to_config(config, username, email, name, password):
    if 'credentials' not in config:
        config['credentials'] = {'usernames': {}}

    if 'usernames' not in config['credentials']:
        config['credentials']['usernames'] = {}

    # Create a new user entry
    hashed_password = stauth.Hasher([password]).generate()[0]  # Hash the password
    config['credentials']['usernames'][username] = {
        'email': email,
        'name': name,
        'password': hashed_password
    }


# function to check email
def is_valid_email_syntax(email):
    """
    Check if the email address has a valid syntax.
    """
    email_regex = re.compile(
        r"(^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$)"
    )
    return re.match(email_regex, email) is not None


# function to check email
def has_valid_domain(email):
    """
    Check if the domain of the email address has valid DNS records.
    """
    domain = email.split('@')[1]
    try:
        # Check if domain has an MX record
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False


# function to check email
def is_email_valid(email):
    """
    Check if the email address is valid by syntax and domain.
    """
    return is_valid_email_syntax(email) and has_valid_domain(email)


# Function to check if passwords match
def passwords_match(password, confirm_password):
        return password == confirm_password


# Function to check if username or email already exists
def user_exists(username, email):
    credentials = config.get('credentials', {}).get('usernames', {})
    for user, details in credentials.items():
        if user == username or details.get('email') == email:
            return True
    return False


# Load the configuration file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Set up authentication
authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)


# check if the login is full as required
def login_required():
    # ****Handle login****
    name, authentication_status, username = authenticator.login('main')
    # Display content based on authentication status
    if authentication_status:
        homepage.run(authenticator, username)
        return True
    elif authentication_status is None:
        st.warning('Please enter your username and password')
    elif not authentication_status:
        st.error('Username/password is incorrect')


# check if the registered is full as required
def registered_required(login):
    # **** Handle registered*******
    if not login:
        st.title("Register a New User")

        with st.form("registration_form"):
            name = st.text_input("Full Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            submit_button = st.form_submit_button("Register")

            if submit_button:
                if not email or not username or not name or not password or not confirm_password:
                    st.warning("Please fill in all the fields.")
                elif user_exists(username, email):
                    st.error("Username or email already exists.")
                elif not is_email_valid(email):
                    st.error("email not legal")
                elif not passwords_match(password, confirm_password):
                    st.error("Passwords do not match.")
                else:
                    st.success("Successfully registered.")
                    # Add user to configuration
                    add_user_to_config(config, username, email, name, password)
                    save_config('config.yaml', config)


def run():
    login = login_required()
    if login is None:
        registered_required(login)


run()

