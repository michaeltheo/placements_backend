import logging

from tenacity import retry, wait_fixed, stop_after_attempt
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Twilio client using credentials from settings
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3), reraise=True)
def send_sms(to_phone_number: str, message: str):
    """
    Send an SMS message to a specified phone number with a retry mechanism.

    Parameters:
    - to_phone_number (str): The recipient's phone number.
    - message (str): The message to be sent.

    Retries up to 3 times with a 2-second wait between attempts if an error occurs.
    """
    try:
        # Send the SMS message using the Twilio client
        message = twilio_client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        logger.info(f"SMS sent successfully: {message.sid}")
    except TwilioRestException as e:
        # Log the error and raise the exception to trigger a retry
        logger.error(f"Failed to send SMS: {e}")
        raise


def format_phone_number(phone_number: str) -> str:
    """
    Format the phone number to include the country code for Greece (+30).

    Parameters:
    - phone_number (str): The original phone number.

    Returns:
    - str: The formatted phone number with the country code.
    """
    if not phone_number.startswith("+"):
        # Add the Greek country code (+30) if not already present
        phone_number = f"+30{phone_number.lstrip('0')}"
    return phone_number
