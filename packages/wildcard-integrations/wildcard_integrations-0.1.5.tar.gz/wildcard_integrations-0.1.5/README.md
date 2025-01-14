# Wildcard Integrations

API client integrations for the Wildcard ecosystem.

## Installation

Install all clients:
```bash
pip install wildcard-integrations
```

Or install specific clients:
```bash
# Just Gmail
pip install "wildcard-integrations[gmail]"

# Just Airtable
pip install "wildcard-integrations[airtable]"

# Multiple specific clients
pip install "wildcard-integrations[gmail,airtable]"
```

## Usage

### Gmail API
```python
from wildcard_gmail import UsersApi
```

### Airtable API
```python
from wildcard_airtable import BasesApi, TablesApi, RecordsApi
``` 