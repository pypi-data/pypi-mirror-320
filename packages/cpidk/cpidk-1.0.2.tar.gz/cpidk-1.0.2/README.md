# CPIDK - library for checking driver permissions in Poland.

## Installation
```bash
pip install cpidk
```

## Usage
```python
from cpidk import check_driver_permissions

data = check_driver_permissions(
    firstname="Jan",
    surname="Kowalski",
    serial_number="A1234567"
)

if data is None:
    print("Driver not found")
else:
    print(data)
```