import requests
import json
from django.conf import settings
import logging

# Get logger
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is not set")

        # Check if a specific model is specified in settings
        specified_model = settings.GEMINI_MODEL
        if specified_model:
            self.model_name = specified_model
        else:
            # Default to gemini-1.5-flash as in your working example
            self.model_name = 'gemini-1.5-flash'

        logger.info(f"Using model: {self.model_name}")

        # Set up the API URL
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

        # Set up headers
        self.headers = {
            "Content-Type": "application/json"
        }

    def generate_response(self, messages):
        """
        Generate a response from the Gemini model based on the conversation history.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys

        Returns:
            The generated response text
        """
        try:
            # Get the last user message
            last_user_message = None
            for message in reversed(messages):
                if message['role'] == 'user':
                    last_user_message = message['content']
                    break

            if not last_user_message:
                logger.warning("No user message found in history")
                return "I couldn't understand your request. Please try again."

            # Prepare the request data
            data = {
                "contents": [{
                    "parts": [{
                        "text": last_user_message
                    }]
                }]
            }

            # Add conversation history context if available
            if len(messages) > 1:
                # Create a context message from previous exchanges
                context = "Previous conversation:\n"
                for msg in messages[:-1]:  # Exclude the last user message which we're sending directly
                    role_prefix = "User: " if msg['role'] == 'user' else "Assistant: "
                    context += f"{role_prefix}{msg['content']}\n"

                # Add context to the prompt
                data["contents"][0]["parts"][0]["text"] = context + "\nCurrent message: " + last_user_message

            logger.info(f"Sending request to Gemini API with model {self.model_name}")

            # Make the API request
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=self.headers,
                data=json.dumps(data)
            )

            # Process the response
            response_json = response.json()
            logger.info(f"Received response from Gemini API: {response.status_code}")

            if response.status_code == 200 and 'candidates' in response_json and len(response_json['candidates']) > 0:
                return response_json['candidates'][0]['content']['parts'][0]['text']
            else:
                error_msg = f"Error from Gemini API: {response_json.get('error', {}).get('message', 'Unknown error')}"
                logger.error(error_msg)
                return error_msg

        except Exception as e:
            # Handle API errors
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)
            return error_msg
