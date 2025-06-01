#!/usr/bin/env python3
"""Test client module
"""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, PropertyMock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


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

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url property"""
        # Test payload
        test_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }
        
        # Create client instance
        client = GithubOrgClient("google")
        
        # Patch the org property to return our test payload
        with patch.object(
            GithubOrgClient, 'org', new_callable=PropertyMock,
            return_value=test_payload
        ):
            # Get the public repos URL
            result = client._public_repos_url
            
            # Verify the result
            self.assertEqual(result, test_payload["repos_url"])

    @parameterized.expand([
        (
            {"license": {"key": "my_license"}},
            "my_license",
            True
        ),
        (
            {"license": {"key": "other_license"}},
            "my_license",
            False
        )
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license method"""
        # Call the static method
        result = GithubOrgClient.has_license(repo, license_key)
        
        # Verify the result
        self.assertEqual(result, expected)


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': TEST_PAYLOAD[0][2],
        'apache2_repos': TEST_PAYLOAD[0][3]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        # Create a patcher for requests.get
        cls.get_patcher = patch('requests.get')
        # Start the patcher
        cls.mock_get = cls.get_patcher.start()

        # Configure the mock to return different payloads based on URL
        def side_effect(url):
            if url == "https://api.github.com/orgs/google":
                return Mock(json=lambda: cls.org_payload)
            elif url == "https://api.github.com/orgs/google/repos":
                return Mock(json=lambda: cls.repos_payload)
            return None

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down test fixtures"""
        # Stop the patcher
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos method without license"""
        # Create client instance
        client = GithubOrgClient("google")
        
        # Get public repos
        repos = client.public_repos()
        
        # Verify the result matches expected_repos
        self.assertEqual(repos, self.expected_repos)
        
        # Verify requests.get was called with correct URLs
        self.mock_get.assert_any_call("https://api.github.com/orgs/google")
        self.mock_get.assert_any_call("https://api.github.com/orgs/google/repos")

    def test_public_repos_with_license(self):
        """Test public_repos method with license filter"""
        # Create client instance
        client = GithubOrgClient("google")
        
        # Get public repos with Apache 2.0 license
        repos = client.public_repos(license="apache-2.0")
        
        # Verify the result matches apache2_repos
        self.assertEqual(repos, self.apache2_repos)
        
        # Verify requests.get was called with correct URLs
        self.mock_get.assert_any_call("https://api.github.com/orgs/google")
        self.mock_get.assert_any_call("https://api.github.com/orgs/google/repos")
