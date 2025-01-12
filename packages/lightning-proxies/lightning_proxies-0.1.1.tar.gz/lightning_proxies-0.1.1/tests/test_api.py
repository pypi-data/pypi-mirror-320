import unittest
from unittest.mock import patch
from lightning_proxies import LightningProxiesAPI, APIError, AuthenticationError, InvalidParameterError

class TestLightningProxiesAPI(unittest.TestCase):
    def setUp(self):
        self.api = LightningProxiesAPI(api_key="test_api_key")

    @patch('lightning_proxies.api.requests.post')
    def test_change_credentials_residential_success(self, mock_post):
        mock_response = unittest.mock.Mock()
        mock_response.raise_for_status = unittest.mock.Mock()
        mock_response.json.return_value = {
            "message": "Credentials updated successfully."
        }
        mock_post.return_value = mock_response

        response = self.api.change_credentials(
            subscription_id="valid_subscription_id",
            plan_type="residential",
            username="NewUser123",
            password="NewPass123"
        )
        self.assertEqual(response["message"], "Credentials updated successfully.")

    @patch('lightning_proxies.api.requests.post')
    def test_change_credentials_isp_success(self, mock_post):
        mock_response = unittest.mock.Mock()
        mock_response.raise_for_status = unittest.mock.Mock()
        mock_response.json.return_value = {
            "message": "Credentials updated successfully."
        }
        mock_post.return_value = mock_response

        response = self.api.change_credentials(
            subscription_id="valid_subscription_id",
            plan_type="isp",
            username="ISPUser123",
            password="ISPPass123",
            proxy_type="http"
        )
        self.assertEqual(response["message"], "Credentials updated successfully.")

    @patch('lightning_proxies.api.requests.post')
    def test_change_credentials_invalid_plan_type(self, mock_post):
        with self.assertRaises(ValueError):
            self.api.change_credentials(
                subscription_id="valid_subscription_id",
                plan_type="invalid_type",
                username="User1234",
                password="Pass1234"
            )

    @patch('lightning_proxies.api.requests.post')
    def test_change_credentials_short_username_residential(self, mock_post):
        with self.assertRaises(InvalidParameterError):
            self.api.change_credentials(
                subscription_id="valid_subscription_id",
                plan_type="residential",
                username="User1",
                password="Pass1234"
            )

    @patch('lightning_proxies.api.requests.post')
    def test_change_credentials_invalid_proxy_type_isp(self, mock_post):
        with self.assertRaises(ValueError):
            self.api.change_credentials(
                subscription_id="valid_subscription_id",
                plan_type="isp",
                username="ISPUser123",
                password="ISPPass123",
                proxy_type="ftp"  # Invalid value
            )

    @patch('lightning_proxies.api.requests.post')
    def test_change_credentials_proxy_type_for_residential(self, mock_post):
        with self.assertRaises(ValueError):
            self.api.change_credentials(
                subscription_id="valid_subscription_id",
                plan_type="residential",
                username="NewUser123",
                password="NewPass123",
                proxy_type="http"  # Should be omitted
            )

if __name__ == '__main__':
    unittest.main()