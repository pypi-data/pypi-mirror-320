# test_bionet.py

import os
import unittest
import logging
from unittest.mock import patch, Mock

import requests
from BioNet import BioNetData, ServiceProvider, post_bionet_data
from BioNet.logging_config import setup_logging

# Setup logging
setup_logging()

class TestBioNet(unittest.TestCase):
    def setUp(self):
        self.test_sps_api = "https://localhost:8081/api"
        self.service_provider_catalog_url = os.getenv('BioNetServiceProviderCatalogURL', "http://localhost:81")

    def test_post_bionet_data_success(self):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        with patch('BioNet.bionet.requests.post') as mock_post:
            mock_post.return_value = mock_response

            data = BioNetData(data={"key": "value"})
            service_provider = ServiceProvider(self.test_sps_api)

            # Act
            response = post_bionet_data(data, service_provider)

            # Assert
            mock_post.assert_called_once_with(self.test_sps_api, json={'data': {"key": "value"}})
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"success": True})

    def test_post_bionet_data_failure(self):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError

        with patch('BioNet.bionet.requests.post') as mock_post:
            mock_post.return_value = mock_response

            data = BioNetData(data={"key": "value"})
            service_provider = ServiceProvider(self.test_sps_api)

            # Act
            response = post_bionet_data(data, service_provider)

            # Assert
            mock_post.assert_called_once_with(self.test_sps_api, json={'data': {"key": "value"}})
            self.assertIsNone(response)

if __name__ == '__main__':
    unittest.main()