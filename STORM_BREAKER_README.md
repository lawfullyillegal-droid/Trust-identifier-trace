# Storm-Breaker Tool

Storm-Breaker is an advanced trust identifier trace tool that provides comprehensive scanning and analysis of trust identifiers across multiple data sources.

## Features

- **Comprehensive Identifier Analysis**: Analyzes patterns, formats, and characteristics of trust identifiers
- **Multi-Source Scanning**: Integrates with existing trust scanning infrastructure
- **Offline Validation**: Performs format validation and risk assessment without requiring external APIs
- **Pattern Recognition**: Identifies and categorizes different types of identifiers (EIN, SSN, IRS tracking, etc.)
- **Overlay Generation**: Creates YAML overlay files for each scanned identifier
- **Detailed Reporting**: Generates comprehensive scan reports with analysis and statistics
- **Flexible Output**: Customizable output formats and file naming

## Installation

1. Ensure Python 3.7+ is installed
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run a comprehensive scan with verbose output:
```bash
python3 storm_breaker.py -v
```

### Custom Output

Specify a custom output filename:
```bash
python3 storm_breaker.py -v -o my_scan_results.json
```

### Using the Runner Script

For a guided experience, use the interactive runner:
```bash
./run_storm_breaker.sh
```

### Command Line Options

- `-v, --verbose`: Enable verbose output showing detailed scan progress
- `-o OUTPUT, --output OUTPUT`: Specify custom output filename for results
- `--report-only`: Generate report without scanning (future feature)
- `-h, --help`: Show help message and exit

## Output Files

Storm-Breaker generates several types of output:

### Scan Results (`output/storm_breaker_results_*.json`)
Contains comprehensive scan data including:
- Identifier analysis (pattern type, format validation)
- Risk assessment
- Timestamps and metadata
- Overlay file references

### Log Files (`output/storm_breaker_*.log`)
Detailed execution logs showing:
- Scan progress
- Error messages
- Processing timestamps

### Overlay Files (`overlays/*_overlay.yml`)
YAML files for each identifier containing:
- Identifier metadata
- Analysis results
- Validation data
- Hash fingerprints

## Identifier Types Supported

Storm-Breaker recognizes and analyzes the following identifier patterns:

- **EIN**: Employer Identification Numbers (`EIN-*`)
- **SSN**: Social Security Numbers (`SSN-*`)
- **IRS Tracking**: IRS tracking numbers (`IRS-TRACK-*`)
- **CSE Case**: Child Support Enforcement cases (`CSE-CASE-*`)
- **ADOT Customer**: Arizona DOT customer IDs (`ADOT-CUST-*`)
- **Addresses**: Physical addresses (`ADDR-*`)
- **Entity Names**: Business/trust entity names (`ENTITY-*`)
- **Birth Registry**: Birth registry numbers (`*BIRTH*`)
- **Property Records**: Property and deed records (`*DEED*`, `*PROP*`)

## Example Output

```json
{
  "scan_info": {
    "timestamp": "2025-09-04_12-47-04",
    "tool": "Storm-Breaker v1.0",
    "total_identifiers": 9,
    "scan_duration": "N/A"
  },
  "results": [
    {
      "identifier": "EIN-92-6319308",
      "source": "EIN",
      "hash": "fe628416a7bd99ee",
      "scan_timestamp": "2025-09-04 12:47:04 UTC",
      "analysis": {
        "length": 14,
        "contains_numbers": true,
        "contains_letters": true,
        "contains_special": true,
        "pattern_type": "employer_identification"
      },
      "validation": {
        "format_valid": true,
        "checksum_valid": null,
        "risk_level": "low",
        "confidence": 0.8
      },
      "status": "scanned",
      "overlay_path": "/path/to/overlays/ein_overlay.yml"
    }
  ]
}
```

## Integration

Storm-Breaker is designed to work alongside existing trust scanning tools:

- Reads identifiers from `identifiers.json`
- Compatible with existing overlay structure
- Extends functionality of `trust_scan_bot.py` and related tools
- Provides enhanced analysis beyond basic Reddit/GLEIF scanning

## Architecture

Storm-Breaker follows a modular design:

1. **Identifier Loading**: Reads from JSON configuration
2. **Pattern Analysis**: Analyzes identifier characteristics
3. **Validation Engine**: Performs format and risk validation
4. **Overlay Generator**: Creates structured metadata files
5. **Report Engine**: Generates comprehensive analysis reports

## Error Handling

Storm-Breaker includes robust error handling:

- Graceful handling of missing input files
- Network-independent operation (offline capable)
- Detailed error logging
- Continued operation on individual identifier failures

## Future Enhancements

Planned features for future versions:

- External API integration (when network access is available)
- Advanced risk scoring algorithms
- Configurable validation rules
- Export to multiple formats (CSV, XML)
- Real-time monitoring capabilities
- Integration with additional data sources

## Security Considerations

- Identifiers are hashed for fingerprinting
- Sensitive data handling follows best practices
- Offline operation reduces data exposure
- Structured logging for audit trails

## Contributing

This tool is part of the Trust-identifier-trace project. Contributions should maintain compatibility with existing infrastructure while enhancing analysis capabilities.