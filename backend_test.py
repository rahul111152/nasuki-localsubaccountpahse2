#!/usr/bin/env python3
"""
NASUKI Backend Auth Foundation Test Suite
Tests all auth endpoints and status endpoints via external URL.
"""
import requests
import json
import sys
from typing import Dict, Any

# Read the external backend URL from frontend/.env
BASE_URL = "https://bc2c004e-1d7d-4fb5-a341-84f48bac2a81.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log_test(name: str):
    print(f"\n{Colors.BLUE}[TEST]{Colors.RESET} {name}")

def log_pass(msg: str):
    print(f"  {Colors.GREEN}✓{Colors.RESET} {msg}")

def log_fail(msg: str):
    print(f"  {Colors.RED}✗{Colors.RESET} {msg}")

def log_info(msg: str):
    print(f"  {Colors.YELLOW}ℹ{Colors.RESET} {msg}")

def test_root_endpoint():
    """Test 1: GET /api/ should return 200 with correct JSON"""
    log_test("GET /api/ - Health check")
    try:
        resp = requests.get(f"{API_BASE}/", timeout=10)
        log_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            log_fail(f"Expected 200, got {resp.status_code}")
            return False
        
        data = resp.json()
        log_info(f"Response: {json.dumps(data)}")
        
        if data.get("message") != "NASUKI API":
            log_fail(f"Expected message='NASUKI API', got '{data.get('message')}'")
            return False
        
        if data.get("status") != "ok":
            log_fail(f"Expected status='ok', got '{data.get('status')}'")
            return False
        
        log_pass("Root endpoint working correctly")
        return True
    except Exception as e:
        log_fail(f"Exception: {e}")
        return False

def test_status_roundtrip():
    """Test 2: POST /api/status then GET /api/status"""
    log_test("POST /api/status + GET /api/status - Status roundtrip")
    try:
        # POST a new status check
        payload = {"client_name": "backend_test_suite"}
        resp = requests.post(f"{API_BASE}/status", json=payload, timeout=10)
        log_info(f"POST status: {resp.status_code}")
        
        if resp.status_code != 200:
            log_fail(f"POST expected 200, got {resp.status_code}")
            log_info(f"Response: {resp.text}")
            return False
        
        created = resp.json()
        log_info(f"Created: {json.dumps(created)}")
        
        # Verify response has required fields
        if "id" not in created:
            log_fail("Response missing 'id' field")
            return False
        if created.get("client_name") != "backend_test_suite":
            log_fail(f"client_name mismatch: {created.get('client_name')}")
            return False
        if "timestamp" not in created:
            log_fail("Response missing 'timestamp' field")
            return False
        
        created_id = created["id"]
        log_pass(f"Status check created with id={created_id}")
        
        # GET all status checks
        resp = requests.get(f"{API_BASE}/status", timeout=10)
        log_info(f"GET status: {resp.status_code}")
        
        if resp.status_code != 200:
            log_fail(f"GET expected 200, got {resp.status_code}")
            return False
        
        status_list = resp.json()
        log_info(f"Retrieved {len(status_list)} status checks")
        
        # Verify our created status is in the list
        found = any(s.get("id") == created_id for s in status_list)
        if not found:
            log_fail(f"Created status check (id={created_id}) not found in list")
            return False
        
        log_pass("Status roundtrip working correctly")
        return True
    except Exception as e:
        log_fail(f"Exception: {e}")
        return False

def test_auth_me_no_header():
    """Test 3: GET /api/auth/me without Authorization header should return 401"""
    log_test("GET /api/auth/me (no Authorization) - Should return 401")
    try:
        resp = requests.get(f"{API_BASE}/auth/me", timeout=10)
        log_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 401:
            log_fail(f"Expected 401, got {resp.status_code}")
            log_info(f"Response: {resp.text}")
            return False
        
        log_pass("Correctly returned 401 for missing Authorization")
        return True
    except Exception as e:
        log_fail(f"Exception: {e}")
        return False

def test_auth_me_invalid_token():
    """Test 4: GET /api/auth/me with invalid Bearer token should return 401"""
    log_test("GET /api/auth/me (invalid Bearer token) - Should return 401")
    try:
        headers = {"Authorization": "Bearer bogus-token-123"}
        resp = requests.get(f"{API_BASE}/auth/me", headers=headers, timeout=10)
        log_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 401:
            log_fail(f"Expected 401, got {resp.status_code}")
            log_info(f"Response: {resp.text}")
            return False
        
        log_pass("Correctly returned 401 for invalid token")
        return True
    except Exception as e:
        log_fail(f"Exception: {e}")
        return False

def test_auth_session_empty_session_id():
    """Test 5: POST /api/auth/session with empty session_id should return 400"""
    log_test("POST /api/auth/session (empty session_id) - Should return 400")
    try:
        payload = {"session_id": ""}
        resp = requests.post(f"{API_BASE}/auth/session", json=payload, timeout=10)
        log_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 400:
            log_fail(f"Expected 400, got {resp.status_code}")
            log_info(f"Response: {resp.text}")
            return False
        
        data = resp.json()
        log_info(f"Response: {json.dumps(data)}")
        log_pass("Correctly returned 400 for empty session_id")
        return True
    except Exception as e:
        log_fail(f"Exception: {e}")
        return False

def test_auth_session_invalid_session_id():
    """Test 6: POST /api/auth/session with invalid session_id should return 401 or 502"""
    log_test("POST /api/auth/session (invalid session_id) - Should return 401 or 502")
    try:
        payload = {"session_id": "totally-invalid-xyz"}
        resp = requests.post(f"{API_BASE}/auth/session", json=payload, timeout=20)
        log_info(f"Status: {resp.status_code}")
        log_info(f"Response: {resp.text}")
        
        if resp.status_code == 200:
            log_fail("Should NOT return 200 for invalid session_id")
            return False
        
        if resp.status_code == 500:
            log_fail("Should NOT return 500 (unhandled error)")
            return False
        
        if resp.status_code == 401:
            log_pass("Returned 401 (invalid/expired session)")
            return True
        
        if resp.status_code == 502:
            log_pass("Returned 502 (auth provider unreachable)")
            return True
        
        log_fail(f"Unexpected status code: {resp.status_code}")
        return False
    except Exception as e:
        log_fail(f"Exception: {e}")
        return False

def test_auth_logout_no_header():
    """Test 7: POST /api/auth/logout without Authorization should return 200 {"ok": true}"""
    log_test("POST /api/auth/logout (no Authorization) - Should return 200")
    try:
        resp = requests.post(f"{API_BASE}/auth/logout", timeout=10)
        log_info(f"Status: {resp.status_code}")
        
        if resp.status_code != 200:
            log_fail(f"Expected 200, got {resp.status_code}")
            log_info(f"Response: {resp.text}")
            return False
        
        data = resp.json()
        log_info(f"Response: {json.dumps(data)}")
        
        if data.get("ok") != True:
            log_fail(f"Expected ok=true, got {data}")
            return False
        
        log_pass("Correctly returned 200 with ok=true")
        return True
    except Exception as e:
        log_fail(f"Exception: {e}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}NASUKI Backend Auth Foundation Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}Base URL: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
    
    tests = [
        ("Root endpoint", test_root_endpoint),
        ("Status roundtrip", test_status_roundtrip),
        ("Auth /me no header", test_auth_me_no_header),
        ("Auth /me invalid token", test_auth_me_invalid_token),
        ("Auth /session empty session_id", test_auth_session_empty_session_id),
        ("Auth /session invalid session_id", test_auth_session_invalid_session_id),
        ("Auth /logout no header", test_auth_logout_no_header),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n{Colors.RED}FATAL ERROR in {name}: {e}{Colors.RESET}")
            results.append((name, False))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status} - {name}")
    
    print(f"\n{Colors.BLUE}Total: {passed_count}/{total_count} tests passed{Colors.RESET}")
    
    if passed_count == total_count:
        print(f"{Colors.GREEN}✓ All tests passed!{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}✗ Some tests failed{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
