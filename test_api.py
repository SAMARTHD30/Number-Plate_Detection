import requests
import os

def test_api():
    # API endpoint
    base_url = "http://localhost:8000/api/v1"

    # Test image path - replace with your test image
    test_image = "test_car.jpg"

    if not os.path.exists(test_image):
        print(f"Error: Test image '{test_image}' not found!")
        print("Please place a test image in the same directory as this script.")
        return

    print("Testing License Plate Detection API...")

    # Test 1: Detect endpoint
    print("\n1. Testing /detect endpoint...")
    try:
        with open(test_image, "rb") as f:
            files = {"image": f}
            response = requests.post(f"{base_url}/detect", files=files)
            if response.status_code == 200:
                print("✓ Detect endpoint working!")
                print(f"Response: {response.json()}")
            else:
                print(f"✗ Detect endpoint failed with status code: {response.status_code}")
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ Error testing detect endpoint: {str(e)}")

    # Test 2: Process endpoint
    print("\n2. Testing /process endpoint...")
    try:
        with open(test_image, "rb") as f:
            files = {"car_image": f}
            data = {"custom_text": "TEST123"}
            response = requests.post(f"{base_url}/process", files=files, data=data)
            if response.status_code == 200:
                print("✓ Process endpoint working!")
                # Save the processed image
                with open("processed_test.jpg", "wb") as f:
                    f.write(response.content)
                print("✓ Processed image saved as 'processed_test.jpg'")
            else:
                print(f"✗ Process endpoint failed with status code: {response.status_code}")
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ Error testing process endpoint: {str(e)}")

if __name__ == "__main__":
    test_api()