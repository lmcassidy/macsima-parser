#!/usr/bin/env python3
"""
Quick test script to verify error handling works correctly
"""

import requests
import json

def test_error_file():
    """Test uploading an invalid file to the Flask app"""
    
    # Create a simple invalid JSON file
    invalid_content = "{ this is not valid json"
    
    # Upload to the Flask app (assuming it's running on localhost:5001)
    try:
        with open('/tmp/invalid_test.json', 'w') as f:
            f.write(invalid_content)
        
        files = {'file': ('invalid_test.json', open('/tmp/invalid_test.json', 'rb'), 'application/json')}
        response = requests.post('http://localhost:5001/upload', files=files)
        
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            error_data = response.json()
            print(f"Error response: {error_data}")
        else:
            print(f"Response text: {response.text[:500]}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == '__main__':
    test_error_file()