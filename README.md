# Pressroom

[//]: # (<img src="resources/pressroom_logo.PNG" alt="Pressroom Logo" width="240" height="240" />)

## Setup Instructions

1. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following content:
```
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
```

4. Chrome WebDriver Setup:
- Make sure you have Google Chrome installed
- The Chrome WebDriver is automatically managed by Selenium 4.x+

## Usage

### Sending Slack Messages
```python
from slack_utils import SlackClient

slack = SlackClient()
success = slack.send_message(
    message="Test message",
    channel_id="C0123456789"  # Replace with your channel ID
)
```

### Verifying Slack Requests
```python
from slack_utils import SlackClient

slack = SlackClient()
is_valid = slack.verify_slack_request(
    timestamp="1234567890",  # X-Slack-Request-Timestamp header
    signature="v0=abcdef...", # X-Slack-Signature header
    body="raw_request_body"   # Raw request body
)
```

### Web Scraping with Selenium
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: run in headless mode

driver = webdriver.Chrome(options=chrome_options)
# Use driver for web scraping
driver.quit()  # Don't forget to quit the driver when done
```

## Environment Variables

// should we remove this?
- `SLACK_BOT_TOKEN`: Your Slack Bot User OAuth Token (starts with `xoxb-`)
  - Get this from: https://api.slack.com/apps > OAuth & Permissions
  - Required scopes: `chat:write`
- `SLACK_SIGNING_SECRET`: Your Slack Signing Secret
  - Get this from: https://api.slack.com/apps > Basic Information > App Credentials
  - Used to verify that requests come from Slack

## Project Structure

- `slack_utils.py`: Utilities for sending messages to Slack and verifying Slack requests
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (not tracked in git)

## Notes

- Make sure to never commit your `.env` file or any sensitive tokens to version control
- Always activate your virtual environment before running the project
- Keep your dependencies up to date for security and stability
- The signing secret is used to verify incoming requests from Slack
- The bot token is still required for sending messages to Slack