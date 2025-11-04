#!/usr/bin/env python3
"""
DNS Configuration Helper for GitHub Actions
This script helps configure alternative DNS servers if the default DNS is failing
"""

import subprocess
import sys
import os


def is_root():
    """Check if script is running with root privileges (Unix only)"""
    # os.geteuid() is not available on Windows; handle gracefully
    if hasattr(os, "geteuid"):
        return os.geteuid() == 0
    else:
        print("⚠️ Root check is not supported on this platform. This script is intended for Unix-like systems.")
        return False


def test_dns(hostname, nameserver=None):
    """Test DNS resolution for a hostname"""
    try:
        if nameserver:
            result = subprocess.run(
                ['nslookup', hostname, nameserver],
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            result = subprocess.run(
                ['nslookup', hostname],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error testing DNS for {hostname}: {e}")
        return False


def configure_dns_servers(servers):
    """Configure DNS servers in /etc/resolv.conf"""
    if not is_root():
        print("⚠️ Root privileges required to modify DNS configuration")
        print("Run with: sudo python dns_config_helper.py")
        return False
    
    try:
        # Backup existing resolv.conf
        subprocess.run(['cp', '/etc/resolv.conf', '/etc/resolv.conf.backup'], check=True)
        print("✅ Backed up /etc/resolv.conf to /etc/resolv.conf.backup")
        
        # Write new DNS configuration
        with open('/etc/resolv.conf', 'w') as f:
            for server in servers:
                f.write(f"nameserver {server}\n")
        
        print(f"✅ Configured DNS servers: {', '.join(servers)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to configure DNS: {e}")
        return False


def main():
    print("=" * 60)
    print("DNS Configuration Helper for GitHub Actions")
    print("=" * 60)
    print()
    
    # Test hostnames
    test_hosts = [
        'api.gleif.org',
        'www.reddit.com',
        'www.google.com'
    ]
    
    # Alternative DNS servers to try
    dns_servers = [
        ('Google DNS Primary', '8.8.8.8'),
        ('Google DNS Secondary', '8.8.4.4'),
        ('Cloudflare DNS Primary', '1.1.1.1'),
        ('Cloudflare DNS Secondary', '1.0.0.1'),
        ('Quad9 DNS', '9.9.9.9'),
        ('OpenDNS Primary', '208.67.222.222'),
        ('OpenDNS Secondary', '208.67.220.220'),
    ]
    
    print("Step 1: Testing current DNS configuration")
    print("-" * 60)
    
    current_dns_working = True
    for host in test_hosts:
        result = test_dns(host)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {host}")
        if not result:
            current_dns_working = False
    
    print()
    
    if current_dns_working:
        print("✅ Current DNS configuration is working correctly!")
        print("No changes needed.")
        return 0
    
    print("⚠️ Current DNS configuration has issues.")
    print()
    print("Step 2: Testing alternative DNS servers")
    print("-" * 60)
    
    working_servers = []
    for name, server in dns_servers:
        print(f"\nTesting {name} ({server}):")
        all_working = True
        for host in test_hosts:
            result = test_dns(host, server)
            status = "✅" if result else "❌"
            print(f"  {status} {host}")
            if not result:
                all_working = False
        
        if all_working:
            working_servers.append(server)
            print(f"  ✅ {name} can resolve all test hosts")
    
    print()
    print("=" * 60)
    
    if not working_servers:
        print("❌ No alternative DNS servers could resolve the hosts")
        print("This may indicate a network firewall or proxy issue.")
        print()
        print("Recommendations:")
        print("1. Check firewall rules (port 53 UDP/TCP)")
        print("2. Verify network proxy configuration")
        print("3. Contact network administrator")
        print("4. See NETWORK_TROUBLESHOOTING.md for more options")
        return 1
    
    print(f"✅ Found {len(working_servers)} working DNS server(s)")
    print()
    
    # Offer to configure DNS
    if is_root():
        print("Configure these DNS servers? (yes/no)")
        response = input("> ").strip().lower()
        
        if response in ['yes', 'y']:
            if configure_dns_servers(working_servers[:2]):  # Use top 2 servers
                print()
                print("✅ DNS configuration updated successfully!")
                print()
                print("Testing new configuration:")
                print("-" * 60)
                for host in test_hosts:
                    result = test_dns(host)
                    status = "✅ PASS" if result else "❌ FAIL"
                    print(f"{status} - {host}")
                
                print()
                print("To revert changes, run:")
                print("  sudo cp /etc/resolv.conf.backup /etc/resolv.conf")
                return 0
            else:
                return 1
        else:
            print("DNS configuration not changed.")
            print()
            print("To manually configure, add these lines to /etc/resolv.conf:")
            for server in working_servers[:2]:
                print(f"  nameserver {server}")
            return 0
    else:
        print("To configure these DNS servers, run:")
        print()
        print("  sudo python dns_config_helper.py")
        print()
        print("Or add manually to workflow:")
        print()
        print("  - name: Configure DNS")
        print("    run: |")
        for server in working_servers[:2]:
            print(f"      echo 'nameserver {server}' | sudo tee /etc/resolv.conf")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
