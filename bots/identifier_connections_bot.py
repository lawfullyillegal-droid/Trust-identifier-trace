#!/usr/bin/env python3
"""
Identifier Connections Bot - Comprehensive connection discovery tool

This bot searches for all connections between trust identifiers across multiple
sources and platforms, creating a comprehensive relationship map.
"""
import os
import json
import yaml
import requests
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Set, Optional


class IdentifierConnectionsBot:
    """Advanced bot for discovering all connections between identifiers"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.identifiers: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []
        self.connection_graph: Dict[str, Set[str]] = {}
        self.aliases: List[str] = []
        self.adot_numbers: List[str] = []
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp"""
        if self.verbose:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(level, "📝")
            print(f"[{timestamp}] {emoji} {message}")
    
    def load_identifiers(self) -> bool:
        """Load identifiers from JSON file"""
        try:
            identifiers_file = Path(__file__).parent / "identifiers.json"
            with open(identifiers_file, 'r') as f:
                self.identifiers = json.load(f)
            self.log(f"Loaded {len(self.identifiers)} identifiers from identifiers.json", "SUCCESS")
            return True
        except FileNotFoundError:
            self.log("identifiers.json not found, using sample data", "WARNING")
            self.identifiers = [
                {"identifier": "EIN-92-6319308", "source": "EIN"},
                {"identifier": "SSN-602-05-7209", "source": "SSN"},
                {"identifier": "IRS-TRACK-108541264370", "source": "IRSTrack"}
            ]
            return False
        except Exception as e:
            self.log(f"Error loading identifiers: {e}", "ERROR")
            return False
    
    def load_aliases(self) -> bool:
        """Load trust aliases and ADOT numbers from YAML file"""
        try:
            yaml_file = Path(__file__).parent / "identifiers.yaml"
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                self.aliases = data.get('trust_aliases', [])
                self.adot_numbers = data.get('adot_numbers', [])
            self.log(f"Loaded {len(self.aliases)} aliases and {len(self.adot_numbers)} ADOT numbers", "SUCCESS")
            return True
        except FileNotFoundError:
            self.log("identifiers.yaml not found, using defaults", "WARNING")
            self.aliases = ["TRAVIS RYLE", "RYLE PRIVATE BANK", "TRAVIS RYLE TRUST"]
            self.adot_numbers = ["AZC-004921", "ADOT-782134"]
            return False
        except Exception as e:
            self.log(f"Error loading aliases: {e}", "ERROR")
            return False
    
    def find_reddit_connections(self, identifier: str) -> List[Dict[str, Any]]:
        """Search Reddit for mentions that might indicate connections"""
        connections = []
        try:
            headers = {"User-Agent": "IdentifierConnectionsBot/1.0"}
            url = f"https://www.reddit.com/search.json?q={identifier}&limit=20"
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                
                for post in posts:
                    post_data = post.get("data", {})
                    title = post_data.get("title", "")
                    selftext = post_data.get("selftext", "")
                    
                    # Check if any other identifiers are mentioned
                    mentioned_identifiers = []
                    for other_ident in self.identifiers:
                        other_id = other_ident["identifier"]
                        if other_id != identifier and (other_id in title or other_id in selftext):
                            mentioned_identifiers.append(other_id)
                    
                    # Check if any aliases are mentioned
                    mentioned_aliases = []
                    for alias in self.aliases:
                        if alias.lower() in title.lower() or alias.lower() in selftext.lower():
                            mentioned_aliases.append(alias)
                    
                    if mentioned_identifiers or mentioned_aliases:
                        connections.append({
                            "source": "Reddit",
                            "post_title": title,
                            "subreddit": post_data.get("subreddit", "unknown"),
                            "url": f"https://reddit.com{post_data.get('permalink', '')}",
                            "connected_identifiers": mentioned_identifiers,
                            "connected_aliases": mentioned_aliases,
                            "timestamp": datetime.fromtimestamp(post_data.get("created_utc", 0), tz=timezone.utc).isoformat()
                        })
                
                self.log(f"Found {len(connections)} Reddit connections for {identifier}", "SUCCESS")
            else:
                self.log(f"Reddit API returned status {response.status_code}", "WARNING")
                
        except requests.exceptions.RequestException as e:
            self.log(f"Network error querying Reddit: {e}", "WARNING")
            # Offline mode - create mock connection
            connections.append({
                "source": "Reddit",
                "post_title": f"Mock connection analysis for {identifier}",
                "subreddit": "offline_mode",
                "url": "N/A",
                "connected_identifiers": [],
                "connected_aliases": self.aliases[:1] if self.aliases else [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "offline_mode": True
            })
        except Exception as e:
            self.log(f"Error finding Reddit connections: {e}", "ERROR")
        
        return connections
    
    def find_gleif_connections(self, identifier: str) -> List[Dict[str, Any]]:
        """Search GLEIF for entity connections"""
        connections = []
        try:
            # Try searching by identifier
            url = f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]={identifier}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                records = data.get("data", [])
                
                for record in records:
                    entity = record.get("attributes", {}).get("entity", {})
                    legal_name = entity.get("legalName", "")
                    lei = record.get("id", "")
                    
                    # Check if this entity mentions any aliases
                    connected_aliases = []
                    for alias in self.aliases:
                        if alias.lower() in legal_name.lower():
                            connected_aliases.append(alias)
                    
                    connections.append({
                        "source": "GLEIF",
                        "lei": lei,
                        "legal_name": legal_name,
                        "country": entity.get("legalAddress", {}).get("country", "N/A"),
                        "connected_aliases": connected_aliases,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                
                if records:
                    self.log(f"Found {len(connections)} GLEIF connections for {identifier}", "SUCCESS")
                    
        except requests.exceptions.RequestException as e:
            self.log(f"Network error querying GLEIF: {e}", "WARNING")
            # Offline mode - create mock connection
            connections.append({
                "source": "GLEIF",
                "lei": "MOCK-LEI-001",
                "legal_name": f"Mock GLEIF entity for {identifier}",
                "country": "US",
                "connected_aliases": self.aliases[:1] if self.aliases else [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "offline_mode": True
            })
        except Exception as e:
            self.log(f"Error finding GLEIF connections: {e}", "ERROR")
        
        return connections
    
    def find_cross_identifier_connections(self) -> List[Dict[str, Any]]:
        """Find connections between identifiers based on patterns and relationships"""
        connections = []
        
        # Group identifiers by type
        identifier_groups = {}
        for ident in self.identifiers:
            source = ident.get("source", "Unknown")
            if source not in identifier_groups:
                identifier_groups[source] = []
            identifier_groups[source].append(ident["identifier"])
        
        # Create connections between related types
        connection_rules = [
            ("EIN", "EntityName", "Entity-Tax_ID_Relationship"),
            ("SSN", "BirthRegNum", "Person-Birth_Record_Relationship"),
            ("Address", "PropertyRecord", "Location-Property_Relationship"),
            ("ADOTCust", "Address", "Customer-Location_Relationship"),
            ("CSECase", "SSN", "Case-Person_Relationship"),
            ("IRSTrack", "EIN", "Tax_Tracking-Entity_Relationship")
        ]
        
        for source1, source2, relationship_type in connection_rules:
            if source1 in identifier_groups and source2 in identifier_groups:
                for ident1 in identifier_groups[source1]:
                    for ident2 in identifier_groups[source2]:
                        connections.append({
                            "source": "Cross-Identifier_Analysis",
                            "identifier_1": ident1,
                            "identifier_2": ident2,
                            "relationship_type": relationship_type,
                            "confidence": "high",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
        
        self.log(f"Found {len(connections)} cross-identifier connections", "SUCCESS")
        return connections
    
    def find_alias_connections(self) -> List[Dict[str, Any]]:
        """Find connections between identifiers and aliases"""
        connections = []
        
        for ident in self.identifiers:
            identifier = ident["identifier"]
            
            # Check if identifier contains any alias text
            for alias in self.aliases:
                if any(part.lower() in identifier.lower() for part in alias.split()):
                    connections.append({
                        "source": "Alias_Match",
                        "identifier": identifier,
                        "alias": alias,
                        "match_type": "name_component",
                        "confidence": "high",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
            # Check ADOT number connections
            for adot in self.adot_numbers:
                if "ADOT" in identifier and any(part in identifier for part in adot.split("-")):
                    connections.append({
                        "source": "ADOT_Reference",
                        "identifier": identifier,
                        "adot_number": adot,
                        "match_type": "reference_number",
                        "confidence": "medium",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
        
        self.log(f"Found {len(connections)} alias-based connections", "SUCCESS")
        return connections
    
    def build_connection_graph(self):
        """Build a graph representation of all connections"""
        for connection in self.connections:
            # Add nodes and edges based on connection type
            if "identifier_1" in connection and "identifier_2" in connection:
                id1 = connection["identifier_1"]
                id2 = connection["identifier_2"]
                
                if id1 not in self.connection_graph:
                    self.connection_graph[id1] = set()
                if id2 not in self.connection_graph:
                    self.connection_graph[id2] = set()
                
                self.connection_graph[id1].add(id2)
                self.connection_graph[id2].add(id1)
            
            elif "identifier" in connection:
                identifier = connection["identifier"]
                if identifier not in self.connection_graph:
                    self.connection_graph[identifier] = set()
                
                # Add alias connections
                if "alias" in connection:
                    self.connection_graph[identifier].add(connection["alias"])
        
        self.log(f"Built connection graph with {len(self.connection_graph)} nodes", "SUCCESS")
    
    def calculate_connection_metrics(self) -> Dict[str, Any]:
        """Calculate metrics about the connection network"""
        metrics = {
            "total_connections": len(self.connections),
            "connection_types": {},
            "most_connected_identifiers": [],
            "connection_sources": {},
            "relationship_types": {}
        }
        
        # Count connections by type
        for conn in self.connections:
            source = conn.get("source", "Unknown")
            metrics["connection_sources"][source] = metrics["connection_sources"].get(source, 0) + 1
            
            if "relationship_type" in conn:
                rel_type = conn["relationship_type"]
                metrics["relationship_types"][rel_type] = metrics["relationship_types"].get(rel_type, 0) + 1
        
        # Find most connected identifiers
        connection_counts = [(node, len(connections)) for node, connections in self.connection_graph.items()]
        connection_counts.sort(key=lambda x: x[1], reverse=True)
        metrics["most_connected_identifiers"] = [
            {"identifier": node, "connection_count": count}
            for node, count in connection_counts[:5]
        ]
        
        return metrics
    
    def run_comprehensive_scan(self) -> Dict[str, Any]:
        """Run comprehensive connection discovery scan"""
        self.log("Starting Identifier Connections Bot comprehensive scan...", "INFO")
        
        # Load data
        self.load_identifiers()
        self.load_aliases()
        
        # Find connections from all sources
        self.log("Searching for Reddit connections...", "INFO")
        for ident in self.identifiers:
            identifier = ident["identifier"]
            reddit_conns = self.find_reddit_connections(identifier)
            self.connections.extend(reddit_conns)
        
        self.log("Searching for GLEIF connections...", "INFO")
        for ident in self.identifiers:
            identifier = ident["identifier"]
            gleif_conns = self.find_gleif_connections(identifier)
            self.connections.extend(gleif_conns)
        
        self.log("Analyzing cross-identifier connections...", "INFO")
        cross_conns = self.find_cross_identifier_connections()
        self.connections.extend(cross_conns)
        
        self.log("Analyzing alias connections...", "INFO")
        alias_conns = self.find_alias_connections()
        self.connections.extend(alias_conns)
        
        # Build connection graph
        self.log("Building connection graph...", "INFO")
        self.build_connection_graph()
        
        # Calculate metrics
        metrics = self.calculate_connection_metrics()
        
        # Prepare results
        results = {
            "scan_metadata": {
                "bot_name": "Identifier Connections Bot",
                "version": "1.0",
                "scan_timestamp": datetime.now(timezone.utc).isoformat(),
                "total_identifiers_scanned": len(self.identifiers),
                "total_connections_found": len(self.connections)
            },
            "identifiers": [ident["identifier"] for ident in self.identifiers],
            "aliases": self.aliases,
            "adot_numbers": self.adot_numbers,
            "connections": self.connections,
            "connection_graph": {
                node: list(connections) for node, connections in self.connection_graph.items()
            },
            "metrics": metrics
        }
        
        self.log(f"Scan complete! Found {len(self.connections)} total connections", "SUCCESS")
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = "identifier_connections.json") -> str:
        """Save results to JSON file"""
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / filename
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.log(f"Results saved to {output_file}", "SUCCESS")
        return str(output_file)
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print a summary of the scan results"""
        print("\n" + "="*60)
        print("IDENTIFIER CONNECTIONS BOT - SCAN SUMMARY")
        print("="*60)
        
        metadata = results["scan_metadata"]
        print(f"\n🔍 Scanned {metadata['total_identifiers_scanned']} identifiers")
        print(f"🔗 Found {metadata['total_connections_found']} total connections")
        
        metrics = results["metrics"]
        print(f"\n📊 CONNECTION SOURCES:")
        for source, count in metrics["connection_sources"].items():
            print(f"   • {source}: {count} connections")
        
        if metrics["relationship_types"]:
            print(f"\n🔀 RELATIONSHIP TYPES:")
            for rel_type, count in metrics["relationship_types"].items():
                print(f"   • {rel_type}: {count}")
        
        print(f"\n🏆 MOST CONNECTED IDENTIFIERS:")
        for item in metrics["most_connected_identifiers"][:3]:
            print(f"   • {item['identifier']}: {item['connection_count']} connections")
        
        print(f"\n✅ Scan completed: {metadata['scan_timestamp']}")
        print("="*60 + "\n")


def main():
    """Main entry point for Identifier Connections Bot"""
    print("🔗 IDENTIFIER CONNECTIONS BOT")
    print("Comprehensive connection discovery across all trust identifiers")
    print("-" * 60)
    
    bot = IdentifierConnectionsBot(verbose=True)
    
    try:
        # Run comprehensive scan
        results = bot.run_comprehensive_scan()
        
        # Save results
        output_file = bot.save_results(results)
        
        # Print summary
        bot.print_summary(results)
        
        print(f"📄 Full results saved to: {output_file}")
        print("✅ Identifier Connections Bot completed successfully\n")
        
    except KeyboardInterrupt:
        print("\n⚠️  Scan interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during scan: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
