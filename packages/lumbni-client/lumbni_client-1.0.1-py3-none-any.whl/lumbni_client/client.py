import requests
from .exceptions import LumbniApiError

class LumbniClient:
    def __init__(self, api_key: str, mode: str = "dev"):
        self.api_key = api_key
        self.mode = mode
        
        # Set the base URL based on the mode (dev or prod)
        if self.mode == "prod":
            self.base_url = "https://load.lumbni.tech"
        else:
            self.base_url = "https://api.lumbni.tech:8000"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, data: dict = None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, json=data, headers=self.headers)
            response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            # Capture detailed info about the error
            error_message = f"HTTP error occurred: {http_err}"
            error_code = response.status_code
            error_details = response.text if response.text else "No details available"
            
            # Raise a more informative exception
            raise LumbniApiError(
                f"{error_message} - Status Code: {error_code}. Response: {error_details}"
            )
        except requests.exceptions.RequestException as req_err:
            # Handle any non-HTTP errors (network issues, etc.)
            raise LumbniApiError(f"Request error occurred: {req_err}")
        except Exception as err:
            # Any other unexpected error
            raise LumbniApiError(f"An unexpected error occurred: {err}")

    def generate_text(self, prompt: str, system_prompt: str = "", vendor: str = "", model_name: str = "",
                      temperature: float = 0.7, top_p: float = 0.95, top_k: int = 2, max_output_tokens: int = 100,
                      stream: bool = False) -> dict:
        """
        Generates text from the Lumbni API using the provided parameters.
        
        :param prompt: The main prompt text
        :param system_prompt: System-level instructions (optional)
        :param vendor: The vendor name (optional)
        :param model_name: The model to use (optional)
        :param temperature: Sampling temperature (default: 0.7)
        :param top_p: Nucleus sampling parameter (default: 0.95)
        :param top_k: Top-k sampling parameter (default: 2)
        :param max_output_tokens: Max tokens to generate (default: 100)
        :param stream: Whether to stream the response (default: False)
        :return: JSON response from the API
        """
        endpoint = "/api/v1/generate/text"
        
        # Filter out parameters that are empty or None
        data = {
            "vendor": vendor or None,
            "prompt": prompt,
            "system_prompt": system_prompt or None,
            "model_name": model_name or None,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens,
            "stream": stream
        }

        # Remove any keys where the value is None or an empty string
        data = {key: value for key, value in data.items() if value not in [None, ""]}

        return self._make_request("POST", endpoint, data)
