# CBE Verification SDK

A Python SDK for verifying Commercial Bank of Ethiopia (CBE) transactions.

## Installation

```bash
pip install cbe-verification-sdk
```

## Quick Start

```python
from cbe_verification_sdk import CBEVerificationClient

# Initialize client
client = CBEVerificationClient(
    api_key="your-api-key-here",
    api_base_url="http://your-api-url.com"
)

# Verify a transaction
result = client.verify_transaction(
    reference_number="FT253487211",
    account_number="1000012345678"
)

print(result)
```

## Features

- Easy verification of CBE transactions
- Automatic PDF text extraction
- Error handling and logging
- Rate limit handling

## Requirements

- Python 3.7+
- PyPDF2
- requests

## Documentation

For detailed documentation, visit [your-documentation-url].

## License

MIT License - see LICENSE file for details.