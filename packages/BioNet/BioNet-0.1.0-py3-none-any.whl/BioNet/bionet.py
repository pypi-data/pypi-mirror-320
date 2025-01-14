# BioNet/bionet.py

import os
import requests
import logging
from .logging_config import setup_logging
from .models import BioNetData, ServiceProvider
from dotenv import load_dotenv

# Setup logging
setup_logging()

# Load environment variables from .env file
load_dotenv()  # By default, this does not override existing environment variables

def get_environment_variables():
    """
    Retrieves environment variables for BioNet Service Provider Catalog URL and Operations Library URL.
    Sets using defaults if not found in environment.
    """
    service_provider_catalog_url = os.getenv('BioNetServiceProviderCatalogURL')
    operations_library_url = os.getenv('BioNetOperationsLibraryURL')

    if service_provider_catalog_url:
        logging.info(f"BioNet Service Provider Catalog URL: {service_provider_catalog_url}")
    else:
        logging.warning("BioNetServiceProviderCatalogURL environment variable is not set. Setting to default value.")
        service_provider_catalog_url = "http://localhost:81"

    if operations_library_url:
        logging.info(f"BioNet Operations Library URL: {operations_library_url}")
    else:
        logging.warning("BioNetOperationsLibraryURL environment variable is not set. Setting to default value.")
        operations_library_url = "http://localhost:82"

    return service_provider_catalog_url, operations_library_url

service_provider_catalog_url, operations_library_url = get_environment_variables()

def post_bionet_data(bionet_data: BioNetData, service_provider: ServiceProvider):
    """
    Sends a POST request with the BioNet data to the specified service provider's API URL.

    :param bionet_data: BioNetData object containing the data to be sent.
    :param service_provider: ServiceProvider object containing the API URL.
    :return: Response object from the POST request.
    """
    try:
        # Prepare the data payload for the POST request
        payload = {'data': bionet_data.data}

        logging.info(f"Sending POST request to {service_provider.apiURL} with payload: {payload}")

        # Make the POST request
        response = requests.post(service_provider.apiURL, json=payload)
        
        # Check if the request was successful
        response.raise_for_status()
        logging.info(f"Received successful response: {response.status_code}")

        return response

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
        return None

def get_service_provider_catalog_data():
    """
    Makes a GET request to the service_provider_catalog URL specified by the BioNetServiceProviderCatalogURL environment variable.

    :return: Response object from the GET request, or None if the request fails or the URL is not set.
    """
    if not service_provider_catalog_url:
        logging.warning("BioNetServiceProviderCatalogURL environment variable is not set.")
        return None

    try:
        logging.info(f"Making GET request to service_provider_catalog URL: {service_provider_catalog_url}")

        # Make the GET request
        response = requests.get(service_provider_catalog_url)

        # Check if the request was successful
        response.raise_for_status()
        logging.info(f"Received successful response from service_provider_catalog: {response.status_code}")

        return response

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching service_provider_catalog data: {e}")
        return None
    

