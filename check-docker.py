#!/usr/bin/env python3
"""
Quick script to check if Docker services are running.
Run this before starting Streamlit.
"""

import requests
import sys

def check_service(url, name):
    try:
        r = requests.get(url, timeout=2)
        print(f"✅ {name}: Running")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Not running (connection refused)")
        return False
    except requests.exceptions.Timeout:
        print(f"⚠️  {name}: Timeout (may be starting)")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def main():
    print("🔍 Checking Docker services...\n")
    
    services = {
        "Faulty App": "http://localhost:8080/health",
        "Prometheus": "http://localhost:9090/-/ready",
        "Loki": "http://localhost:3100/ready"
    }
    
    results = {}
    for name, url in services.items():
        results[name] = check_service(url, name)
    
    print("\n" + "="*50)
    
    if all(results.values()):
        print("✅ All services are running!")
        print("\nYou can now run: streamlit run app.py")
        sys.exit(0)
    else:
        print("❌ Some services are not running!")
        print("\nTo start Docker containers, run:")
        print("  docker compose up -d --build")
        print("\nThen wait 30-60 seconds and run this script again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
