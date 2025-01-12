import requests
from typing import Any, Dict, Optional, List
import logging

from .exceptions import APIError, AuthenticationError, InvalidParameterError
from .validators import Validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestHandler:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        return self._handle_response(response)

    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, headers=self.headers, data=data, json=json_data)
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            response.raise_for_status()
            logger.info(f"Request successful: {response.url}")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                logger.error(f"Authentication error: {http_err} - Response: {response.text}")
                raise AuthenticationError(f"Authentication failed: {http_err} - Response: {response.text}")
            else:
                logger.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
                raise APIError(f"HTTP error occurred: {http_err} - Response: {response.text}")
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            raise APIError(f"Other error occurred: {err}")


class LightningProxiesAPI:
    def __init__(self, api_key: str, base_url: str = "https://resell.lightningproxies.net/api"):
        self.request_handler = RequestHandler(api_key, base_url)

    def purchase_plan(self, option: str, **kwargs) -> Dict:
        """
        Purchase a plan.

        :param option: Type of the plan (residential, mobile, IPv6, datacenter, ISP).
        :param kwargs: Parameters depending on the type of the plan.
        :return: API response.
        """
        valid_options = ['residential', 'mobile', 'IPv6', 'datacenter', 'ISP']
        if option not in valid_options:
            raise ValueError(f"Invalid option '{option}'. Valid options are: {valid_options}")

        endpoint = f"getplan/{option}"

        # Prepare the request body depending on the option
        payload = {}
        if option == 'residential':
            bandwidth = kwargs.get('bandwidth')
            if bandwidth is None:
                raise ValueError("Parameter 'bandwidth' is required for residential plan.")
            payload['bandwidth'] = str(bandwidth)

        elif option == 'mobile':
            bandwidth = kwargs.get('bandwidth')
            if bandwidth is None:
                raise ValueError("Parameter 'bandwidth' is required for mobile plan.")
            payload['bandwidth'] = str(bandwidth)

        elif option == 'IPv6':
            plan = kwargs.get('plan')
            speed = kwargs.get('speed')
            bandwidth = kwargs.get('bandwidth')

            if plan is not None and speed is not None:
                # IPv6 - Unlimited Plan
                payload['plan'] = plan
                payload['speed'] = speed
            elif bandwidth is not None:
                # IPv6 - Bandwidth Plan
                payload['bandwidth'] = bandwidth
            else:
                raise ValueError("For IPv6 plan, provide either 'plan' and 'speed' or 'bandwidth'.")

        elif option == 'datacenter':
            plan = kwargs.get('plan')
            if plan is None:
                raise ValueError("Parameter 'plan' is required for datacenter plan.")
            if plan not in [1, 7, 30]:
                raise ValueError("Parameter 'plan' must be one of the following values: 1, 7, 30.")
            payload['plan'] = str(plan)

        elif option == 'ISP':
            ip = kwargs.get('ip')
            region = kwargs.get('region')
            if ip is None or region is None:
                raise ValueError("Parameters 'ip' and 'region' are required for ISP plan.")
            valid_regions = [
                "virm", "dtag", "vocu", "dtag_nl", "pol", "bra", "lva",
                "fra", "rou", "can", "nor", "aut", "ukr", "tur", "jpn", "isr",
                "twn", "kor", "esp", "sgp", "hkn", "tha", "ind", "ita"
            ]
            if region not in valid_regions:
                raise ValueError(f"Invalid region '{region}'. Valid regions are: {valid_regions}")
            payload['ip'] = ip
            payload['region'] = region

        return self.request_handler.post(endpoint, json_data=payload)

    def get_residential_proxy_info(self, plan_id: str) -> Dict:
        """
        Get Residential proxy information by planId.

        :param plan_id: The plan identifier (planId) of the product you purchased.
        :return: API response with proxy information.
        """
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")

        endpoint = f"plan/residential/read/{plan_id}"
        return self.request_handler.get(endpoint)

    def get_ipv6_proxy_info(self, plan_id: str) -> Dict:
        """
        Get IPv6 proxy information by planId.

        :param plan_id: The plan identifier (planId) of the product you purchased.
        :return: API response with IPv6 proxy information.
        """
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")

        endpoint = f"plan/ipv6/read/{plan_id}"
        return self.request_handler.get(endpoint)

    def get_datacenter_proxy_info(self, plan_id: str) -> Dict:
        """
        Get Datacenter proxy information by planId.

        :param plan_id: The plan identifier (planId) of the product you purchased.
        :return: API response with Datacenter proxy information.
        """
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")

        endpoint = f"plan/datacenter/read/{plan_id}"
        return self.request_handler.get(endpoint)

    def get_mobile_proxy_info(self, plan_id: str) -> Dict:
        """
        Get Mobile proxy information by planId.

        :param plan_id: The plan identifier (planId) of the product you purchased.
        :return: API response with Mobile proxy information.
        """
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")

        endpoint = f"plan/mobile/read/{plan_id}"
        return self.request_handler.get(endpoint)

    def get_isp_proxy_info(self, plan_id: str) -> Dict:
        """
        Get ISP proxy information by planId.

        :param plan_id: The plan identifier (planId) of the product you purchased.
        :return: API response with ISP proxy information.
        """
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")

        endpoint = f"plan/isp/read/{plan_id}"
        return self.request_handler.get(endpoint)

    def get_residential_mass_check(self, page: int, limit: int) -> List[Dict]:
        """
        Mass check Residential proxies using pagination.

        :param page: Page number.
        :param limit: Number of records per page.
        :return: List of dictionaries with Residential proxy information.
        """
        if not isinstance(page, int) or page < 1:
            raise ValueError("Parameter 'page' must be a positive integer.")
        if not isinstance(limit, int) or limit < 1:
            raise ValueError("Parameter 'limit' must be a positive integer.")

        # Form the final URL with pagination parameters
        endpoint = f"plan/{page}-{limit}"
        return self.request_handler.post(endpoint)

    def manage_ipv6_whitelist(self, action: str, plan_id: str, ip_address: str) -> Dict:
        """
        Add or remove an IP address from the IPv6 proxy whitelist.

        :param action: Action ('add' or 'remove').
        :param plan_id: The plan identifier (planId) of the product you purchased.
        :param ip_address: IP address to add or remove from the whitelist.
        :return: API response with the result message.
        """
        if action not in ['add', 'remove']:
            raise ValueError("Parameter 'action' must be either 'add' or 'remove'.")
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")
        if not ip_address:
            raise ValueError("Parameter 'ip_address' is required and cannot be empty.")
        Validator.validate_ip(ip_address)

        endpoint = f"plan/ipv6/{action}/whitelist/{plan_id}/{ip_address}"
        return self.request_handler.post(endpoint)

    def manage_datacenter_whitelist(self, action: str, plan_id: str, ip_address: str) -> Dict:
        """
        Add or remove an IP address from the Datacenter proxy whitelist.

        :param action: Action ('add' or 'remove').
        :param plan_id: The plan identifier (planId) of the product you purchased.
        :param ip_address: IP address to add or remove from the whitelist.
        :return: API response with the result message.
        """
        if action not in ['add', 'remove']:
            raise ValueError("Parameter 'action' must be either 'add' or 'remove'.")
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")
        if not ip_address:
            raise ValueError("Parameter 'ip_address' is required and cannot be empty.")
        Validator.validate_ip(ip_address)

        endpoint = f"plan/datacenter/{action}/whitelist/{plan_id}/{ip_address}"
        return self.request_handler.post(endpoint)

    def manage_ipv6_gigabyte(self, action: str, plan_id: str, gb: int) -> Dict:
        """
        Add or remove gigabytes (GB) from the IPv6 plan.

        :param action: Action ('add' or 'remove').
        :param plan_id: The plan identifier (planId) of the product you purchased.
        :param gb: Number of gigabytes to add or remove.
        :return: API response with the result message.
        """
        if action not in ['add', 'remove']:
            raise ValueError("Parameter 'action' must be either 'add' or 'remove'.")
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")
        if not isinstance(gb, int) or gb <= 0:
            raise ValueError("Parameter 'gb' must be a positive integer.")

        endpoint = f"{action}/{plan_id}/{gb}"
        return self.request_handler.post(endpoint)

    def manage_residential_gigabyte(self, action: str, plan_id: str, gb: float) -> Dict:
        """
        Add or remove gigabytes (GB) from the Residential plan.

        :param action: Action ('add' or 'remove').
        :param plan_id: The plan identifier (planId) of the product you purchased.
        :param gb: Number of gigabytes to add or remove.
                   - For adding: whole numbers (1, 2, 3, etc.).
                   - For removing: whole or decimal numbers (1, 2.15, 0.15, etc.).
        :return: API response with the result message.
        """
        if action not in ['add', 'remove']:
            raise ValueError("Parameter 'action' must be either 'add' or 'remove'.")
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")
        if not isinstance(gb, (int, float)) or gb <= 0:
            raise ValueError("Parameter 'gb' must be a positive number.")
        if action == 'add' and not isinstance(gb, int):
            raise ValueError("For 'add' action, 'gb' must be a whole number (integer).")

        endpoint = f"{action}/{plan_id}/{gb}"
        return self.request_handler.post(endpoint)

    def manage_mobile_gigabyte(self, action: str, plan_id: str, gb: float) -> Dict:
        """
        Add or remove gigabytes (GB) from the Mobile plan.

        :param action: Action ('add' or 'remove').
        :param plan_id: The plan identifier (planId) of the product you purchased.
        :param gb: Number of gigabytes to add or remove.
                   - For adding: whole numbers (1, 2, 3, etc.).
                   - For removing: whole or decimal numbers (1, 2.15, 0.15, etc.).
        :return: API response with the result message.
        """
        if action not in ['add', 'remove']:
            raise ValueError("Parameter 'action' must be either 'add' or 'remove'.")
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")
        if not isinstance(gb, (int, float)) or gb <= 0:
            raise ValueError("Parameter 'gb' must be a positive number.")
        if action == 'add' and not isinstance(gb, int):
            raise ValueError("For 'add' action, 'gb' must be a whole number (integer).")

        endpoint = f"{action}/{plan_id}/{gb}"
        return self.request_handler.post(endpoint)

    def get_residential_countries(self) -> List[Dict[str, str]]:
        """
        Get the list of available countries for Residential proxies.

        :return: List of dictionaries with 'country_name' and 'country_code'.
        """
        endpoint = "getlist/country_list"
        response = self.request_handler.post(endpoint)
        country_list = response.get("country_list")
        if country_list is None:
            raise APIError("Response JSON does not contain 'country_list'.")
        return country_list

    def get_residential_states(self, country_code: str) -> List[Dict[str, str]]:
        """
        Get the list of available states for Residential proxies based on country_code.

        :param country_code: Country code (e.g., 'us').
        :return: List of dictionaries with 'code'.
        """
        if not country_code:
            raise ValueError("Parameter 'country_code' is required and cannot be empty.")
        if not isinstance(country_code, str):
            raise ValueError("Parameter 'country_code' must be a string.")

        endpoint = "getlist/state_list"
        payload = {
            'country_code': country_code.lower()
        }
        response = self.request_handler.post(endpoint, json_data=payload)
        state_list = response.get("state_list")
        if state_list is None:
            raise APIError("Response JSON does not contain 'state_list'.")
        return state_list

    def get_residential_cities(self, country_code: str, state: str) -> List[Dict[str, str]]:
        """
        Get the list of available cities for Residential proxies based on country_code and state.

        :param country_code: Country code (e.g., 'us').
        :param state: State name (e.g., 'arizona').
        :return: List of dictionaries with 'code'.
        """
        if not country_code:
            raise ValueError("Parameter 'country_code' is required and cannot be empty.")
        if not state:
            raise ValueError("Parameter 'state' is required and cannot be empty.")
        if not isinstance(country_code, str):
            raise ValueError("Parameter 'country_code' must be a string.")
        if not isinstance(state, str):
            raise ValueError("Parameter 'state' must be a string.")

        endpoint = "getlist/city_list"
        payload = {
            'country_code': country_code.lower(),
            'state': state.lower()
        }
        response = self.request_handler.post(endpoint, json_data=payload)
        city_list = response.get("city_list")
        if city_list is None:
            raise APIError("Response JSON does not contain 'city_list'.")
        return city_list

    def get_residential_isp_list(self, country_code: str) -> List[Dict[str, str]]:
        """
        Get the list of available Internet Service Providers (ISP) for Residential proxies based on country_code.

        :param country_code: Country code (e.g., 'us').
        :return: List of dictionaries with 'name', 'asn', and 'country'.
        """
        if not country_code:
            raise ValueError("Parameter 'country_code' is required and cannot be empty.")
        if not isinstance(country_code, str):
            raise ValueError("Parameter 'country_code' must be a string.")

        endpoint = "getlist/isp_list"
        payload = {
            'country_code': country_code.lower()
        }
        response = self.request_handler.post(endpoint, json_data=payload)
        isp_list = response.get("isp_list")
        if isp_list is None:
            raise APIError("Response JSON does not contain 'isp_list'.")
        return isp_list

    def get_mobile_countries(self) -> List[Dict[str, Any]]:
        """
        Get the list of available countries for Mobile proxies.

        :return: List of dictionaries with country information (id, name, iso2, region_id, geo_asns, asnData).
        """
        endpoint = "getlist/mobile/country"
        response = self.request_handler.post(endpoint)
        if not isinstance(response, list):
            raise APIError("Response JSON is not a list as expected.")
        return response

    def get_product_info(self, plan_id: str) -> Dict:
        """
        Get general information about a product by planId.

        :param plan_id: The plan identifier (planId) of the product you purchased.
        :return: API response with general product information.
        """
        if not plan_id:
            raise ValueError("Parameter 'plan_id' is required and cannot be empty.")
        if not isinstance(plan_id, str):
            raise ValueError("Parameter 'plan_id' must be a string.")

        endpoint = f"info/{plan_id}"
        response = self.request_handler.get(endpoint)
        return response

    def change_credentials(self, subscription_id: str, plan_type: str, username: str, password: str,
                           proxy_type: Optional[str] = None) -> Dict:
        """
        Change credentials (username and password) for a plan.

        :param subscription_id: Subscription identifier (subscriptionId) of the plan.
        :param plan_type: Plan type ('residential' or 'isp').
        :param username: New username. Alphanumeric characters (a-z, A-Z, 0-9). Residential requires a minimum of 8 characters.
        :param password: New password. Alphanumeric characters (a-z, A-Z, 0-9). Residential requires a minimum of 8 characters.
        :param proxy_type: Proxy type ('http' or 'socks'). Used only for ISP. Omit for residential plans.
        :return: API response with the result message.
        """
        # Validate parameters
        if not subscription_id or not isinstance(subscription_id, str):
            raise ValueError("Subscription ID must be a non-empty string.")

        Validator.validate_plan_type(plan_type)
        Validator.validate_username(username, plan_type)
        Validator.validate_password(password, plan_type)

        if plan_type == 'isp':
            if proxy_type not in ['http', 'socks']:
                raise ValueError("Proxy type must be either 'http' or 'socks' for ISP plans.")
        else:
            if proxy_type is not None:
                raise ValueError("Proxy type should be omitted for residential plans.")

        endpoint = f"credentials-change/{subscription_id}"
        payload = {
            'planType': plan_type,
            'username': username,
            'password': password
        }
        if plan_type == 'isp':
            payload['proxyType'] = proxy_type

        return self.request_handler.post(endpoint, json_data=payload)