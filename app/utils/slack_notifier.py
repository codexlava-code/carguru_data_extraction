import time, os, hashlib, hmac
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.config.config import settings

class SlackClient:
    def __init__(self):
        """Initialize Slack client with bot token and signing secret."""
        # # Load environment variables from .env.example file
        # load_dotenv()
        self.token = settings.SLACK_BOT_TOKEN
        if not self.token:
            raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
        self.client = WebClient(token=self.token)
        self.signing_secret = settings.SLACK_SIGNING_SECRET

    def send_message(self, message: str, channel_id: str) -> bool:
        """
        Send a message to a Slack channel.

        Args:
            message (str): The message text to send
            channel_id (str): The ID of the channel to send the message to

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            return True
        except SlackApiError as e:
            error_details = {
                'error': str(e.response['error']),
                'response': e.response.data,
                'status_code': e.response.status_code,
                'headers': dict(e.response.headers)
            }
            print("Detailed Slack Error:")
            print(f"Error Type: {error_details['error']}")
            print(f"Status Code: {error_details['status_code']}")
            print(f"Response Data: {error_details['response']}")
            print(f"Headers: {error_details['headers']}")
            return False
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return False

    # Ensures that incoming requests to your microservice actually originate from Slack and haven’t been tampered with.
    # This is critical for security when handling webhooks or API calls from Slack.
    def verify_slack_request(self, timestamp: str, signature: str, body: str) -> bool:
        """
        Verify that the request actually came from Slack.

        Args:
            timestamp (str): X-Slack-Request-Timestamp header
            signature (str): X-Slack-Signature header
            body (str): Raw request body

        Returns:
            bool: True if the request is valid, False otherwise
        """
        if not self.signing_secret:
            print("Warning: SLACK_SIGNING_SECRET not set")
            return False

        # Check if the timestamp is too old
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False

        # Create the signature base string
        sig_basestring = f"v0:{timestamp}:{body}"

        # Calculate the signature
        my_signature = 'v0=' + hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()

        # Compare signatures
        return hmac.compare_digest(my_signature, signature)

# Initialize the Slack client
# slack_obj = SlackClient()