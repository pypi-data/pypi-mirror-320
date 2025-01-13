import os
import sys
import base64
import subprocess
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import platform
from getpass import getpass
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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
    except Exception as e:
        print(f"Decryption failed: {e}")
        raise

def set_persistent_env_var(env_var_name, env_var_value, overwrite=False):
    current_os = platform.system()

    # Check if the variable already exists
    existing_value = os.environ.get(env_var_name)
    if existing_value and not overwrite:
        print(f"{env_var_name} already exists. Current value: {existing_value}")
        update = input(f"Do you want to overwrite {env_var_name}? (y/n): ").lower().strip()
        if update != 'y':
            print(f"Keeping existing value for {env_var_name}")
            return

    if current_os in ["Darwin", "Linux"]:
        home_dir = os.path.expanduser("~")
        shell_files = [".bashrc", ".zshrc", ".bash_profile", ".profile"]

        for shell_file in shell_files:
            full_path = os.path.join(home_dir, shell_file)
            if os.path.exists(full_path):
                with open(full_path, 'r') as file:
                    lines = file.readlines()

                var_exists = False
                for i, line in enumerate(lines):
                    if line.strip().startswith(f'export {env_var_name}='):
                        lines[i] = f'export {env_var_name}="{env_var_value}"\n'
                        var_exists = True
                        break

                if not var_exists:
                    lines.append(f'\nexport {env_var_name}="{env_var_value}"\n')

                with open(full_path, 'w') as file:
                    file.writelines(lines)

                print(f"Updated {env_var_name} in {full_path}")
                break
        else:
            print(f"No suitable shell config file found. Please manually set {env_var_name}.")
    
    elif current_os == "Windows":
        set_env_cmd = f'[System.Environment]::SetEnvironmentVariable("{env_var_name}", "{env_var_value}", "User")'
        subprocess.run(["powershell", "-Command", set_env_cmd], check=True)
        print(f"Set {env_var_name} in Windows environment variables.")
    
    else:
        print(f"Unsupported operating system: {current_os}")
    
    os.environ[env_var_name] = env_var_value


def refresh_tokens(client_id, client_secret):
    """Refreshes expired tokens using the stored refresh token."""
    try:
        refresh_token = os.environ.get("GMAIL_AUTH_REFRESH_TOKEN")
        salt = base64.b64decode(os.environ.get("GMAIL_AUTH_SALT"))
        key = get_encryption_key(client_id, salt)
        decrypted_refresh_token = decrypt_value(refresh_token, key)

        creds = Credentials(
            None,
            refresh_token=decrypted_refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            set_persistent_env_var(
                "GMAIL_AUTH_REFRESH_TOKEN", encrypt_value(creds.refresh_token, key)
            )
            set_persistent_env_var(
                "GMAIL_AUTH_TOKEN_EXPIRY", creds.expiry.isoformat()
            )
            print("Tokens refreshed successfully.")
        else:
            print("Tokens are still valid.")

    except Exception as e:
        print(f"Failed to refresh tokens: {e}")

def setup_cron_job():
    """Sets up a cron job to refresh Gmail tokens every hour and source .bashrc."""
    script_path = os.path.abspath(__file__)
    cron_command = f"0 * * * * python {script_path} --refresh-tokens && source ~/.bashrc"

    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=True)
        existing_crontab = result.stdout
    except subprocess.CalledProcessError:
        existing_crontab = ""

    if cron_command in existing_crontab:
        print("Cron job already exists.")
    else:
        new_crontab = existing_crontab + f"\n{cron_command}\n"
        subprocess.run(["crontab"], input=new_crontab, text=True, check=True)
        print("Cron job added to refresh tokens every hour and source .bashrc.")

def setup_windows_task():
    """Sets up a Windows Task Scheduler job to refresh tokens every hour."""
    python_path = os.path.abspath(sys.executable)
    script_path = os.path.abspath(__file__)
    task_name = "RefreshGmailTokens"
    command = f'SchTasks /Create /SC HOURLY /TN "{task_name}" /TR "{python_path} {script_path} --refresh-tokens" /F'

    try:
        subprocess.run(["powershell", "-Command", command], check=True)
        print(f"Scheduled task '{task_name}' added to refresh tokens every hour.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add scheduled task: {e}")

def refresh_windows_env():
    """Refresh environment variables in the Windows registry."""
    try:
        command = '[System.Environment]::SetEnvironmentVariable("GMAIL_CLIENT_ID", $env:GMAIL_CLIENT_ID, "User"); ' \
                  '[System.Environment]::SetEnvironmentVariable("GMAIL_CLIENT_SECRET", $env:GMAIL_CLIENT_SECRET, "User"); ' \
                  '[System.Environment]::SetEnvironmentVariable("GMAIL_AUTH_REFRESH_TOKEN", $env:GMAIL_AUTH_REFRESH_TOKEN, "User"); ' \
                  '[System.Environment]::SetEnvironmentVariable("GMAIL_AUTH_SALT", $env:GMAIL_AUTH_SALT, "User")'
        subprocess.run(["powershell", "-Command", command], check=True)
        print("Windows environment variables refreshed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to refresh Windows environment variables: {e}")

def main():
    print("Welcome to the Gmail Automator setup!")
    print("Please look at the video to understand a base setup -- https://drive.google.com/file/d/1Q31YA-uUEN39PQArz2TEhughpsqm_zxi/view?usp=sharing ")
    client_id = input("Enter your Google OAuth Client ID: ")
    client_secret = getpass("Enter your Google OAuth Client Secret: ")

    set_persistent_env_var('GMAIL_CLIENT_ID', client_id, overwrite=True)
    set_persistent_env_var('GMAIL_CLIENT_SECRET', client_secret, overwrite=True)

    flow = Flow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=[
            'openid',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/userinfo.email'
        ],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    print(f"\nPlease visit this URL to authorize the application: {auth_url}")
    auth_code = input("Enter the authorization code: ")
    
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        user_email = get_user_email(creds)
        if user_email:
            set_persistent_env_var('GMAIL_USER_EMAIL', user_email, overwrite=True)
        
        salt = os.urandom(16)
        key = get_encryption_key(client_id, salt)
        set_persistent_env_var('GMAIL_AUTH_SALT', base64.b64encode(salt).decode(), overwrite=True)
        set_persistent_env_var('GMAIL_AUTH_REFRESH_TOKEN', encrypt_value(creds.refresh_token, key), overwrite=True)
        set_persistent_env_var('GMAIL_AUTH_TOKEN_EXPIRY', creds.expiry.isoformat(), overwrite=True)
        
        print("\nSetup completed successfully!")
        print("All necessary credentials have been stored as environment variables.\n")
        print("You can now use the Gmail Automator in your projects.")
        print("If you want to deploy to a pipeline, Please create the following repository secrets")
        print(f"\033[95mGMAIL_CLIENT_ID: {client_id}\033[0m")
        print(f"\033[95mGMAIL_CLIENT_SECRET: {client_secret}\033[0m")
        print(f"\033[95mGMAIL_USER_EMAIL: {user_email}\033[0m")
        print(f"\033[95mGMAIL_AUTH_SALT: {str(base64.b64encode(salt).decode())}\033[0m")
        print(f"\033[95mGMAIL_AUTH_REFRESH_TOKEN: {str(encrypt_value(creds.refresh_token, key))}\033[0m")
        print(f"\033[95mGMAIL_AUTH_TOKEN_EXPIRY: {str(creds.expiry.isoformat())}\033[0m")

    except Exception as e:
        print(f"Failed to complete setup: {str(e)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gmail Token Setup and Refresh Script")
    parser.add_argument(
        "--refresh-tokens",
        action="store_true",
        help="Refresh tokens if they are expired.",
    )
    parser.add_argument(
        "--setup-cron",
        action="store_true",
        help="Set up a cron job to refresh tokens every hour (Linux).",
    )
    parser.add_argument(
        "--setup-task",
        action="store_true",
        help="Set up a scheduled task to refresh tokens every hour (Windows).",
    )

    args = parser.parse_args()

    # Check which argument was passed
    if args.setup_cron:
        main()
        setup_cron_job()
    elif args.setup_task:
        main()
        setup_windows_task()
    elif args.refresh_tokens:
        client_id = os.environ.get("GMAIL_CLIENT_ID")
        client_secret = os.environ.get("GMAIL_CLIENT_SECRET")
        if not client_id or not client_secret:
            print("Client ID and Client Secret must be set in environment variables.")
        else:
            refresh_tokens(client_id, client_secret)

            if sys.platform in ["linux", "darwin"]:
                subprocess.run(["bash", "-c", "source ~/.bashrc"])

            elif sys.platform == "win32":
                refresh_windows_env()
    else:
        # No arguments provided, default to running `main()`
        main()
