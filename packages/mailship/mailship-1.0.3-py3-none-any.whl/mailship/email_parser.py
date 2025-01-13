# src/gmail_automator/email_parser.py

import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import base64

class EmailParserError(Exception):
    """Custom exception for email parsing errors."""
    pass

logger = logging.getLogger(__name__)

# def extract_token(email_content, token_pattern=None, token_length=None):
#     """
#     Extract a numeric token from the email content.

#     Args:
#         email_content (str): The full content of the email.
#         token_pattern (str, optional): Custom regex pattern to match the token.
#         token_length (int, optional): Expected length of the token.

#     Returns:
#         str: The extracted token, or None if not found.

#     Raises:
#         EmailParserError: If there's an error during token extraction.
#     """
#     print(type(email_content))
#     try:
#         if token_pattern is None:
#             if token_length:
#                 token_pattern = rf'\b\d{{{token_length}}}\b'
#             else:
#                 token_pattern = r'\b\d{1,}\b'

#         matches = re.findall(token_pattern, email_content)
#         print(matches)
#         if not matches:
#             logger.info(f"No token found matching the pattern: {token_pattern}")
#             return None

#         if token_length and all(len(match) != token_length for match in matches):
#             logger.info(f"No token found with the specified length: {token_length}")
#             return None

#         return matches[0]
#     except re.error as e:
#         raise EmailParserError(f"Invalid regex pattern: {str(e)}")
#     except Exception as e:
#         raise EmailParserError(f"Error extracting token: {str(e)}")

def extract_token(email_content, token_pattern=None, token_length=None):
    """
    Extract a numeric token from the email content.

    Args:
        email_content (str): The full content of the email.
        token_pattern (str, optional): Custom regex pattern to match the token.
        token_length (int, optional): Expected length of the token.

    Returns:
        str: The extracted token, or None if not found.

    Raises:
        EmailParserError: If there's an error during token extraction.
    """
    print(type(email_content))
    email_content = str(email_content)
    try:
        if token_pattern is None:
            if token_length:
                # Modified to ensure a space precedes the numeric token
                token_pattern = rf'(?<=\s)\d{{{token_length}}}\b'
            else:
                # Match any block of digits preceded by a space
                token_pattern = r'(?<=\s)\d+\b'

        matches = re.findall(token_pattern, email_content)
        # print(matches)
        if not matches:
            logger.info(f"No token found matching the pattern: {token_pattern}")
            return None

        if token_length and all(len(match) != token_length for match in matches):
            logger.info(f"No token found with the specified length: {token_length}")
            return None

        return matches[0]
    except re.error as e:
        raise EmailParserError(f"Invalid regex pattern: {str(e)}")
    except Exception as e:
        raise EmailParserError(f"Error extracting token: {str(e)}")

def extract_link(email_data, domain=None):
    """
    Extracts links from the email data, prioritizing structured content (decoded HTML).
    If the content is unstructured (plain string), it falls back to regex.

    Args:
        email_data (str or dict): The email content, either as a dictionary with `decoded_content`
                                  or as a plain string.
        domain (str, optional): The domain to filter links by.

    Returns:
        list: A list of links that match the specified domain, or all found links if no domain is specified.
    """
    try:
        links = []

        # Determine the type of email_data and create both dictionary and string representations
        if isinstance(email_data, dict):
            email_dict = email_data
            email_str = email_data.get('decoded_content', {}).get('text', '') + ' ' + email_data.get('snippet', '')
        elif isinstance(email_data, str):
            email_str = email_data
            email_dict = {'decoded_content': {'text': email_data}}
        else:
            raise EmailParserError("Unsupported email data format. Expected dict or str.")

        # Try to extract link from the structured dictionary first (HTML content)
        if 'decoded_content' in email_dict and 'link' in email_dict['decoded_content']:
            links.append(email_dict['decoded_content']['link'])

        # Fallback to regex if no HTML-extracted link is present
        if not links:
            link_pattern = r'http[s]?://[^\s]+'
            regex_links = re.findall(link_pattern, email_str)
            links.extend(regex_links)

        # Filter links by the specified domain, if provided
        if domain:
            filtered_links = []
            for link in links:
                parsed_link = urlparse(link)
                if parsed_link.netloc.endswith(domain):  # Matches the specified domain
                    filtered_links.append(link)
            links = filtered_links

        # Ensure links are unique
        unique_links = list(set(links))
        if(len(unique_links)> 1):
            print(f"There are {str(len(unique_links))} links found in the email. Only the first will be returned. Please use domain parameter to ensure you get the right link.")
        return unique_links[0]

    except Exception as e:
        raise EmailParserError(f"Error extracting link: {str(e)}")

def search_by_regex(email_content, pattern):
    """
    Search the email content using a regex pattern.

    Args:
        email_content (str): The full content of the email.
        pattern (str): The regex pattern to search for.

    Returns:
        list: All matches found in the email content.

    Raises:
        EmailParserError: If there's an error during the regex search.
    """
    email_content=str(email_content)
    try:
        matches = re.findall(pattern, email_content)
        if not matches:
            logger.info(f"No matches found for pattern: {pattern}")
        return matches
    except re.error as e:
        raise EmailParserError(f"Invalid regex pattern: {str(e)}")
    except Exception as e:
        raise EmailParserError(f"Error performing regex search: {str(e)}")

def get_email_body(email_data):
    """
    Extract the email body from the email data returned by the Gmail API.

    Args:
        email_data (dict): The email data returned by the Gmail API.

    Returns:
        str: The email body.

    Raises:
        EmailParserError: If there's an error extracting the email body.
    """
    try:
        parts = email_data['payload'].get('parts', [])
        body = email_data['payload'].get('body', {}).get('data', '')
        
        if not body and parts:
            for part in parts:
                if part['mimeType'] in ['text/plain', 'text/html']:
                    body = part['body'].get('data', '')
                    break
        
        if body:
            # The body is base64url encoded, so we need to decode it
            return base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8')
        else:
            logger.warning("No email body found")
            return ''
    except Exception as e:
        raise EmailParserError(f"Error extracting email body: {str(e)}")