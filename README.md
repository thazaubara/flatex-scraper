# Flatex scraper
Web scraper built on selenium to get my portfolio value from flatex broker.

## Credentials

This script reads credentials from import. Generate `credentials.py` in root directory of script.

`credentials.py`

```python
DB_HOST = ""
DB_PORT = port

DB_TABLE = ""
DB_NAME = ""
DB_USER = ""
DB_PASS = ""

FLATEX_USER = ""
FLATEX_PASS = ""
```

## Known Bugs

- Sometimes Flatex does not show all values. Static reference to those table cells fails and this leads to exceptions.

## Usage

Runs on a Ubuntu Server 24/7. 4 Hour crontab.

## Why tho?

Nice Grafana Dashboard. Because i can!
