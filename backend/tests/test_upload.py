#!/usr/bin/env python3
"""Test script for crop diagnosis endpoint"""

import io

import requests
from PIL import Image


def create_test_image():
    """Create a simple test image"""
    # Create a simple RGB image
    image = Image.new('RGB', (100, 100), color='red')

    # Save to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr

def test_endpoint():
    """Test the crop diagnosis endpoint"""
    url = "http://localhost:8000/api/v1/crop/diagnose"

    # Create test image
    image_data = create_test_image()

    # Prepare files for multipart upload
    files = {
        'image': ('test_crop.jpg', image_data, 'image/jpeg')
    }

    # Optional form data
    data = {
        'description': 'Test image from Python script'
    }

    try:
        print(f"Sending POST request to: {url}")
        print(f"Image size: {len(image_data)} bytes")

        response = requests.post(url, files=files, data=data)

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.ok:
            print("✅ Success!")
            print(f"Response: {response.json()}")
        else:
            print("❌ Error!")
            print(f"Response text: {response.text}")

    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    test_endpoint()
