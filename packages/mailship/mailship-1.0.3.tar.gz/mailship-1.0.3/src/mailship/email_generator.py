import json
import os
import random
import string
from datetime import datetime

class EmailGenerationError(Exception):
    """Custom exception for email generation errors."""
    pass

def generate_unique_email(base_email):
    """
    Generate a unique email address based on the user's Gmail address.

    Args:
        base_email (str): The user's Gmail address.

    Returns:
        str: A unique email address.
    """
    local_part, domain = base_email.split('@')
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # No colons in the timestamp
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{local_part}+{timestamp}{random_string}@{domain}"

def store_generated_email(email, timestamp):
    """
    Store the generated email in a JSON file in the current project directory.

    Args:
        email (str): The generated email address.
        timestamp (datetime): The timestamp when the email was generated.

    Raises:
        EmailGenerationError: If there's an error writing to the file.
    """
    project_dir = os.getcwd()
    file_path = os.path.join(project_dir, 'generated_emails.json')
    
    try:
        data = get_stored_emails()
        data.append({
            'email': email,
            'timestamp': timestamp.isoformat()
        })
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except (IOError, OSError, json.JSONDecodeError) as e:
        raise EmailGenerationError(f"Error storing generated email: {str(e)}")

def get_stored_emails():
    """
    Retrieve the list of previously generated emails.

    Returns:
        list: A list of dictionaries containing email addresses and their generation timestamps.

    Raises:
        EmailGenerationError: If there's an error reading the file.
    """
    project_dir = os.getcwd()
    file_path = os.path.join(project_dir, 'generated_emails.json')
    
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (IOError, OSError, json.JSONDecodeError) as e:
        raise EmailGenerationError(f"Error reading stored emails: {str(e)}")

def is_valid_generated_email(email):
    """
    Check if a generated email is valid (contains only alphanumeric characters after the +).

    Args:
        email (str): The email address to check.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    local_part, domain = email.split('@')
    if '+' not in local_part:
        return False
    
    base, unique_part = local_part.split('+')
    return unique_part.isalnum()

def generate_email(base_email):
    """
    Generate a unique email and ensure it's valid.

    Args:
        base_email (str): The user's Gmail address.

    Returns:
        str: A unique, valid email address.

    Raises:
        EmailGenerationError: If unable to generate a valid email after multiple attempts.
    """
    max_attempts = 10
    for _ in range(max_attempts):
        new_email = generate_unique_email(base_email)
        if is_valid_generated_email(new_email):
            return new_email
    raise EmailGenerationError("Unable to generate a valid email after multiple attempts.")

def email_exists(email):
    """
    Check if an email already exists in the stored emails.

    Args:
        email (str): The email address to check.

    Returns:
        bool: True if the email exists, False otherwise.
    """
    stored_emails = get_stored_emails()
    return any(stored_email['email'] == email for stored_email in stored_emails)

def clear_stored_emails():
    """
    Clear or delete the stored emails JSON file.

    Raises:
        EmailGenerationError: If there's an error deleting the file.
    """
    project_dir = os.getcwd()
    file_path = os.path.join(project_dir, 'generated_emails.json')
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print("Stored emails file has been deleted.")
        except (IOError, OSError) as e:
            raise EmailGenerationError(f"Error deleting stored emails file: {str(e)}")
    else:
        print("No stored emails file found.")