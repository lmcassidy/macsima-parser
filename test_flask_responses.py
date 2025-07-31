#!/usr/bin/env python3
"""
Test script to verify Flask app returns proper JSON error responses
"""

import json
from app import app, get_user_friendly_error_message

def test_error_message_function():
    """Test the error message function directly"""
    
    # Test JSONDecodeError
    json_error = json.JSONDecodeError("Expecting value", "test", 0)
    message = get_user_friendly_error_message(json_error, "invalid_empty.json")
    print(f"JSONDecodeError message: {message}")
    
    # Test KeyError  
    key_error = KeyError("experiments")
    message = get_user_friendly_error_message(key_error, "missing_experiments.json")
    print(f"KeyError message: {message}")
    
    # Test generic error
    generic_error = Exception("Something went wrong")
    message = get_user_friendly_error_message(generic_error, "test.json")
    print(f"Generic error message: {message}")

def test_flask_app():
    """Test Flask app with test client"""
    
    with app.test_client() as client:
        # Test empty file
        with open('data/test-samples/invalid_empty.json', 'rb') as f:
            response = client.post('/upload', data={'file': (f, 'invalid_empty.json')})
            print(f"Empty file response status: {response.status_code}")
            if response.content_type == 'application/json':
                data = response.get_json()
                print(f"Empty file error message: {data.get('message')}")
            else:
                print(f"Response content type: {response.content_type}")
                print(f"Response data: {response.get_data(as_text=True)[:200]}")
        
        # Test missing experiments file
        with open('data/test-samples/missing_experiments.json', 'rb') as f:
            response = client.post('/upload', data={'file': (f, 'missing_experiments.json')})
            print(f"Missing experiments response status: {response.status_code}")
            if response.content_type == 'application/json':
                data = response.get_json()
                print(f"Missing experiments error message: {data.get('message')}")
            else:
                print(f"Response content type: {response.content_type}")

if __name__ == '__main__':
    print("Testing error message function...")
    test_error_message_function()
    print("\nTesting Flask app...")
    test_flask_app()