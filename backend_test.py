#!/usr/bin/env python3
"""
BLOCK E Testing Suite - Telegram Admin Alerts + Cron Hardening
Tests all hardened endpoints and services functionality
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List


class BlockEAPITester:
    def __init__(self, base_url="https://fractal-modules.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {endpoint}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"   Status: {response.status_code} (expected {expected_status})")
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text[:500] if response.text else ""}

            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - {name}")
                if isinstance(response_data, dict):
                    # Print interesting response fields
                    for key in ['ok', 'status', 'stats', 'success', 'result']:
                        if key in response_data:
                            print(f"   {key}: {response_data[key]}")
            else:
                print(f"❌ FAILED - {name}")
                print(f"   Expected status {expected_status}, got {response.status_code}")
                print(f"   Response: {json.dumps(response_data, indent=2)[:300]}")
                self.failures.append({
                    'name': name,
                    'expected_status': expected_status,
                    'actual_status': response.status_code,
                    'response': response_data
                })

            return success, response_data

        except Exception as e:
            print(f"❌ FAILED - {name} - Error: {str(e)}")
            self.failures.append({
                'name': name,
                'error': str(e)
            })
            return False, {}

    def test_telegram_health(self) -> bool:
        """Test GET /api/fractal/v2.1/admin/telegram/health"""
        success, response = self.run_test(
            "Telegram Health Check",
            "GET",
            "/api/fractal/v2.1/admin/telegram/health",
            200
        )
        
        if success:
            # Check expected response structure
            expected_fields = ['ok', 'status']
            missing = [f for f in expected_fields if f not in response]
            if missing:
                print(f"   ⚠️  Missing fields: {missing}")
            
            # Check if status is valid
            if response.get('status') in ['HEALTHY', 'DEGRADED', 'UNHEALTHY', 'NOT_CONFIGURED', 'NOT_INITIALIZED']:
                print(f"   ✅ Valid status: {response.get('status')}")
            else:
                print(f"   ⚠️  Unknown status: {response.get('status')}")
        
        return success

    def test_telegram_stats(self) -> bool:
        """Test GET /api/fractal/v2.1/admin/telegram/stats"""
        success, response = self.run_test(
            "Telegram Stats",
            "GET",
            "/api/fractal/v2.1/admin/telegram/stats",
            200
        )
        
        if success:
            # Check stats structure
            if 'stats' in response:
                stats = response['stats']
                expected_stats = ['sentLast5Min', 'sentLastHour', 'failuresLastHour', 'rateLimitedLastHour']
                missing = [s for s in expected_stats if s not in stats]
                if missing:
                    print(f"   ⚠️  Missing stats: {missing}")
                else:
                    print(f"   ✅ All expected stats present")
            
            if 'auditLog' in response:
                print(f"   ✅ Audit log present ({len(response['auditLog'])} entries)")
        
        return success

    def test_telegram_test_hardened(self) -> bool:
        """Test POST /api/fractal/v2.1/admin/telegram/test-hardened"""
        success, response = self.run_test(
            "Telegram Test Hardened",
            "POST",
            "/api/fractal/v2.1/admin/telegram/test-hardened",
            200,
            data={}  # Empty object instead of None
        )
        
        if success:
            if response.get('success'):
                print(f"   ✅ Test message sent successfully")
                
                # Check result structure
                if 'result' in response:
                    result = response['result']
                    result_fields = ['ok', 'status', 'retries', 'rateLimited', 'deduplicated', 'timestamp']
                    present = [f for f in result_fields if f in result]
                    print(f"   ✅ Result fields present: {present}")
            else:
                print(f"   ⚠️  Test message failed: {response}")
        
        return success

    def test_cron_status(self) -> bool:
        """Test GET /api/fractal/v2.1/admin/cron/status"""
        success, response = self.run_test(
            "Cron Status",
            "GET",
            "/api/fractal/v2.1/admin/cron/status",
            200
        )
        
        if success:
            # Check response structure
            if response.get('ok') is True:
                print(f"   ✅ Cron service OK")
            
            if 'stats' in response:
                stats = response['stats']
                expected_stats = ['activeLocksCount', 'executionsLast24h', 'failuresLast24h', 'timeoutsLast24h']
                present = [s for s in expected_stats if s in stats]
                print(f"   ✅ Stats fields present: {present}")
            
            if 'locks' in response:
                print(f"   ✅ Lock status present")
        
        return success

    def test_cron_history(self) -> bool:
        """Test GET /api/fractal/v2.1/admin/cron/history"""
        success, response = self.run_test(
            "Cron History",
            "GET",
            "/api/fractal/v2.1/admin/cron/history",
            200
        )
        
        if success:
            if 'history' in response:
                history = response['history']
                print(f"   ✅ History present ({len(history)} entries)")
                
                # Check history entry structure if present
                if history:
                    first_entry = history[0]
                    expected_fields = ['jobName', 'executionId', 'status', 'startedAt']
                    present = [f for f in expected_fields if f in first_entry]
                    print(f"   ✅ History entry fields: {present}")
        
        return success

    def test_cron_history_with_params(self) -> bool:
        """Test GET /api/fractal/v2.1/admin/cron/history with query parameters"""
        success, response = self.run_test(
            "Cron History (with params)",
            "GET",
            "/api/fractal/v2.1/admin/cron/history?job=fractal-daily&limit=10",
            200
        )
        return success

    def test_daily_job_hardened_no_auth(self) -> bool:
        """Test POST /api/fractal/v2.1/admin/jobs/daily-run-hardened without auth (should fail)"""
        success, response = self.run_test(
            "Daily Job Hardened (No Auth)",
            "POST",
            "/api/fractal/v2.1/admin/jobs/daily-run-hardened",
            401,  # Expecting 401 Unauthorized
            data={"symbol": "BTC"}
        )
        return success

    def test_daily_job_hardened_with_auth(self) -> bool:
        """Test POST /api/fractal/v2.1/admin/jobs/daily-run-hardened with auth"""
        # Use the FRACTAL_CRON_SECRET from .env with Bearer token
        headers = {
            'Authorization': 'Bearer fractal_production_cron_secret_2024'
        }
        
        success, response = self.run_test(
            "Daily Job Hardened (With Auth)",
            "POST",
            "/api/fractal/v2.1/admin/jobs/daily-run-hardened",
            200,
            data={"symbol": "BTC"},
            headers=headers
        )
        
        if success:
            # Check response structure
            expected_fields = ['success', 'jobId']
            present = [f for f in expected_fields if f in response]
            print(f"   ✅ Response fields present: {present}")
            
            if response.get('success'):
                print(f"   ✅ Job executed successfully")
            elif response.get('skipped'):
                print(f"   ✅ Job skipped (reason: {response.get('skipReason')})")
        
        return success

    def test_notify_startup(self) -> bool:
        """Test POST /api/fractal/v2.1/admin/notify/startup"""
        success, response = self.run_test(
            "Notify Startup",
            "POST",
            "/api/fractal/v2.1/admin/notify/startup",
            200,
            data={}  # Empty object instead of None
        )
        
        if success:
            if response.get('success'):
                print(f"   ✅ Startup notification sent")
        
        return success

    def run_comprehensive_tests(self) -> int:
        """Run all BLOCK E tests"""
        print("=" * 60)
        print("🧪 BLOCK E - Telegram Admin Alerts + Cron Hardening Tests")
        print("=" * 60)
        
        # Test all endpoints
        test_methods = [
            self.test_telegram_health,
            self.test_telegram_stats,
            self.test_telegram_test_hardened,
            self.test_cron_status,
            self.test_cron_history,
            self.test_cron_history_with_params,
            self.test_daily_job_hardened_no_auth,
            self.test_daily_job_hardened_with_auth,
            self.test_notify_startup,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} crashed: {e}")
                self.failures.append({
                    'name': test_method.__name__,
                    'error': f"Test method crashed: {e}"
                })
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 BLOCK E TEST SUMMARY")
        print("=" * 60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {len(self.failures)}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.failures:
            print("\n❌ FAILURES:")
            for i, failure in enumerate(self.failures, 1):
                print(f"{i}. {failure['name']}")
                if 'error' in failure:
                    print(f"   Error: {failure['error']}")
                else:
                    print(f"   Expected: {failure.get('expected_status')}, Got: {failure.get('actual_status')}")
        
        return 0 if self.tests_passed == self.tests_run else 1


def main():
    """Main test runner"""
    print("🚀 Starting BLOCK E API Tests...")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Create tester
    tester = BlockEAPITester()
    
    # Run comprehensive tests
    exit_code = tester.run_comprehensive_tests()
    
    print(f"\n🏁 Testing completed with exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())