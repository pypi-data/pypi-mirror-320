from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

config = {
    "solidity": {
        "compilers": [
            {
                "version": "0.8.2",
                "settings": {}
            },
            {
                "version": "0.7.2",
                "settings": {}
            },
            {
                "version": "0.6.12",
                "settings": {}
            },
            {
                "version": "0.6.11",
                "settings": {}
            }
        ]
    },
    "networks": {
        "l1": {
            "gas": 2100000,
            "gasLimit": 0,
            "url": os.getenv('L1RPC', ''),
            "accounts": [os.getenv('DEVNET_PRIVKEY')] if os.getenv('DEVNET_PRIVKEY') else []
        },
        "l2": {
            "url": os.getenv('L2RPC', ''),
            "accounts": [os.getenv('DEVNET_PRIVKEY')] if os.getenv('DEVNET_PRIVKEY') else []
        }
    }
}

# If you need to access this configuration from other files
def get_config():
    return config