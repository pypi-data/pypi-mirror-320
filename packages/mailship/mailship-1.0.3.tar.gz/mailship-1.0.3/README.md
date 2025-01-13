# MailShip 

MailShip is a Python library designed to simplify Gmail-related automation tasks. It is developer-friendly and ideal for testing or automation scenarios involving email interactions.

## Features

- Generate unique email addresses for testing
- Wait for and retrieve emails automatically
- Extract tokens and links from email content
- Perform regex-based searches on email content
- Integrate seamlessly with Selenium and other frameworks
- Supports CI/CD workflows with GitHub Actions
- Flexible logging options for better debugging

## Pip Package

For the Python Package on PIP, visit the [PIP Project](https://pypi.org/project/mailship/).

## Configuration

Before using MailShip, you need to set up a Google Cloud project and configure OAuth credentials. Follow the steps below:

### Step 1: Create a Google Cloud Project

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project selector at the top and choose "New Project."
3. Enter a name for your project (e.g., "MailShip") and click "Create."
4. Select your new project from the project dropdown once it's created.

### Step 2: Enable the Gmail API

1. Go to "APIs & Services" > "Library" in the left sidebar.
2. Search for "Gmail API" and select it.
3. Click "Enable" to activate the API for your project.

### Step 3: Configure the OAuth Consent Screen

1. Navigate to "APIs & Services" > "OAuth consent screen."
2. Select "External" (or "Internal" for Google Workspace accounts).
3. Fill in the following fields:
   - **App Name**: MailShip
   - **User Support Email**: Your email address
   - **Developer Contact Information**: Your email address
4. Add these required scopes on the "Scopes" page:
   - https://www.googleapis.com/auth/gmail.readonly
   - https://www.googleapis.com/auth/userinfo.email
5. Save the settings and add your Gmail account under "Test Users."

### Step 4: Create an OAuth 2.0 Client ID

1. Go to "APIs & Services" > "Credentials."
2. Click "Create Credentials" > "OAuth client ID."
3. Choose "Desktop app" as the application type.
4. Name the client (e.g., "MailShip Desktop Client") and click "Create."
5. Download the `client_secrets.json` file and place it in your project directory.

### Step 5: Run the Setup Script

Run one of the following setup script to configure MailShip:

### Option 1: Setup Gmail Authentication

Run the following command to set up your Gmail API credentials without automatic token refreshing setup. 

   ```bash
   python setup_auth.py
   ```
This will guide you through authentication and save credentials.

 **Note: Refresh Tokens Only**:
   ```bash
   python setup_auth.py --refresh-tokens
   ```
   - Use this command to refresh tokens manually.

### Option 2: Set Up Automatic Token Refreshing (Linux)

- To set up a **cron job** (Linux/macOS) for automatic token refreshing, run:

   - **Linux/macOS (Cron Job)**:
     ```bash
     python setup_auth.py --setup-cron
     ```
     - Creates a cron job to refresh tokens hourly.
   
### Option 3: Set Up Automatic Token Refreshing (Windows)

- To set up a **scheduled task** (Windows), run:

   - **Windows (Task Scheduler)**:
     ```bash
     python setup_auth.py --setup-task
     ```
     - Creates a scheduled task for automatic token refresh.

### CI/CD Integration

To refresh tokens during CI/CD workflows, add this step to your GitHub Actions configuration:

```yaml
- name: Refresh Tokens
  env:
    GMAIL_CLIENT_ID: ${{ secrets.GMAIL_CLIENT_ID }}
    GMAIL_CLIENT_SECRET: ${{ secrets.GMAIL_CLIENT_SECRET }}
    GMAIL_AUTH_REFRESH_TOKEN: ${{ secrets.GMAIL_AUTH_REFRESH_TOKEN }}
    GMAIL_AUTH_SALT: ${{ secrets.GMAIL_AUTH_SALT }}
  run: python setup_auth.py --refresh-tokens
```

This ensures that tokens remain active during automated pipelines.

## Usage

Here's a simple example of how to use MailShip:

```python
from mailship import GmailAutomator

def run_example():
    automator = GmailAutomator(verbose=True)  # Set verbose=True for detailed logs
    
    try:
        email = automator.generate_email()
        print(f"Generated email: {email}")
        
        print("Waiting for an email (timeout: 60 seconds)...")
        received_email = automator.wait_for_email(email, timeout=60)
        
        if received_email:
            print(f"Received email: {received_email['subject']}")
            token = automator.extract_token(received_email)
            link = automator.extract_link(received_email)
            print(f"Extracted token: {token}")
            print(f"Extracted link: {link}")
            
            # Perform a regex search
            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = automator.search_by_regex(received_email['decoded_content']['text'], pattern)
            print(f"Found emails: {emails}")
        else:
            print("No email received within the timeout period.")
    
    finally:
        automator.cleanup()

if __name__ == "__main__":
    run_example()
```

## Key Functions

1. **`generate_email()`**:
   - Returns a unique email address for testing.

2. **`wait_for_email(recipient, sender=None, subject=None, timeout=180)`**:
   - Waits for an email matching the given criteria.

3. **`extract_token(email_content, pattern=None, token_length=None)`**:
   - Extracts a token from the email body based on a regex pattern or token length.

4. **`extract_link(email_content, domain=None)`**:
   - Extracts a link from the email content, optionally filtered by domain.

5. **`search_by_regex(email_content, pattern)`**:
   - Performs a custom regex search on email content.

## Integration with Selenium

MailShip integrates seamlessly with Selenium and Playwright for testing workflows involving email interactions. Use MailShip to generate email addresses, validate email content, and automate form submissions in conjunction with Selenium WebDriver.

## CI/CD with GitHub Actions

To set up MailShip in a CI/CD pipeline:

1. Add a `.github/workflows/gmail_automation.yml` file to your repository.
2. Include MailShip-related secrets in your repository settings:
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`
   - `GMAIL_USER_EMAIL`
   - `GMAIL_AUTH_REFRESH_TOKEN`
   - `GMAIL_AUTH_SALT`
3. Use this YAML template:

```yaml
name: Gmail Automation
on:
  push:
    branches:
      - main

jobs:
  automation:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Refresh Tokens
        env:
          GMAIL_CLIENT_ID: ${{ secrets.GMAIL_CLIENT_ID }}
          GMAIL_CLIENT_SECRET: ${{ secrets.GMAIL_CLIENT_SECRET }}
          GMAIL_AUTH_REFRESH_TOKEN: ${{ secrets.GMAIL_AUTH_REFRESH_TOKEN }}
          GMAIL_AUTH_SALT: ${{ secrets.GMAIL_AUTH_SALT }}
        run: python setup_auth.py --refresh-tokens

      - name: Run tests
        run: pytest
```

## Contributing

We welcome contributions to MailShip! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeatureName`).
3. Commit your changes (`git commit -m 'Add YourFeatureName'`).
4. Push the branch (`git push origin feature/YourFeatureName`).
5. Open a Pull Request on GitHub.

## Reporting Issues

If you encounter any issues or have suggestions, open an issue on GitHub with the following details:
- Steps to reproduce the issue
- Expected and actual behavior
- Any error messages or logs

## License

This project is licensed under a Custom Repository License. Refer to the [LICENSE](LICENSE) file for details.

## Contact

For inquiries or support:
- **Twitter**: [@OluwaseyiAjadi4](https://twitter.com/OluwaseyiAjadi4)
- **LinkedIn**: [Oluwaseyi Ajadi](https://www.linkedin.com/in/oluwaseyi-ajadi/)
