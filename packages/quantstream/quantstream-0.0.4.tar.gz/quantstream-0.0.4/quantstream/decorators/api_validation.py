import threading
import os
from functools import wraps
from quantstream.config import GLOBAL_API_KEYS


def prompt_for_api_key(service: str):
    """
    Prompts the user to enter an API key for the given service and updates GLOBAL_API_KEYS.

    Args:
        service (str): The name of the service.
    """
    api_key = input(f"Please enter your {service.upper()} API key: ")
    GLOBAL_API_KEYS[service] = api_key


def validate_api_key(service: str = "fmp"):
    """
    Decorator to ensure the API key for a service is set before making API calls.

    Args:
        service (str): The name of the service to validate. Defaults to "fmp".
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if API key is set in GLOBAL_API_KEYS or environment variable
            if service not in GLOBAL_API_KEYS or not GLOBAL_API_KEYS[service]:
                if f"{service.upper()}_API_KEY" in os.environ:
                    GLOBAL_API_KEYS[service] = os.environ[f"{service.upper()}_API_KEY"]
                else:
                    # Prompt user for API key
                    print(
                        f"The {service.upper()} API key must be provided. "
                        f"Get your key from the service's developer website."
                    )
                    timer = threading.Timer(10.0, prompt_for_api_key, args=(service,))
                    timer.start()
                    timer.join()

                    # Validate that the API key is now set
                    if not GLOBAL_API_KEYS.get(service):
                        raise ValueError(
                            f"{service.upper()} API key is required to proceed."
                        )
            return func(*args, **kwargs)

        return wrapper

    return decorator
