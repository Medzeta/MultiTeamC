"""
Test GitHub API för att diagnostisera problem
"""

import requests
import json

def test_github_api():
    """Testa GitHub API anslutning"""
    
    # GitHub API URL
    api_url = "https://api.github.com/repos/Medzeta/Multi-Team-C/releases/latest"
    
    print("Testing GitHub API...")
    print(f"URL: {api_url}")
    print("-" * 50)
    
    try:
        # Test basic connectivity
        print("1. Testing basic connectivity...")
        response = requests.get(api_url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API call successful!")
            data = response.json()
            print(f"Latest release: {data.get('tag_name', 'Unknown')}")
            print(f"Release name: {data.get('name', 'Unknown')}")
            print(f"Published: {data.get('published_at', 'Unknown')}")
            
            # Check assets
            assets = data.get('assets', [])
            print(f"Assets: {len(assets)} files")
            for asset in assets:
                print(f"  - {asset['name']} ({asset['size']} bytes)")
                
        elif response.status_code == 404:
            print("❌ Repository not found or no releases")
            print("Check if:")
            print("  - Repository exists: https://github.com/Medzeta/Multi-Team-C")
            print("  - Repository is public")
            print("  - At least one release exists")
            
        elif response.status_code == 403:
            print("❌ API rate limit exceeded")
            print("Wait a few minutes and try again")
            
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - check internet connection")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check internet connection")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_github_api()
