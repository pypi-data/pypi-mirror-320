import os
import time
from typing import List
from dotenv import load_dotenv
from .config import get_config  # Now importing from our Python config file

# Load environment variables
load_dotenv()

def wait(ms: int = 0) -> None:
    """Sleep for the specified number of milliseconds."""
    return time.sleep(ms / 1000)  # Convert milliseconds to seconds

def arb_log(text: str) -> None:
    """Display an animated loading sequence with the given text."""
    for i in range(25):
        wait(40)
        if i == 12:
            str_output = f"{' ' * (i * 2)}"
        else:
            str_output = f"{' ' * (i * 2)}{' ' * (i * 2)}"
        
        # Center the string to 60 characters
        while len(str_output) < 60:
            str_output = f" {str_output} "
        
        print(str_output)
    
    print(f"Arbitrum Demo: {text}")
    wait(2000)
    
    print("Lets")
    wait(1000)
    
    print("Go ")
    wait(1000)
    print("... ")
    wait(1000)
    print("")

def require_env_variables(env_vars: List[str]) -> None:
    """Verify that required environment variables are set."""
    for env_var in env_vars:
        if not os.getenv(env_var):
            raise ValueError(f"Error: set your '{env_var}' environmental variable")
    
    print("Environmental variables properly set ")

# Example usage
if __name__ == "__main__":
    config = get_config()  # Get the configuration if needed
    require_env_variables(["L1RPC", "L2RPC", "DEVNET_PRIVKEY"])  # Check for required environment variables
    arb_log("Testing")  # Display the animation with message