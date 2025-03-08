import os
import random
from typing import Dict

def get_proxy_config() -> Dict[str, str]:
    """
    Get proxy configuration from environment variables.
    Returns a dictionary with proxy URL formatted for use with requests.
    
    Returns:
        Dict[str, str]: A dictionary containing proxy configuration in the format {'https': proxy_url}
    """
    # Get proxy configuration from environment variables
    proxy_domain = os.getenv('PROXY_DOMAIN')
    proxy_ports_str = os.getenv('PROXY_PORTS', '')
    proxy_username = os.getenv('PROXY_USERNAME')
    proxy_password = os.getenv('PROXY_PASSWORD')
    
    # If any required proxy information is missing, return empty dict
    if not all([proxy_domain, proxy_ports_str, proxy_username, proxy_password]):
        return {}
    
    # Parse proxy ports (comma-separated list of ports)
    try:
        proxy_ports = [int(port) for port in proxy_ports_str.split(',') if port.strip()]
        if not proxy_ports:
            return {}
    except ValueError:
        return {}
    
    # Select a random port from the available range
    selected_port = random.choice(proxy_ports)
    
    # Format the proxy URL
    proxy_url = f"https://{proxy_username}:{proxy_password}@{proxy_domain}:{selected_port}"
    
    return {"https": proxy_url} 