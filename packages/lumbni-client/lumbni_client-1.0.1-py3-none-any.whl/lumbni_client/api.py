from .client import LumbniClient

def generate_text(client: LumbniClient, prompt: str, system_prompt: str = "", vendor: str = "", model_name: str = "",
                  temperature: float = 0.7, top_p: float = 0.95, top_k: int = 2, max_output_tokens: int = 100,
                  stream: bool = False, mode: str = "dev") -> dict:
    """
    Generates text based on the provided prompt and system parameters using the Lumbni API client.
    
    :param client: LumbniClient instance.
    :param prompt: The prompt for text generation.
    :param system_prompt: Optional system-level prompt to guide the model (default: "").
    :param vendor: Optional vendor-specific data (default: "").
    :param model_name: Optional model name for generation (default: "").
    :param temperature: Temperature parameter for generation (default: 0.7).
    :param top_p: Top-p sampling (default: 0.95).
    :param top_k: Top-k sampling (default: 2).
    :param max_output_tokens: Maximum number of tokens for the output (default: 100).
    :param stream: If true, enables streaming (default: False).
    :param mode: Set the mode of operation, either "dev" or "prod" (default: "dev").
    
    :return: The generated text response from the API.
    """
    # Pass mode to the client initialization
    if not isinstance(client, LumbniClient):
        client = LumbniClient(api_key=client.api_key, mode=mode)  # Ensure client is properly set for the mode

    # Call the client's generate_text method with the provided parameters
    return client.generate_text(
        prompt=prompt,
        system_prompt=system_prompt,
        vendor=vendor,
        model_name=model_name,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        max_output_tokens=max_output_tokens,
        stream=stream
    )
