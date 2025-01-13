# src/gmail_automator/auth.py

import os
import base64
import time
import json
import platform
import subprocess
from datetime import datetime
from google.oauth2.credentials import Credentials
from cryptography.fernet import InvalidToken
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import google.auth.exceptions
# auth.py
# src/gmail_automator/auth.py


SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email'
]

def set_persistent_env_var(env_var_name, env_var_value):
    """Sets or updates a persistent environment variable across different operating systems."""
    current_os = platform.system()

    if current_os in ["Darwin", "Linux"]:
        home_dir = os.path.expanduser("~")
        shell_files = [".bashrc", ".zshrc", ".profile"]

        for shell_file in shell_files:
            full_path = os.path.join(home_dir, shell_file)
            if os.path.exists(full_path):
                with open(full_path, 'r') as file:
                    lines = file.readlines()

                var_exists = False
                for i, line in enumerate(lines):
                    if line.startswith(f'export {env_var_name}='):
                        lines[i] = f'export {env_var_name}="{env_var_value}"\n'
                        var_exists = True
                        break

                if not var_exists:
                    lines.append(f'export {env_var_name}="{env_var_value}"\n')

                with open(full_path, 'w') as file:
                    file.writelines(lines)

                print(f"Updated {env_var_name} in {full_path}")
                print("\033[91mPlease reload your shell. Type source ~/.bashrc\033[0m")

                break
        else:
            print("No suitable shell config file found. Please manually set the environment variable.")

    elif current_os == "Windows":
        set_env_cmd = f'[System.Environment]::SetEnvironmentVariable("{env_var_name}", "{env_var_value}", "User")'
        subprocess.run(["powershell", "-Command", set_env_cmd], check=True)
        print(f"Set or updated {env_var_name} in the Windows environment variables.")
    
    else:
        print(f"Unsupported operating system: {current_os}")
    
    os.environ[env_var_name] = env_var_value

def get_user_email(credentials):
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info['email']
    except Exception as e:
        print(f"Error retrieving user email: {str(e)}")
        return None

def get_encryption_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_value(value, key):
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value, key):
    try:
        f = Fernet(key)
        return f.decrypt(encrypted_value.encode()).decode()
    except InvalidToken:
        print("Decryption failed: Invalid token (mismatched key or corrupted data).")
        raise
    except Exception as e:
        print(f"Decryption failed with an unexpected error: {e}")
        raise

def check_and_refresh_credentials():
    creds = None
    client_id = os.environ.get('GMAIL_CLIENT_ID')
    client_secret = os.environ.get('GMAIL_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set as environment variables")
    
    if os.environ.get('GMAIL_AUTH_REFRESH_TOKEN'):
        try:
            salt = base64.b64decode(os.environ.get('GMAIL_AUTH_SALT'))
            # print(salt)
            key = get_encryption_key(client_id, salt)
            # print(key)
            refresh_token = decrypt_value(os.environ.get('GMAIL_AUTH_REFRESH_TOKEN'), key)
            # print(refresh_token)
            expiry = datetime.fromisoformat(os.environ.get('GMAIL_AUTH_TOKEN_EXPIRY'))
            
            creds = Credentials(
                None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                expiry=expiry
            )
        except Exception as e:
            print(f"Error decrypting stored credentials: {str(e)}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                salt = base64.b64decode(os.environ.get('GMAIL_AUTH_SALT'))
                key = get_encryption_key(client_id, salt)
                set_persistent_env_var('GMAIL_AUTH_REFRESH_TOKEN', encrypt_value(creds.refresh_token, key))
                set_persistent_env_var('GMAIL_AUTH_TOKEN_EXPIRY', creds.expiry.isoformat())
            except Exception as e:
                print(f"Error refreshing token: {str(e)}")
                creds = None

    if not creds:
        flow = Flow.from_client_config(
            {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        
        print(f"Please visit this URL to authorize the application: {auth_url}")
        auth_code = input("Enter the authorization code: ")
        
        try:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            
            user_email = get_user_email(creds)
            if user_email:
                set_persistent_env_var('GMAIL_USER_EMAIL', user_email)
            
            salt = os.urandom(16)
            key = get_encryption_key(client_id, salt)
            print(key)
            set_persistent_env_var('GMAIL_AUTH_SALT', base64.b64encode(salt).decode())
            set_persistent_env_var('GMAIL_AUTH_REFRESH_TOKEN', encrypt_value(creds.refresh_token, key))
            set_persistent_env_var('GMAIL_AUTH_TOKEN_EXPIRY', creds.expiry.isoformat())
            
            print("Credentials have been stored as environment variables.")
        except Exception as e:
            print(f"Failed to obtain access token: {str(e)}")
            return None

    return creds

def clear_stored_credentials():
    """Clear all stored Gmail authentication credentials from environment variables."""
    credentials_vars = [
        'GMAIL_AUTH_REFRESH_TOKEN',
        'GMAIL_AUTH_SALT',
        'GMAIL_AUTH_TOKEN_EXPIRY',
        'GMAIL_USER_EMAIL'
    ]

    for var in credentials_vars:
        if var in os.environ:
            del os.environ[var]

    print("Gmail authentication credentials have been cleared from environment variables.")
    print("Note: You may need to manually remove these variables from your shell configuration file.")