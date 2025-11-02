# Identifier Connections Bot

## Overview
The Identifier Connections Bot is a comprehensive connection discovery tool that searches for all relationships between trust identifiers across multiple sources and platforms. It creates a complete relationship map showing how different identifiers are connected.

## Features

### Multi-Source Connection Discovery
- **Reddit Integration**: Scans Reddit posts and comments for mentions linking multiple identifiers
- **GLEIF Integration**: Searches the Global Legal Entity Identifier Foundation database for entity connections
- **Cross-Identifier Analysis**: Analyzes patterns and relationships between different identifier types
- **Alias Matching**: Identifies connections through trust aliases and ADOT numbers

### Connection Types Detected

1. **Reddit Connections**: Posts mentioning multiple identifiers together
2. **GLEIF Connections**: Legal entity records matching identifiers or aliases
3. **Cross-Identifier Relationships**: Pattern-based connections such as:
   - Entity-Tax ID relationships (EIN ↔ EntityName)
   - Person-Birth Record relationships (SSN ↔ BirthRegNum)
   - Location-Property relationships (Address ↔ PropertyRecord)
   - Customer-Location relationships (ADOTCust ↔ Address)
   - Case-Person relationships (CSECase ↔ SSN)
   - Tax Tracking-Entity relationships (IRSTrack ↔ EIN)
4. **Alias Connections**: Links between identifiers and known trust aliases
5. **ADOT Reference Connections**: Matches with Arizona Department of Transportation numbers

### Connection Graph
The bot builds a complete graph representation of all connections, showing:
- Which identifiers are connected to each other
- How identifiers relate to aliases
- Connection strength and type
- Most highly connected identifiers

### Metrics and Analytics
- Total connections found
- Connection sources breakdown
- Relationship type distribution
- Most connected identifiers ranking

## Usage

### Basic Usage
```bash
python3 identifier_connections_bot.py
```

### Output
The bot generates a comprehensive JSON file at `output/identifier_connections.json` containing:
- Scan metadata (timestamp, version, counts)
- All identifiers scanned
- Trust aliases and ADOT numbers
- Complete list of connections with details
- Connection graph representation
- Summary metrics and analytics

### Example Output Structure
```json
{
  "scan_metadata": {
    "bot_name": "Identifier Connections Bot",
    "version": "1.0",
    "scan_timestamp": "2025-10-21T22:19:38.773176+00:00",
    "total_identifiers_scanned": 9,
    "total_connections_found": 31
  },
  "connections": [
    {
      "source": "Cross-Identifier_Analysis",
      "identifier_1": "EIN-92-6319308",
      "identifier_2": "ENTITY-THE-TRAVIS-RYLE-PRIVATE-BANK",
      "relationship_type": "Entity-Tax_ID_Relationship",
      "confidence": "high",
      "timestamp": "2025-10-21T22:19:38.749644+00:00"
    }
  ],
  "connection_graph": {
    "EIN-92-6319308": ["ENTITY-THE-TRAVIS-RYLE-PRIVATE-BANK"],
    "ENTITY-THE-TRAVIS-RYLE-PRIVATE-BANK": ["EIN-92-6319308", "THE TRAVIS RYLE PRIVATE BANK"]
  },
  "metrics": {
    "total_connections": 31,
    "connection_sources": {
      "Reddit": 9,
      "GLEIF": 9,
      "Cross-Identifier_Analysis": 6,
      "ADOT_Reference": 2,
      "Alias_Match": 5
    }
  }
}
```

## Automated Execution

The bot can be run automatically via GitHub Actions:

### Workflow Schedule
- Manual trigger via `workflow_dispatch`
- Automatic execution every 6 hours

### Workflow Location
`.github/workflows/identifier_connections_bot.yml`

## Dashboard Visualization

The bot's results can be visualized using the Connections Dashboard:

### Accessing the Dashboard
1. Ensure the bot has run at least once
2. Start a local web server: `python3 -m http.server 8000`
3. Navigate to: `http://localhost:8000/connections_dashboard.html`

### Dashboard Features
- **Network Graph**: Interactive visualization of identifier connections
- **Statistics**: Summary metrics showing total identifiers, connections, and sources
- **Connection Details Table**: Searchable table of all connections
- **Source Breakdown**: Distribution of connections by source type

## Offline Mode

The bot is designed to work gracefully in offline or network-restricted environments:
- Falls back to mock data when Reddit is unreachable
- Creates sample GLEIF connections when API is unavailable
- Still performs local analysis (cross-identifier and alias matching)
- Marks offline connections with `"offline_mode": true` flag

## Dependencies

Required Python packages:
- `requests` - HTTP requests for API calls
- `pyyaml` - YAML file parsing for identifiers

Install via: `pip install -r requirements.txt`

## Integration with Existing Tools

The Identifier Connections Bot complements other repository tools:
- **trust_scan_bot.py**: Basic identifier scanning
- **reddit_trace.py**: Reddit-specific profiling
- **gleif_trace.py**: GLEIF entity scanning
- **storm_breaker.py**: Advanced pattern analysis

The Connections Bot provides a unified view across all these systems.

## Technical Details

### Class: `IdentifierConnectionsBot`

**Methods:**
- `load_identifiers()`: Loads identifiers from identifiers.json
- `load_aliases()`: Loads aliases and ADOT numbers from identifiers.yaml
- `find_reddit_connections(identifier)`: Searches Reddit for connection mentions
- `find_gleif_connections(identifier)`: Searches GLEIF database for entity connections
- `find_cross_identifier_connections()`: Analyzes pattern-based relationships
- `find_alias_connections()`: Matches identifiers with aliases
- `build_connection_graph()`: Creates graph representation of connections
- `calculate_connection_metrics()`: Generates analytics and statistics
- `run_comprehensive_scan()`: Executes full connection discovery
- `save_results(results, filename)`: Saves results to JSON file
- `print_summary(results)`: Prints formatted summary report

### Connection Confidence Levels
- **high**: Direct pattern match or explicit relationship
- **medium**: Partial match or reference-based connection
- **low**: Weak association or contextual mention

## Example Use Cases

1. **Comprehensive Audit**: Discover all connections between trust identifiers
2. **Relationship Mapping**: Understand how different identifiers relate to each other
3. **Network Analysis**: Identify central/hub identifiers with many connections
4. **Data Validation**: Verify expected relationships exist in the data
5. **Discovery**: Find unexpected connections that warrant investigation

## Output Files

- `output/identifier_connections.json` - Main results file
- `bots/identifier_connections_bot.py` - Bot source code
- `.github/workflows/identifier_connections_bot.yml` - Automation workflow

## Troubleshooting

### No connections found
- Ensure `identifiers.json` and `identifiers.yaml` exist
- Check network connectivity for Reddit/GLEIF APIs
- Verify identifier formats match expected patterns

### Network errors
- Normal in sandboxed/restricted environments
- Bot will fall back to offline mode automatically
- Mock data will be generated for testing

### Missing output file
- Check that `output/` directory exists
- Verify bot completed successfully (exit code 0)
- Review console output for error messages

## Contributing

To extend the bot:
1. Add new connection discovery methods in the class
2. Update `run_comprehensive_scan()` to call new methods
3. Add new connection types to the metrics calculation
4. Update dashboard to display new connection types

## Version History

- **v1.0** (2025-10-21): Initial release
  - Multi-source connection discovery
  - Connection graph generation
  - Comprehensive metrics and analytics
  - Dashboard visualization support
