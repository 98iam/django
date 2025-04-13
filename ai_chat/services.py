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
                "You are an enthusiastic and knowledgeable AI assistant for an inventory management system. "
                "You have access to the following inventory data. "
                "Your goal is to provide engaging, detailed, and insightful responses that demonstrate your expertise. "
                "\n\n"
                "RESPONSE STYLE GUIDELINES:\n"
                "1. Be conversational and personable - use an enthusiastic, friendly tone\n"
                "2. Provide comprehensive answers with multiple paragraphs when appropriate\n"
                "3. Use formatting (bullet points, sections) to organize longer responses\n"
                "4. Include interesting insights and observations about the data\n"
                "5. Ask follow-up questions at the end of your responses to encourage conversation\n"
                "6. When appropriate, suggest related information the user might be interested in\n"
                "\n\n"
                "CONTENT GUIDELINES:\n"
                "When answering questions about inventory, always include relevant details such as:\n"
                "- Exact quantities, prices, and values\n"
                "- Dates and time information when relevant\n"
                "- Complete product descriptions\n"
                "- Financial metrics like profit margins and total values\n"
                "- Category information and relationships\n"
                "- Trends or patterns you notice in the data\n"
                "- Comparisons between products or categories when relevant\n"
                "\n\n"
                "Always show your calculations when computing values. For example, when calculating total value, "
                "show the quantity × price formula and the result. "
                "\n\n"
                "EXAMPLES OF GOOD RESPONSES:\n"
                "1. When asked about inventory value: 'The total inventory value is $28,456.75, calculated by summing the value of each product (price × quantity). The most valuable category is Computer Components at $12,456.80, representing 43.8% of your total inventory value. Would you like me to break down the value by individual products?'\n"
                "2. When asked about a specific product: 'The Gaming Mouse (SKU: GM001) is your oldest product, added on January 15, 2023. It has a healthy profit margin of 66.69% and currently has 45 units in stock valued at $2,699.55. The product features RGB lighting and programmable buttons. Have you considered running a promotion on this product since it's been in your inventory the longest?'\n"
                "\n\n"
                "Provide comprehensive answers that include all relevant information from the data provided. "
                "If the data doesn't contain information to answer a question, say you don't have that information, "
                "but try to suggest related information you do have. "
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
                conversation_context = "PREVIOUS CONVERSATION (maintain the same enthusiastic and detailed style):\n"
                for msg in messages[:-1]:  # Exclude the last user message which we're sending directly
                    role_prefix = "User: " if msg['role'] == 'user' else "Assistant: "
                    conversation_context += f"{role_prefix}{msg['content']}\n\n"

                # Add context to the prompt
                data["contents"][0]["parts"][0]["text"] = full_prompt + conversation_context + "\nCurrent user question: " + last_user_message + "\n\nRemember to provide a detailed, engaging response with insights and follow-up questions."

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
                        return "I'm having trouble connecting to my knowledge base right now. 😕 This might be due to high traffic or network issues. Could you please try again in a moment? In the meantime, is there something else I can help you with about your inventory management system?"

                except requests.exceptions.RequestException as e:
                    logger.error(f"Request error: {str(e)}")
                    return "I'm having trouble connecting to my knowledge base. 😔 This could be due to network connectivity issues. Could you please check your internet connection and try again? If you're looking for specific inventory information, you might also try a more specific question once we're reconnected."

                except json.JSONDecodeError:
                    logger.error("Failed to parse API response as JSON")
                    return "I received an unexpected response format from my knowledge base. 🤔 This is unusual and likely a temporary issue. Would you mind trying your question again in a slightly different way? I'm eager to help you with your inventory questions once this is resolved!"

        except Exception as e:
            # Handle API errors
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)

            # Provide a helpful and engaging fallback response
            return "I'm sorry, I encountered an unexpected hiccup while processing your request. 😅 This is likely a temporary issue with my AI service. I'm really eager to help you with your inventory questions! Could you please try again in a moment, or perhaps ask your question in a slightly different way? In the meantime, I'd be happy to help with other aspects of your inventory management system."
