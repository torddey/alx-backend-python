#!/usr/bin/env python3
"""Test client module
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand([
        ("google", {"login": "google", "id": 1342004}),
        ("abc", {"login": "abc", "id": 123456})
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test GithubOrgClient.org method"""
        # Set up the mock
        mock_get_json.return_value = expected_payload

        # Create client instance
        client = GithubOrgClient(org_name)

        # Call the method
        result = client.org

        # Verify get_json was called once with correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        # Verify the result
        self.assertEqual(result, expected_payload)
