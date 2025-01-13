import os
import re
import time
import logging
from typing import Optional, List
from .auth import check_and_refresh_credentials, get_user_email, set_persistent_env_var
from .email_generator import generate_unique_email
from .email_listener import EmailListener
from .email_parser import extract_token, extract_link, search_by_regex, EmailParserError

class GmailAutomatorError(Exception):
    """Base exception class for GmailAutomator"""
    pass

class GmailAutomator:

    logger = None

    @classmethod
    def _setup_logger(self, verbose: bool):
        logger = logging.getLogger(__name__)
        
        # Check if the logger already has handlers
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            if verbose:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s \n')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            else:
                # This effectively disables all logging output
                logger.addHandler(logging.NullHandler())
                logger.propagate = False
        else:
            # If handlers exist, just update the level and propagation based on verbose
            if verbose:
                logger.setLevel(logging.INFO)
                logger.propagate = True
            else:
                logger.setLevel(logging.CRITICAL)  # Set to a level that won't output anything
                logger.propagate = False

        return logger

    def __init__(self, verbose: bool = False):
        self.credentials = self._authenticate()
        self.listener = None
        self.logger = self._setup_logger(verbose)
    
    def _authenticate(self):
        try:
            return check_and_refresh_credentials()
        except Exception as e:
            raise GmailAutomatorError(f"Authentication failed: {str(e)}")


    def generate_email(self) -> str:
        try:
            user_email = os.environ.get('GMAIL_USER_EMAIL')
            if not user_email:
                user_email = get_user_email(self.credentials)
                if user_email:
                    set_persistent_env_var('GMAIL_USER_EMAIL', user_email)
            
            if not user_email:
                raise ValueError("Unable to retrieve user's email address")
            
            email = generate_unique_email(user_email)
            self.logger.info(f"Generated unique email: {email}")
            return email
        except Exception as e:
            raise GmailAutomatorError(f"Failed to generate unique email: {str(e)}")

   
    def wait_for_email(self, recipient: str, sender: Optional[str] = None, subject: Optional[str] = None, timeout: int = 180) -> Optional[dict]:
        listener = EmailListener(self.credentials, recipient)

        def extract_email(address: str) -> str:
            """Extract the email part from a string like 'Display Name <email@domain.com>'."""
            match = re.search(r'<([^>]+)>', address)
            return match.group(1) if match else address.strip()

        try:
            self.logger.info(f"Waiting for email to {recipient} from {sender or 'any sender'} with subject '{subject or 'any subject'}'")
            listener.start_listening()
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                new_emails = listener.get_new_emails()
                for email in new_emails:
                    email_sender = extract_email(email['sender'])
                    print(f"Extracted sender: {email_sender}")  # Debugging

                    if (not sender or extract_email(sender) == email_sender) and (not subject or email['subject'] == subject):
                        self.logger.info("Matching email received")
                        return email
                time.sleep(5)  # Wait for 5 seconds before checking again
            
            self.logger.warning("No matching email received within the specified timeout")
            return None
        except Exception as e:
            raise GmailAutomatorError(f"Error while waiting for email: {str(e)}")
        finally:
            listener.stop_listening()

    def extract_token(self, email_content: str, pattern: Optional[str] = None, token_length: Optional[int] = None) -> Optional[str]:
        try:
            token = extract_token(email_content, pattern, token_length)
            if token:
                self.logger.info(f"Token extracted: {token}")
            else:
                self.logger.warning("No token found in the email content")
            return token
        except EmailParserError as e:
            raise GmailAutomatorError(f"Failed to extract token: {str(e)}")

    def extract_link(self, email_content: str, domain: Optional[str] = None) -> Optional[str]:
        try:
            link = extract_link(email_content, domain)
            if link:
                self.logger.info(f"Link extracted: {link}")
            else:
                self.logger.warning(f"No link found {f'with domain {domain}' if domain else ''} in the email content")
            return link
        except EmailParserError as e:
            raise GmailAutomatorError(f"Failed to extract link: {str(e)}")

    def search_by_regex(self, email_content: str, pattern: str) -> List[str]:
        try:
            results = search_by_regex(email_content, pattern)
            if results:
                self.logger.info(f"Regex search found {len(results)} matches")
            else:
                self.logger.warning(f"No matches found for pattern: {pattern}")
            return results
        except EmailParserError as e:
            raise GmailAutomatorError(f"Failed to perform regex search: {str(e)}")

    def cleanup(self):
        if self.listener:
            self.listener.stop_listening()
        self.logger.info("Cleanup completed")
    
    @staticmethod
    def update_system_env(var_name, var_value):
        """Update a system environment variable."""
        os.environ[var_name] = var_value