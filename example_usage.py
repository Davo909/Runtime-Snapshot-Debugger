"""
Example usage of the Runtime Snapshot Debugger for small/new developers

This file demonstrates how to use the snapshot debugger to:
1. Capture application state during development
2. Debug issues more effectively
3. Create test cases automatically
4. Track errors and requests
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"

def create_test_snapshots():
    """Create example snapshots for different scenarios"""
    
    print("🚀 Creating example snapshots...")
    
    # Example 1: User registration
    print("\n1. Creating user registration snapshot...")
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "secure123"
    }
    
    response = requests.post(f"{BASE_URL}/snapshot/manual", json={
        "label": "User Registration",
        "path": "/api/users/register",
        "tags": ["user", "registration", "auth"],
        "json": user_data
    })
    
    if response.status_code == 200:
        snap_id = response.json()["snapshot_id"]
        print(f"✅ User registration snapshot created: {snap_id}")
        
        # Set expected output
        expected_output = {
            "user_id": "user_123",
            "status": "created",
            "message": "User registered successfully"
        }
        
        requests.post(f"{BASE_URL}/snapshot/{snap_id}/expected", json={
            "expected_output": expected_output
        })
        print("✅ Expected output set")
    
    # Example 2: Payment processing
    print("\n2. Creating payment processing snapshot...")
    payment_data = {
        "amount": 99.99,
        "currency": "USD",
        "user_id": "user_123",
        "payment_method": "credit_card"
    }
    
    response = requests.post(f"{BASE_URL}/snapshot/manual", json={
        "label": "Payment Processing",
        "path": "/api/payments/process",
        "tags": ["payment", "financial", "critical"],
        "json": payment_data
    })
    
    if response.status_code == 200:
        snap_id = response.json()["snapshot_id"]
        print(f"✅ Payment processing snapshot created: {snap_id}")
        
        # Set expected output
        expected_output = {
            "transaction_id": "txn_456",
            "status": "completed",
            "amount": 99.99,
            "currency": "USD"
        }
        
        requests.post(f"{BASE_URL}/snapshot/{snap_id}/expected", json={
            "expected_output": expected_output
        })
        print("✅ Expected output set")
    
    # Example 3: API error scenario
    print("\n3. Creating error scenario snapshot...")
    invalid_data = {
        "amount": "invalid_amount",  # This should cause an error
        "user_id": None
    }
    
    response = requests.post(f"{BASE_URL}/snapshot/manual", json={
        "label": "Invalid Payment Data",
        "path": "/api/payments/process",
        "tags": ["error", "validation", "debug"],
        "json": invalid_data
    })
    
    if response.status_code == 200:
        snap_id = response.json()["snapshot_id"]
        print(f"✅ Error scenario snapshot created: {snap_id}")
        
        # Set expected output for error case
        expected_output = {
            "error": "Invalid amount format",
            "status": "error",
            "code": 400
        }
        
        requests.post(f"{BASE_URL}/snapshot/{snap_id}/expected", json={
            "expected_output": expected_output
        })
        print("✅ Expected error output set")

def test_snapshots():
    """Test the created snapshots"""
    print("\n🧪 Testing snapshots...")
    
    # Get all snapshots
    response = requests.get(f"{BASE_URL}/snapshots")
    snapshots = response.json()
    
    for snapshot in snapshots:
        print(f"\nTesting snapshot: {snapshot['label']}")
        
        # Replay the snapshot
        response = requests.post(f"{BASE_URL}/snapshot/{snapshot['id']}/replay")
        result = response.json()
        
        if result.get("match"):
            print(f"✅ {snapshot['label']} - Test passed!")
        else:
            print(f"❌ {snapshot['label']} - Test failed!")
            print(f"Expected: {result.get('expected_output')}")
            print(f"Got: {result.get('replayed_state')}")

def check_debug_info():
    """Check debug information"""
    print("\n🐛 Checking debug information...")
    
    # Get debug stats
    response = requests.get(f"{BASE_URL}/debug/stats")
    stats = response.json()
    
    print(f"📊 Debug Statistics:")
    print(f"  - Total snapshots: {stats['total_snapshots']}")
    print(f"  - Total requests: {stats['total_requests']}")
    print(f"  - Total errors: {stats['total_errors']}")
    print(f"  - Error rate: {stats['error_rate']:.1f}%")
    print(f"  - Uptime: {stats['uptime']:.0f} seconds")
    
    # Get recent errors
    response = requests.get(f"{BASE_URL}/debug/errors")
    errors = response.json()
    
    if errors['errors']:
        print(f"\n⚠️ Recent Errors ({len(errors['errors'])}):")
        for error in errors['errors'][-3:]:  # Show last 3 errors
            print(f"  - {error['error_type']}: {error['error_message']}")
            print(f"    💡 Tip: {error['debug_tip']}")
    else:
        print("\n✅ No errors recorded!")

def generate_test_files():
    """Generate test files from snapshots"""
    print("\n📝 Generating test files...")
    
    response = requests.get(f"{BASE_URL}/snapshots")
    snapshots = response.json()
    
    for snapshot in snapshots:
        print(f"Generating test for: {snapshot['label']}")
        
        # Generate test file
        response = requests.get(f"{BASE_URL}/snapshot/{snapshot['id']}/generate-test")
        
        if response.status_code == 200:
            filename = f"test_{snapshot['label'].lower().replace(' ', '_')}.py"
            with open(filename, 'w') as f:
                f.write(response.text)
            print(f"✅ Generated: {filename}")

def main():
    """Main function to demonstrate the tool"""
    print("🎯 Runtime Snapshot Debugger - Example Usage")
    print("=" * 50)
    
    try:
        # Create example snapshots
        create_test_snapshots()
        
        # Wait a moment for processing
        time.sleep(1)
        
        # Test the snapshots
        test_snapshots()
        
        # Check debug information
        check_debug_info()
        
        # Generate test files
        generate_test_files()
        
        print("\n🎉 Example completed successfully!")
        print("\n💡 Tips for small/new developers:")
        print("  1. Use the debug panel to monitor errors and requests")
        print("  2. Create snapshots when you encounter bugs")
        print("  3. Set expected outputs to catch regressions")
        print("  4. Use tags to organize your snapshots")
        print("  5. Export logs when sharing issues with others")
        print("  6. Generate test files for automated testing")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the debugger server.")
        print("Make sure the Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 