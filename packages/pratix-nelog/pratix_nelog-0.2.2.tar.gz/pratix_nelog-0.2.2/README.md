# pratix-nelog

`pratix-nelog` is a Python library to analyze network logs in multiple formats (CSV, JSON, TXT) and consolidate them into a standardized JSON format.

## Features
- Parse logs in various formats.
- Extract key information like timestamps, IP addresses, and actions.
- Consolidate logs into JSON.

## Installation
```bash
pip install pratix-nelog


# Create a log parser object
log_parser = LogParser(log_file="path/to/logfile.log")

# Parse the log file
parsed_data = log_parser.parse()

# Print parsed data
print(parsed_data)
