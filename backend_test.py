#!/usr/bin/env python3
"""
Backend API Testing for Fractal Module
Tests TypeScript Fastify backend (port 8002) proxied through FastAPI (port 8001)
"""

import requests
import sys
import json
from datetime import datetime

class FractalAPITester:
    def __init__(self, base_url="https://mongo-admin-dev.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def log_result(self, test_name, success, details=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details and not success:
            print(f"    Details: {details}")

    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') is True:
                    self.log_result("Health endpoint", True, {
                        "status_code": response.status_code,
                        "response": data
                    })
                    return True
                else:
                    self.log_result("Health endpoint", False, {
                        "status_code": response.status_code,
                        "error": "Response ok field is not True",
                        "response": data
                    })
            else:
                self.log_result("Health endpoint", False, {
                    "status_code": response.status_code,
                    "error": f"Expected 200, got {response.status_code}"
                })
        except Exception as e:
            self.log_result("Health endpoint", False, {
                "error": str(e)
            })
        return False

    def test_fractal_signal_endpoint(self):
        """Test /api/fractal/v2.1/signal?symbol=BTC endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/fractal/v2.1/signal?symbol=BTC", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Check if response has expected structure (signalsByHorizon, assembled, etc.)
                expected_keys = ['signalsByHorizon', 'assembled', 'meta', 'risk', 'reliability']
                has_expected_structure = any(key in data for key in expected_keys)
                
                if isinstance(data, dict) and has_expected_structure:
                    self.log_result("Fractal signal endpoint", True, {
                        "status_code": response.status_code,
                        "has_signals": 'signalsByHorizon' in data,
                        "has_assembled": 'assembled' in data,
                        "response_keys": list(data.keys())
                    })
                    return True
                else:
                    self.log_result("Fractal signal endpoint", False, {
                        "status_code": response.status_code,
                        "error": "Response missing expected signal structure",
                        "response_keys": list(data.keys()) if isinstance(data, dict) else "Not a dict"
                    })
            else:
                self.log_result("Fractal signal endpoint", False, {
                    "status_code": response.status_code,
                    "error": f"Expected 200, got {response.status_code}",
                    "response_text": response.text[:200]
                })
        except Exception as e:
            self.log_result("Fractal signal endpoint", False, {
                "error": str(e)
            })
        return False

    def test_shadow_divergence_endpoint(self):
        """Test /api/fractal/v2.1/admin/shadow-divergence?symbol=BTC endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/fractal/v2.1/admin/shadow-divergence?symbol=BTC", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Check if response has expected shadow divergence structure
                expected_keys = ['meta', 'recommendation', 'equity', 'summary', 'calibration', 'divergenceLedger']
                has_expected_structure = any(key in data for key in expected_keys)
                
                if has_expected_structure:
                    self.log_result("Shadow divergence endpoint", True, {
                        "status_code": response.status_code,
                        "response_keys": list(data.keys()),
                        "has_meta": 'meta' in data,
                        "has_recommendation": 'recommendation' in data
                    })
                    return True
                else:
                    self.log_result("Shadow divergence endpoint", False, {
                        "status_code": response.status_code,
                        "error": "Response missing expected shadow divergence structure",
                        "response_keys": list(data.keys()) if isinstance(data, dict) else "Not a dict"
                    })
            else:
                self.log_result("Shadow divergence endpoint", False, {
                    "status_code": response.status_code,
                    "error": f"Expected 200, got {response.status_code}",
                    "response_text": response.text[:200]
                })
        except Exception as e:
            self.log_result("Shadow divergence endpoint", False, {
                "error": str(e)
            })
        return False

    def test_fractal_health_endpoint(self):
        """Test /api/fractal/health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/fractal/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Fractal health endpoint", True, {
                    "status_code": response.status_code,
                    "response": data
                })
                return True
            else:
                self.log_result("Fractal health endpoint", False, {
                    "status_code": response.status_code,
                    "error": f"Expected 200, got {response.status_code}",
                    "response_text": response.text[:200]
                })
        except Exception as e:
            self.log_result("Fractal health endpoint", False, {
                "error": str(e)
            })
        return False

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🔍 Starting Fractal Backend API Tests...")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test all endpoints
        self.test_health_endpoint()
        self.test_fractal_health_endpoint()
        self.test_fractal_signal_endpoint()
        self.test_shadow_divergence_endpoint()
        
        print("=" * 60)
        print(f"📊 Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All backend tests passed!")
            return True
        else:
            print("⚠️  Some backend tests failed")
            return False

    def get_summary(self):
        """Get test summary"""
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0,
            "results": self.results
        }

def main():
    """Main test execution"""
    tester = FractalAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    summary = tester.get_summary()
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())