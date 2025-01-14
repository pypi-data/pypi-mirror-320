import unittest
from unittest.mock import patch
from certbot_dns_spaceship.client import SpaceshipClient


class TestSpaceshipClient(unittest.TestCase):
    def setUp(self):
        self.credentials_path = "/path/to/mock_credentials.ini"
        self.client = SpaceshipClient(self.credentials_path)

    @patch("requests.post")
    def test_add_txt_record(self, mock_post):
        # Mock the API response
        mock_response = mock_post.return_value
        mock_response.status_code = 201

        domain = "example.com"
        name = "_acme-challenge.example.com"
        content = "test_validation_token"

        # Call the method
        self.client.add_txt_record(domain, name, content)

        # Assert the POST request was made correctly
        mock_post.assert_called_once_with(
            f"https://api.spaceship.com/v1/domains/{domain}/dns-records",
            headers={
                "X-Api-Key": self.client.api_key,
                "X-Api-Secret": self.client.api_secret,
            },
            json={"type": "TXT", "name": name, "content": content},
        )

    @patch("requests.delete")
    def test_remove_txt_record(self, mock_delete):
        # Mock the API response
        mock_response = mock_delete.return_value
        mock_response.status_code = 200

        domain = "example.com"
        name = "_acme-challenge.example.com"
        content = "test_validation_token"

        # Call the method
        self.client.remove_txt_record(domain, name, content)

        # Assert the DELETE request was made correctly
        mock_delete.assert_called_once_with(
            f"https://api.spaceship.com/v1/domains/{domain}/dns-records",
            headers={
                "X-Api-Key": self.client.api_key,
                "X-Api-Secret": self.client.api_secret,
            },
            json={"type": "TXT", "name": name, "content": content},
        )


if __name__ == "__main__":
    unittest.main()
