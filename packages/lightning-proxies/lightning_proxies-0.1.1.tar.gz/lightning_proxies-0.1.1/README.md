# LightningProxiesAPI

[![PyPI version](https://badge.fury.io/py/lightning-proxies.svg)](https://pypi.org/project/lightning-proxies/)

`LightningProxiesAPI` is a Python package for interacting with Lightning Proxies' API, providing access to residential, datacenter, IPv6, mobile, and ISP proxy services. This library simplifies the integration of proxy management, offering functionalities such as adding/removing proxies, retrieving plan details, managing whitelists, and more.

## Features

- **Manage proxies**: Access residential, datacenter, mobile, ISP, and IPv6 proxies.
- **Plan management**: View and manage proxy plans.
- **Whitelisting**: Easily manage IP whitelists for your proxies.
- **Bandwidth**: Monitor and adjust proxy bandwidth usage.
- **Flexible API**: Interact with a wide range of API endpoints for proxy management.

## Installation

You can install the `lightning-proxies` package directly from PyPI using `pip`:

```bash
pip install lightning-proxies
```

## Example usage
```python
from lightning_proxies import LightningProxies

# Initialize the client with your API key
client = LightningProxies(api_key="your_api_key")

# Get residential proxy information using plan ID
plan_id = "648248c31fac1bd9475b61ba"
response = client.get_residential_proxy_info(plan_id)

print(response)
```
## Example: Add an IP to the Whitelist
```python
from lightning_proxies import LightningProxies

# Initialize the client with your API key
client = LightningProxies(api_key="your_api_key")

# Add an IP address to the whitelist for IPv6 proxies
plan_id = "648248c31fac1bd9475b61ba"
ip_address = "1.1.1.1"
response = client.add_ip_to_whitelist(plan_id, ip_address)

print(response)
```
## Documentation
-- soon --

## Contributing 
We welcome contributions! Please fork the repository, create a branch, and submit a pull request. Ensure that all tests pass and that your code adheres to the project's coding standards.

### Steps for Contributing:
1. Fork the repository.
2. Create a new feature branch.
3. Make your changes and commit them.
4. Push your changes to your fork.
5. Open a pull request to the main branch.
