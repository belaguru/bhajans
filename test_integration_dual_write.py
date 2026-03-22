"""
Quick integration test for dual-write implementation
Run this after starting the server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_bhajan():
    """Test creating a bhajan with tags"""
    print("\n1. Creating bhajan with tags...")
    
    response = requests.post(
        f"{BASE_URL}/api/bhajans",
        data={
            "title": "Test Dual Write Bhajan",
            "lyrics": "This is a test bhajan for dual-write strategy\nSecond line of lyrics",
            "tags": "hanuman,rama,bhajan",
            "uploader_name": "Test User"
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        bhajan = response.json()
        print(f"Created bhajan ID: {bhajan['id']}")
        print(f"Tags: {bhajan['tags']}")
        return bhajan['id']
    else:
        print(f"Error: {response.text}")
        return None


def test_get_bhajan(bhajan_id):
    """Test retrieving bhajan with unified tags"""
    print(f"\n2. Retrieving bhajan {bhajan_id}...")
    
    response = requests.get(f"{BASE_URL}/api/bhajans/{bhajan_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        bhajan = response.json()
        print(f"Title: {bhajan['title']}")
        print(f"Tags: {bhajan['tags']}")
        print(f"Tags type: {type(bhajan['tags'])}")
    else:
        print(f"Error: {response.text}")


def test_update_bhajan(bhajan_id):
    """Test updating bhajan tags"""
    print(f"\n3. Updating bhajan {bhajan_id} with new tags...")
    
    response = requests.put(
        f"{BASE_URL}/api/bhajans/{bhajan_id}",
        data={
            "tags": "krishna,aarti"
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        bhajan = response.json()
        print(f"Updated tags: {bhajan['tags']}")
    else:
        print(f"Error: {response.text}")


def test_list_bhajans():
    """Test listing all bhajans"""
    print("\n4. Listing all bhajans...")
    
    response = requests.get(f"{BASE_URL}/api/bhajans")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        bhajans = response.json()
        print(f"Total bhajans: {len(bhajans)}")
        for b in bhajans[:3]:
            print(f"  - {b['title']}: {b['tags']}")
    else:
        print(f"Error: {response.text}")


def test_cleanup(bhajan_id):
    """Delete test bhajan"""
    print(f"\n5. Cleaning up (deleting bhajan {bhajan_id})...")
    
    response = requests.delete(f"{BASE_URL}/api/bhajans/{bhajan_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Cleanup successful")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    print("=" * 60)
    print("DUAL-WRITE INTEGRATION TEST")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print("=" * 60)
    
    # Test create
    bhajan_id = test_create_bhajan()
    
    if bhajan_id:
        # Test get
        test_get_bhajan(bhajan_id)
        
        # Test update
        test_update_bhajan(bhajan_id)
        
        # Test get again
        test_get_bhajan(bhajan_id)
        
        # Test list
        test_list_bhajans()
        
        # Cleanup
        test_cleanup(bhajan_id)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
