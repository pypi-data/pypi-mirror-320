# pratix-nelog

`pratix-nelog` is a Python library to analyze network logs in multiple formats (CSV, JSON, TXT) and consolidate them into a standardized JSON format.

## Features
- Parse logs in various formats.
- Extract key information like timestamps, IP addresses, and actions.
- Consolidate logs into JSON.

## Installation
```bash
pip install pratix-nelog


from pratix_nelog.parser import LogParser
from pratix_nelog.consolidator import LogConsolidator

# Example usage
logs = LogParser.parse_csv("sample_logs.csv")
consolidated_logs = LogConsolidator.consolidate(logs, "csv")
LogConsolidator.save_to_json(consolidated_logs, "output.json")

print("Logs processed and saved to output.json")