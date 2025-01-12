# Anypayx

A Python library and CLI for interacting with Anypayx.com WebSockets and REST APIs.

## Installation

To install the package, use pip:

```
pip install anypayx
```

## Usage

### CLI

The CLI provides commands to create invoices and subscribe to invoices or accounts.

#### Create Invoice

```
anypayx create-invoice --amount 100 --currency USD
```

#### Subscribe to Invoice

```
anypayx subscribe-invoice --invoice-id 12345
```

#### Subscribe to Account

```
anypayx subscribe-account --account-id 67890
```

### Library

You can also use the library in your Python code:

```python
from anypayx.api import AnypayxAPI

api = AnypayxAPI(api_key='your_api_key')
invoice = api.create_invoice(amount=100, currency='USD')
print(invoice)

ws_invoice = api.subscribe_invoice(invoice_id='12345')
print("Subscribed to invoice")

ws_account = api.subscribe_account(account_id='67890')
print("Subscribed to account")
```

## Development and Publication

### Prerequisites

Ensure you have the latest versions of `setuptools`, `wheel`, and `twine`:

```
pip install --upgrade setuptools wheel twine
```

### Building the Package

Navigate to the root directory of your project (where your `setup.py` is located) and run:

```
python setup.py sdist bdist_wheel
```

This will generate distribution archives in the `dist/` directory.

### Register on PyPI

If you haven't already, create an account on [PyPI](https://pypi.org/account/register/).

### Uploading to PyPI

Use `twine` to upload your package:

```
twine upload dist/*
```

You will be prompted to enter your PyPI username and password. If you have two-factor authentication enabled, you will also need to provide a code.

### Verify Your Package

After uploading, verify that your package is available on PyPI by visiting `https://pypi.org/project/anypayx/`.

### Testing Installation

To test the installation of your package, create a virtual environment and install it:

```
python -m venv test-env
source test-env/bin/activate  # On Windows use `test-env\Scripts\activate`
pip install anypayx
```

### Using TestPyPI

Before uploading to the main PyPI, you can test your package on [TestPyPI](https://test.pypi.org/):

Upload to TestPyPI:

```
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Install from TestPyPI:

```
pip install --index-url https://test.pypi.org/simple/ anypayx
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
