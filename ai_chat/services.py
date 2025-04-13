import requests
import json
from django.conf import settings
import logging

# Import inventory context
from .inventory_context import InventoryContext

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

    def generate_response(self, messages, user=None):
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

            # Get relevant inventory context based on the user's message
            try:
                # Pass the user to filter products by this user's account
                inventory_context = InventoryContext.get_relevant_context(last_user_message, user=user)
                logger.info(f"Retrieved inventory context: {len(inventory_context)} characters")
                if inventory_context:
                    logger.debug(f"Inventory context preview: {inventory_context[:100]}...")
            except Exception as e:
                logger.error(f"Error getting inventory context: {str(e)}")
                inventory_context = "Error retrieving inventory data."

            # Create system instructions
            system_instructions = (
                "You are an AI assistant for an inventory management system. "
                "You have access to the following inventory data. "
                "Use this data to provide accurate, detailed, and helpful responses. "
                "When answering questions about inventory, always include relevant details such as:"
                "- Exact quantities, prices, and values"
                "- Dates and time information when relevant"
                "- Complete product descriptions"
                "- Financial metrics like profit margins and total values"
                "- Category information and relationships"
                "\n\n"
                "Always show your calculations when computing values. For example, when calculating total value, "
                "show the quantity × price formula and the result. "
                "\n\n"
                "Provide comprehensive answers that include all relevant information from the data provided. "
                "If the data doesn't contain information to answer a question, say you don't have that information. "
                "Do not make up information that isn't in the provided data."
            )

            # Prepare the full prompt with system instructions and inventory context
            full_prompt = f"{system_instructions}\n\n"

            # Always include inventory context, even if it's an error message
            full_prompt += f"INVENTORY DATA:\n{inventory_context}\n\n"

            # Prepare the request data
            data = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt + last_user_message
                    }]
                }]
            }

            # Add conversation history context if available
            if len(messages) > 1:
                # Create a context message from previous exchanges
                conversation_context = "Previous conversation:\n"
                for msg in messages[:-1]:  # Exclude the last user message which we're sending directly
                    role_prefix = "User: " if msg['role'] == 'user' else "Assistant: "
                    conversation_context += f"{role_prefix}{msg['content']}\n"

                # Add context to the prompt
                data["contents"][0]["parts"][0]["text"] = full_prompt + conversation_context + "\nCurrent message: " + last_user_message

            logger.info(f"Sending request to Gemini API with model {self.model_name}")

            # Make the API request with timeout and retry
            max_retries = 2
            retry_count = 0
            while retry_count <= max_retries:
                try:
                    logger.info(f"Sending request to Gemini API (attempt {retry_count + 1})")
                    response = requests.post(
                        f"{self.api_url}?key={self.api_key}",
                        headers=self.headers,
                        data=json.dumps(data),
                        timeout=30  # 30 second timeout
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

                except requests.exceptions.Timeout:
                    retry_count += 1
                    if retry_count <= max_retries:
                        logger.warning(f"Request timed out. Retrying ({retry_count}/{max_retries})...")
                    else:
                        return "I'm having trouble connecting to my knowledge base right now. Please try again in a moment."

                except requests.exceptions.RequestException as e:
                    logger.error(f"Request error: {str(e)}")
                    return "I'm having trouble connecting to my knowledge base. Please check your internet connection and try again."

                except json.JSONDecodeError:
                    logger.error("Failed to parse API response as JSON")
                    return "I received an invalid response from my knowledge base. Please try again later."

        except Exception as e:
            # Handle API errors
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)

            # Provide a helpful fallback response
            return "I'm sorry, I encountered an error while processing your request. This might be due to a temporary issue with my AI service. Please try again in a moment, or ask a different question."
