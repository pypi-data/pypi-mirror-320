import time
import base64
import threading
import logging
from bs4 import BeautifulSoup
from queue import Queue
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request

class EmailListenerError(Exception):
    """Custom exception for email listener errors."""
    pass

class EmailListener:
    def __init__(self, credentials, target_email):
        self.credentials = credentials
        self.target_email = target_email
        self.service = build('gmail', 'v1', credentials=credentials)
        self.is_listening = False
        self.quota_units = 0
        self.quota_reset_time = time.time()
        self.logger = logging.getLogger(__name__)
        self.email_queue = Queue()

    def start_listening(self):
        """Start listening for new emails in a separate thread."""
        self.is_listening = True
        self.thread = threading.Thread(target=self._listen)
        self.thread.start()

    def stop_listening(self):
        """Stop the email listening process."""
        self.is_listening = False
        if hasattr(self, 'thread'):
            self.thread.join()

    def _listen(self):
        """Listen for new emails sent to the target email address."""
        history_id = None

        while self.is_listening:
            try:
                if not history_id:
                    # Fetch the user's profile and the initial history ID
                    profile = self._make_api_call(self.service.users().getProfile(userId='me').execute)
                    history_id = profile['historyId']
                    
                    # Fetch the latest messages directly to avoid missing emails
                    messages = self._make_api_call(self.service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute)
                    if 'messages' in messages:
                        for message in messages['messages']:
                            msg = self._make_api_call(self.service.users().messages().get(userId='me', id=message['id']).execute)
                            if self._is_target_recipient(msg):
                                processed_email = self.process_new_email(msg)
                                self.email_queue.put(processed_email)

                # Use the history API to fetch changes since the last history ID
                results = self._make_api_call(
                    self.service.users().history().list(userId='me', startHistoryId=history_id, labelId='INBOX').execute
                )
                changes = results.get('history', [])

                for change in changes:
                    for message in change.get('messagesAdded', []):
                        msg = self._make_api_call(
                            self.service.users().messages().get(userId='me', id=message['message']['id']).execute
                        )
                        # print(msg)
                        if self._is_target_recipient(msg):
                            processed_email = self.process_new_email(msg)
                            self.email_queue.put(processed_email)

                # Update history ID to the latest value after processing the changes
                if changes:
                    history_id = changes[-1]['id']

            except HttpError as error:
                self.logger.error(f'An error occurred: {error}')
                if error.resp.status == 404:
                    history_id = None  # Reset the history ID and retry
                else:
                    raise
            except RefreshError:
                self.logger.error("Credentials have expired. Attempting to refresh.")
                if not self.credentials.refresh(Request()):
                    raise EmailListenerError("Failed to refresh credentials.")
                self.service = build('gmail', 'v1', credentials=self.credentials)

            time.sleep(3)  # Poll more frequently to avoid missing messages

    def _make_api_call(self, api_func):
        """Make an API call with rate limiting."""
        current_time = time.time()
        if current_time - self.quota_reset_time >= 1:
            self.quota_units = 0
            self.quota_reset_time = current_time

        if self.quota_units >= 250:
            sleep_time = 1 - (current_time - self.quota_reset_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.quota_units = 0
            self.quota_reset_time = time.time()

        result = api_func()
        self.quota_units += 2  # Assuming 2 quota units per call, adjust as needed
        return result

    def _is_target_recipient(self, msg):
        """Check if the email was sent to the target email address (To, CC, or BCC)."""
        try:
            headers = msg['payload']['headers']

            # Collect emails from "To", "CC", and "BCC" headers
            recipient_headers = [
                header['value'] for header in headers
                if header['name'].lower() in ['to', 'cc', 'bcc']
            ]

            # Debugging: Print the raw recipient headers
            # print(f"Recipient headers: {recipient_headers}")

            # Split and normalize all recipients
            recipients = [
                email.strip().lower()
                for header in recipient_headers
                for email in header.split(',')
            ]

            # Debugging: Print the full list of parsed recipients
            # print(f"All parsed recipients: {recipients}")

            # Check if the target email is in the list
            return self.target_email.lower() in recipients
        except Exception as e:
            print(f"Error in _is_target_recipient: {e}")
            return False


    def decode_base64(self, content):
        """Decode base64 content."""
        return base64.urlsafe_b64decode(content).decode('utf-8')

    def extract_html_part(self, email_data):
        """Extract and decode the HTML part of a multipart email."""
        for part in email_data.get('parts', []):
            if part['mimeType'] == 'text/html':
                # Found HTML part, decode and return it
                return self.decode_base64(part['body']['data'])
        return None

    def extract_link_from_html(self, html_content):
        """Extract the first link from the HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]
        return links[0] if links else None

    def extract_text_from_html(self, html_content):
        """Extract the text content from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    def process_new_email(self, email_data):
        """
        Process a newly received email.

        Args:
            email_data (dict): The email data received from the Gmail API.

        Returns:
            dict: Processed email information with decoded content.
        """
        # Extract the subject and sender
        subject = next((header['value'] for header in email_data['payload']['headers'] if header['name'].lower() == 'subject'), 'No Subject')
        sender = next((header['value'] for header in email_data['payload']['headers'] if header['name'].lower() == 'from'), 'Unknown Sender')
        
        # Extract the HTML part and decode it
        html_content = self.extract_html_part(email_data['payload'])
        
        # Initialize decoded content
        decoded_content = {}
        
        if html_content:
            # Extract the link from the HTML content
            link = self.extract_link_from_html(html_content)
            # Extract the plain text from the HTML content
            text = self.extract_text_from_html(html_content)
            
            decoded_content['link'] = link
            decoded_content['text'] = text

        # Build the processed email dictionary
        processed_email = {
            'id': email_data['id'],
            'subject': subject,
            'sender': sender,
            'snippet': email_data.get('snippet', ''),
            'decoded_content': decoded_content  # Add the decoded content (link and text)
        }

        self.logger.info(f"New email processed: {processed_email['subject']} from {processed_email['sender']}")
        return processed_email

    def get_new_emails(self):
        """Get all new emails that have been received."""
        emails = []
        while not self.email_queue.empty():
            emails.append(self.email_queue.get())
        return emails