# BioNet Library

BioNet is a Python library designed to facilitate the integration of biological network data with external service providers via HTTP POST requests. This library provides a simple interface for sending data to specified API endpoints.

## Features

- Define and manage BioNet data objects.
- Specify service providers with API URLs.
- Send HTTP POST requests with BioNet data to external services.
- Handle HTTP responses and errors gracefully.

## Installation

To use the BioNet library, you need to have Python installed on your system. You can install the required dependencies using pip:

```bash
pip install requests
pip install python-dotenv
pip3 install setuptools
```

## Usage

Here's a quick example of how to use the BioNet library:

```python
from BioNet import BioNetData, ServiceProvider, post_bionet_data

# Create a BioNetData object
data = BioNetData(data={"key": "value"})

# Create a ServiceProvider object with the API URL
service_provider = ServiceProvider(apiURL="https://example.com/api")

# Make the POST request
response = post_bionet_data(data, service_provider)

# Check the response
if response:
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.json())
else:
    print("Failed to make the POST request.")
```

## Components

### BioNetData

The `BioNetData` class is used to encapsulate the data you want to send. It is initialized with a dictionary containing your data.

### ServiceProvider

The `ServiceProvider` class contains the API URL of the service provider to which you want to send the data. It is initialized with a string representing the URL.

### post_bionet_data

The `post_bionet_data` function takes a `BioNetData` object and a `ServiceProvider` object as parameters. It sends a POST request to the specified API URL with the data and returns the response.

## Testing

The library includes a test suite using the `unittest` framework. To run the tests, execute the following command:

```bash
python -m unittest test_bionet.py
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact Marc Salit at msalit@mitre.org.