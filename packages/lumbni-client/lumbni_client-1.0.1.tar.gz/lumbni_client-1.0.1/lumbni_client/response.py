class LumbniApiResponse:
    """Handles the response from the Lumbni API, extracting useful data."""
    
    def __init__(self, response: dict):
        self.response = response
        self.data = response.get("data", {})
        self.message = response.get("message", "No message provided")
        self.status = response.get("status", "Unknown status")

    def is_successful(self):
        """Checks if the response indicates success."""
        return self.status.lower() == "success"

    def get_text(self):
        """Extracts the generated text from the response."""
        if self.is_successful():
            outputs = self.data.get("outputs", [])
            if outputs:
                return outputs[0].get("message", {}).get("content", "")
        return None

    def get_usage(self):
        """Returns token usage info from the response."""
        return self.data.get("usage", {})

    def __str__(self):
        """Returns a string representation of the response."""
        return f"Status: {self.status}, Message: {self.message}, Generated Text: {self.get_generated_text()}"

def handle_api_response(response: dict):
    """
    Handles the API response, checking if it's successful or if an error occurred.
    
    :param response: The raw response from the Lumbni API.
    :return: None
    """
    api_response = LumbniApiResponse(response)

    if api_response.is_successful():
        print("Text generated successfully!")
        print(f"Generated Text: {api_response.get_generated_text()}")
        print(f"Token Usage: {api_response.get_usage_info()}")
    else:
        print(f"Error: {api_response.message}")
        print(f"Details: {api_response.status}")

def detailed_response(response: dict):
    """Prints a detailed version of the response."""
    api_response = LumbniApiResponse(response)
    print(f"Raw Response Data: {api_response.response}")
    print(f"Status: {api_response.status}")
    print(f"Message: {api_response.message}")
    print(f"Generated Text: {api_response.get_generated_text()}")
    print(f"Token Usage Info: {api_response.get_usage_info()}")
