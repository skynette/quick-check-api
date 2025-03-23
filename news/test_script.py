#!/usr/bin/env python
"""
Hacker News API Test Script

This script tests all endpoints of the Hacker News API application hosted at
quick-check.up.railway.app/api/ according to the specified criteria.

Usage:
    python test_hn_api.py
"""

import requests
import json
import time
from datetime import datetime
import random
import argparse

# API base URL
BASE_URL = "http://localhost:8000/api"

# Headers for requests
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def print_section(title):
    """Print a section header to make output more readable"""
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80 + "\n")

def print_response(response, label=None):
    """Pretty print a response for debugging"""
    if label:
        print(f"\n--- {label} ---")
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    try:
        print("Response Body:")
        pretty_json = json.dumps(response.json(), indent=2)
        # Limit output to prevent flooding the console
        if len(pretty_json) > 1000:
            print(pretty_json[:1000] + "...\n(truncated)")
        else:
            print(pretty_json)
    except:
        print(f"Raw Response: {response.text[:500]}...")
    print()

def test_list_items():
    """Test the GET /items/ endpoint with various filters"""
    print_section("TESTING LIST ITEMS ENDPOINT")
    
    # Test basic list endpoint
    print("Testing basic list endpoint...")
    response = requests.get(f"{BASE_URL}/items/", headers=HEADERS)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    
    assert "count" in data, "Response missing 'count' field"
    assert "results" in data, "Response missing 'results' field"
    
    total_count = data["count"]
    print(f"Total items in database: {total_count}")
    
    # Save the first item for later tests
    first_item = None
    if data["results"]:
        first_item = data["results"][0]
        print(f"First item type: {first_item.get('type')}, ID: {first_item.get('item_id')}")
    
    # Test pagination
    print("\nTesting pagination...")
    page_size = len(data["results"])
    print(f"Default page size: {page_size}")
    
    if data.get("next"):
        print("Testing next page link...")
        response = requests.get(data["next"], headers=HEADERS)
        assert response.status_code == 200, f"Pagination failed with status code {response.status_code}"
        print(f"Successfully retrieved page 2 with {len(response.json()['results'])} items")
    
    # Test filtering by type
    if first_item:
        item_type = first_item.get("type", "story")
        print(f"\nTesting filtering by type '{item_type}'...")
        response = requests.get(f"{BASE_URL}/items/?type={item_type}", headers=HEADERS)
        assert response.status_code == 200
        filtered_data = response.json()
        
        # Check if all items match the filter
        all_match = all(item["type"] == item_type for item in filtered_data["results"])
        assert all_match, f"Not all items match the filter type '{item_type}'"
        print(f"Successfully filtered by type '{item_type}': {filtered_data['count']} items found")
    
    # Test filtering by top-level items
    print("\nTesting filtering for top-level items...")
    response = requests.get(f"{BASE_URL}/items/?top_level=true", headers=HEADERS)
    assert response.status_code == 200
    top_level_data = response.json()
    print(f"Top-level items: {top_level_data['count']}")
    
    # Test search functionality
    print("\nTesting search functionality...")
    search_term = "python"  # Common term that might appear in HN posts
    response = requests.get(f"{BASE_URL}/items/?search={search_term}", headers=HEADERS)
    assert response.status_code == 200
    search_data = response.json()
    print(f"Search results for '{search_term}': {search_data['count']} items found")
    
    # Test combined filters
    print("\nTesting combined filters...")
    response = requests.get(f"{BASE_URL}/items/?type=story&top_level=true", headers=HEADERS)
    assert response.status_code == 200
    combined_data = response.json()
    print(f"Stories that are top-level: {combined_data['count']} items found")
    
    # Test ordering
    print("\nTesting ordering by score (descending)...")
    response = requests.get(f"{BASE_URL}/items/?ordering=-score", headers=HEADERS)
    assert response.status_code == 200
    ordered_data = response.json()
    
    if len(ordered_data["results"]) >= 2:
        first_score = ordered_data["results"][0].get("score", 0)
        second_score = ordered_data["results"][1].get("score", 0)
        print(f"First item score: {first_score}, Second item score: {second_score}")
        assert first_score >= second_score, "Ordering by score descending failed"
    
    print("\nList endpoint tests completed successfully!")
    return first_item

def test_item_detail(item_id):
    """Test the GET /items/{item_id}/ endpoint"""
    print_section(f"TESTING ITEM DETAIL ENDPOINT FOR ITEM {item_id}")
    
    response = requests.get(f"{BASE_URL}/items/{item_id}/", headers=HEADERS)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    item_data = response.json()
    print(f"Successfully retrieved item {item_id}")
    print(f"Title: {item_data.get('title')}")
    print(f"Type: {item_data.get('type')}")
    print(f"Author: {item_data.get('by')}")
    print(f"Score: {item_data.get('score')}")
    
    # Check if comments are included
    if "comments" in item_data:
        comments = item_data["comments"]
        print(f"Number of comments: {len(comments)}")
        if comments:
            print(f"First comment by: {comments[0].get('by')}")
    
    print("\nItem detail endpoint test completed successfully!")
    return item_data

def test_create_item():
    """Test the POST /items/ endpoint"""
    print_section("TESTING CREATE ITEM ENDPOINT")
    
    # Create a new item
    new_item = {
        "type": "story",
        "by": "api_test_user",
        "title": f"Test Story Created at {datetime.now().isoformat()}",
        "text": "This is a test story created by the API test script.",
        "score": random.randint(1, 100)
    }
    
    print(f"Creating new item with title: {new_item['title']}")
    response = requests.post(f"{BASE_URL}/items/", json=new_item, headers=HEADERS)
    
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    created_item = response.json()
    
    print(f"Successfully created item with ID: {created_item.get('item_id')}")
    print(f"Item marked as created_locally: {created_item.get('created_locally')}")
    
    # Verify the item was created correctly
    assert created_item.get("title") == new_item["title"]
    assert created_item.get("by") == new_item["by"]
    assert created_item.get("created_locally") == True
    
    print("\nCreate item endpoint test completed successfully!")
    return created_item

def test_update_item(item_id):
    """Test the PUT and PATCH /items/{item_id}/ endpoints"""
    print_section(f"TESTING UPDATE ITEM ENDPOINT FOR ITEM {item_id}")
    
    # Update the item with PATCH
    update_data = {
        "title": f"Updated Test Story at {datetime.now().isoformat()}",
        "score": random.randint(1, 100)
    }
    
    print(f"Updating item {item_id} with new title: {update_data['title']}")
    response = requests.patch(f"{BASE_URL}/items/{item_id}/", json=update_data, headers=HEADERS)
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    updated_item = response.json()
    
    print(f"Successfully updated item {item_id}")
    assert updated_item.get("title") == update_data["title"]
    assert updated_item.get("score") == update_data["score"]
    
    # Now try a full update with PUT
    full_update_data = {
        "type": "story",
        "by": "api_test_user_updated",
        "title": f"Fully Updated Test Story at {datetime.now().isoformat()}",
        "text": "This story has been fully updated by the API test script.",
        "score": random.randint(1, 100),
        "time": datetime.now().isoformat()
    }
    
    print(f"\nFully updating item {item_id} with PUT")
    response = requests.put(f"{BASE_URL}/items/{item_id}/", json=full_update_data, headers=HEADERS)
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    fully_updated_item = response.json()
    
    print(f"Successfully performed full update on item {item_id}")
    assert fully_updated_item.get("title") == full_update_data["title"]
    assert fully_updated_item.get("by") == full_update_data["by"]
    
    print("\nUpdate item endpoint tests completed successfully!")
    return fully_updated_item

def test_delete_item(item_id):
    """Test the DELETE /items/{item_id}/ endpoint"""
    print_section(f"TESTING DELETE ITEM ENDPOINT FOR ITEM {item_id}")
    
    print(f"Deleting item {item_id}...")
    response = requests.delete(f"{BASE_URL}/items/{item_id}/", headers=HEADERS)
    
    assert response.status_code == 204, f"Expected status code 204, got {response.status_code}"
    print(f"Successfully deleted item {item_id}")
    
    # Verify the item is gone
    response = requests.get(f"{BASE_URL}/items/{item_id}/", headers=HEADERS)
    assert response.status_code == 404, f"Expected item to be gone (404), got {response.status_code}"
    print("Verified item is deleted")
    
    print("\nDelete item endpoint test completed successfully!")

def test_hn_item_protection():
    """Test that Hacker News items are protected from updates/deletes"""
    print_section("TESTING PROTECTION OF HACKER NEWS ITEMS")
    
    # First, get a regular HN item (not created through our API)
    response = requests.get(f"{BASE_URL}/items/?created_locally=false", headers=HEADERS)
    assert response.status_code == 200
    
    data = response.json()
    if not data["results"]:
        print("No Hacker News items found in the database. Skipping protection test.")
        return
    
    hn_item = data["results"][0]
    hn_item_id = hn_item["item_id"]
    
    print(f"Found Hacker News item with ID {hn_item_id}")
    
    # Try to update it
    print(f"Attempting to update Hacker News item {hn_item_id}...")
    update_data = {"title": "This should fail"}
    response = requests.patch(f"{BASE_URL}/items/{hn_item_id}/", json=update_data, headers=HEADERS)
    
    # Should be forbidden
    assert response.status_code == 403, f"Expected status code 403, got {response.status_code}"
    print("Update correctly blocked with 403 Forbidden")
    
    # Try to delete it
    print(f"Attempting to delete Hacker News item {hn_item_id}...")
    response = requests.delete(f"{BASE_URL}/items/{hn_item_id}/", headers=HEADERS)
    
    # Should be forbidden
    assert response.status_code == 403, f"Expected status code 403, got {response.status_code}"
    print("Delete correctly blocked with 403 Forbidden")
    
    print("\nHacker News item protection tests completed successfully!")

def test_sync_endpoint():
    """Test the POST /sync/ endpoint"""
    print_section("TESTING SYNC ENDPOINT")
    
    # Check how many items before sync
    response = requests.get(f"{BASE_URL}/items/", headers=HEADERS)
    before_count = response.json()["count"]
    print(f"Items before sync: {before_count}")
    
    # Trigger a sync with a small count
    sync_data = {"count": 5}  # Small number to make the test quick
    print(f"Triggering sync with count={sync_data['count']}...")
    response = requests.post(f"{BASE_URL}/sync/", json=sync_data, headers=HEADERS)
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    sync_result = response.json()
    print(f"Sync result: {sync_result}")
    
    # Give a little time for the sync to complete
    print("Waiting for sync to complete...")
    time.sleep(2)
    
    # Check how many items after sync
    response = requests.get(f"{BASE_URL}/items/", headers=HEADERS)
    after_count = response.json()["count"]
    print(f"Items after sync: {after_count}")
    
    print("\nSync endpoint test completed!")

def main():
    global BASE_URL
    
    parser = argparse.ArgumentParser(description="Test the Hacker News API")
    parser.add_argument("--url", default=BASE_URL, help="Base URL for the API")
    parser.add_argument("--skip-delete", action="store_true", help="Skip deletion tests")
    args = parser.parse_args()
    
    BASE_URL = args.url

    print(f"Testing Hacker News API at: {BASE_URL}")
    
    try:
        # Test list endpoint and get a sample item
        sample_item = test_list_items()
        
        if sample_item:
            # Test item detail endpoint
            test_item_detail(sample_item["item_id"])
        
        # Test create, update, delete cycle
        created_item = test_create_item()
        updated_item = test_update_item(created_item["item_id"])
        
        if not args.skip_delete:
            test_delete_item(updated_item["item_id"])
        
        # Test protection of HN items
        test_hn_item_protection()
        
        # Test sync endpoint
        test_sync_endpoint()
        
        print_section("ALL TESTS COMPLETED SUCCESSFULLY!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
    except Exception as e:
        print(f"\n❌ ERROR DURING TESTING: {str(e)}")

if __name__ == "__main__":
    main()