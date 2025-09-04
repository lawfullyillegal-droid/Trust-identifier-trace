# Trust-identifier-trace

A trust identifier tracking and verification system that scans various sources for trust-related entities and generates reports.

## Components

- **gleif_echo.py**: Tests GLEIF API connectivity and echoes sample data
- **gleif_trace.py**: Scans GLEIF database for specific trust identifiers
- **gleif_alias_scan.py**: Scans GLEIF data for alias matches from identifiers.yaml
- **trust_scan_bot.py**: Main scanning bot that processes identifiers from JSON configuration
- **reddit_trace.py**: Queries Reddit for mentions of identifiers

## Configuration Files

- **identifiers.json**: JSON configuration of identifiers to scan
- **identifiers.yaml**: YAML configuration with trust aliases and ADOT numbers
- **trust_overlay.xml**: XML overlay for technical trace information

## Usage

Install dependencies:
```bash
pip install -r requirements.txt
```

Run individual components:
```bash
python gleif_echo.py          # Test GLEIF connectivity
python gleif_trace.py         # Scan specific identifiers
python trust_scan_bot.py      # Run full scan process
```
