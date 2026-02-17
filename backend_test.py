#!/usr/bin/env python3
"""
BLOCK 58/59 - Hierarchical Resolver Backend API Tests

Test coverage:
- Multi-signal extended endpoint (all horizons + resolver)
- Regime panel endpoint (horizons + resolved bias)  
- Health check endpoint
- Error handling and validation
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class FractalAPITester:
    def __init__(self, base_url="https://multi-layer-decision.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.session.timeout = 30

    def log(self, msg: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {msg}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 params: Dict = None, validate_fn = None) -> tuple[bool, Any]:
        """Run a single API test with validation"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.tests_run += 1
        self.log(f"Testing {name}...")
        self.log(f"URL: {method} {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params or {})
            else:
                response = self.session.request(method, url, params=params or {})

            success = response.status_code == expected_status
            response_data = {}
            
            if success:
                try:
                    response_data = response.json()
                    self.log(f"✅ Status: {response.status_code}")
                    
                    # Run custom validation if provided
                    if validate_fn:
                        validation_result = validate_fn(response_data)
                        if validation_result is True:
                            self.log("✅ Validation passed")
                        else:
                            self.log(f"❌ Validation failed: {validation_result}")
                            success = False
                            
                except json.JSONDecodeError as e:
                    self.log(f"❌ Invalid JSON response: {e}")
                    success = False
                    
            else:
                self.log(f"❌ Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"Error response: {json.dumps(error_data, indent=2)}")
                except:
                    self.log(f"Response text: {response.text[:500]}")

            if success:
                self.tests_passed += 1
                
            return success, response_data

        except Exception as e:
            self.log(f"❌ Request failed: {str(e)}", "ERROR")
            return False, {}

    def validate_multi_signal_response(self, data: Dict) -> bool | str:
        """Validate multi-signal endpoint response structure"""
        required_fields = ['symbol', 'set', 'asof', 'signalsByHorizon', 'resolved', 'meta']
        
        # Check top-level fields
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"
        
        # Validate signalsByHorizon
        horizons = data.get('signalsByHorizon', {})
        expected_horizons = ['7d', '14d', '30d', '90d', '180d', '365d']
        
        for horizon in expected_horizons:
            if horizon not in horizons:
                return f"Missing horizon: {horizon}"
            
            signal = horizons[horizon]
            signal_fields = ['action', 'expectedReturn', 'confidence', 'reliability', 
                           'effectiveN', 'entropy', 'sizeMultiplier', 'phase', 'tailRisk', 'blockers']
            
            for field in signal_fields:
                if field not in signal:
                    return f"Missing field {field} in horizon {horizon}"
            
            # Validate action enum
            if signal['action'] not in ['LONG', 'SHORT', 'HOLD']:
                return f"Invalid action in {horizon}: {signal['action']}"
                
            # Validate numeric ranges
            if not (0 <= signal['confidence'] <= 1):
                return f"Invalid confidence range in {horizon}: {signal['confidence']}"
                
            if not (0 <= signal['reliability'] <= 1):
                return f"Invalid reliability range in {horizon}: {signal['reliability']}"
        
        # Validate resolved section
        resolved = data.get('resolved', {})
        if not all(key in resolved for key in ['bias', 'timing', 'final']):
            return "Missing resolved sections (bias, timing, final)"
        
        # Validate bias resolution
        bias = resolved['bias']
        if bias.get('dir') not in ['BULL', 'BEAR', 'NEUTRAL']:
            return f"Invalid bias direction: {bias.get('dir')}"
        
        # Validate timing resolution
        timing = resolved['timing']
        if timing.get('action') not in ['ENTER', 'WAIT', 'EXIT']:
            return f"Invalid timing action: {timing.get('action')}"
        
        # Validate final resolution
        final = resolved['final']
        if final.get('action') not in ['BUY', 'SELL', 'HOLD']:
            return f"Invalid final action: {final.get('action')}"
            
        if final.get('mode') not in ['TREND_FOLLOW', 'COUNTER_TREND', 'HOLD']:
            return f"Invalid final mode: {final.get('mode')}"
        
        return True

    def validate_regime_response(self, data: Dict) -> bool | str:
        """Validate regime endpoint response structure"""
        required_fields = ['symbol', 'tf', 'asof', 'horizons', 'resolvedBias']
        
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"
        
        # Validate horizons array
        horizons = data.get('horizons', [])
        if not isinstance(horizons, list) or len(horizons) == 0:
            return "Horizons should be a non-empty array"
        
        for horizon in horizons:
            horizon_fields = ['key', 'label', 'action', 'expectedReturn', 'confidence', 
                            'reliability', 'phase', 'entropy', 'tailP95DD']
            
            for field in horizon_fields:
                if field not in horizon:
                    return f"Missing field {field} in horizon data"
            
            if horizon['action'] not in ['BULL', 'BEAR', 'NEUTRAL']:
                return f"Invalid action in horizon: {horizon['action']}"
        
        # Validate resolvedBias
        bias = data.get('resolvedBias', {})
        if bias.get('bias') not in ['BULL', 'BEAR', 'NEUTRAL']:
            return f"Invalid resolved bias: {bias.get('bias')}"
        
        if 'strength' not in bias or not (0 <= bias['strength'] <= 1):
            return f"Invalid bias strength: {bias.get('strength')}"
        
        return True

    def test_health_check(self):
        """Test basic health endpoint"""
        return self.run_test(
            "Health Check",
            "GET", 
            "/api/health",
            200
        )

    def test_multi_signal_basic(self):
        """Test multi-signal endpoint with BTC and extended set"""
        return self.run_test(
            "Multi-Signal Extended (BTC)",
            "GET",
            "/api/fractal/v2.1/multi-signal",
            200,
            params={"symbol": "BTC", "set": "extended"},
            validate_fn=self.validate_multi_signal_response
        )

    def test_multi_signal_validation(self):
        """Test multi-signal endpoint validation"""
        tests = [
            # Non-BTC symbol should fail
            ("Non-BTC Symbol", {"symbol": "ETH", "set": "extended"}, 400),
            # Invalid set should fail
            ("Invalid Set", {"symbol": "BTC", "set": "basic"}, 400),
            # Missing params should use defaults
            ("Default Params", {}, 200),
        ]
        
        results = []
        for test_name, params, expected_status in tests:
            success, _ = self.run_test(
                f"Multi-Signal {test_name}",
                "GET",
                "/api/fractal/v2.1/multi-signal", 
                expected_status,
                params=params
            )
            results.append(success)
        
        return all(results)

    def test_regime_basic(self):
        """Test regime endpoint with BTC"""
        return self.run_test(
            "Regime Panel (BTC)",
            "GET",
            "/api/fractal/v2.1/regime",
            200,
            params={"symbol": "BTC"},
            validate_fn=self.validate_regime_response
        )

    def test_regime_validation(self):
        """Test regime endpoint validation"""
        tests = [
            # Non-BTC should fail
            ("Non-BTC Symbol", {"symbol": "ETH"}, 400),
            # Default should work
            ("Default Params", {}, 200),
        ]
        
        results = []
        for test_name, params, expected_status in tests:
            success, _ = self.run_test(
                f"Regime {test_name}",
                "GET",
                "/api/fractal/v2.1/regime",
                expected_status,
                params=params
            )
            results.append(success)
        
        return all(results)

    def test_hierarchical_resolver_integration(self):
        """Test that resolver produces consistent results across endpoints"""
        self.log("Testing hierarchical resolver integration...")
        
        # Get multi-signal data
        success1, multi_data = self.run_test(
            "Multi-Signal for Integration Test",
            "GET",
            "/api/fractal/v2.1/multi-signal",
            200,
            params={"symbol": "BTC", "set": "extended"}
        )
        
        # Get regime data  
        success2, regime_data = self.run_test(
            "Regime for Integration Test",
            "GET",
            "/api/fractal/v2.1/regime",
            200,
            params={"symbol": "BTC"}
        )
        
        if not (success1 and success2):
            self.log("❌ Could not fetch data for integration test")
            return False
        
        # Compare resolved bias consistency
        multi_bias = multi_data.get('resolved', {}).get('bias', {}).get('dir')
        regime_bias = regime_data.get('resolvedBias', {}).get('bias')
        
        if multi_bias and regime_bias:
            if multi_bias == regime_bias:
                self.log("✅ Bias consistency check passed")
                return True
            else:
                self.log(f"❌ Bias inconsistency: multi-signal={multi_bias}, regime={regime_bias}")
                return False
        else:
            self.log("❌ Could not extract bias data for comparison")
            return False

    def test_response_times(self):
        """Test endpoint response times"""
        import time
        
        endpoints = [
            ("/api/health", {}),
            ("/api/fractal/v2.1/multi-signal", {"symbol": "BTC", "set": "extended"}),
            ("/api/fractal/v2.1/regime", {"symbol": "BTC"})
        ]
        
        for endpoint, params in endpoints:
            start_time = time.time()
            success, _ = self.run_test(
                f"Response Time - {endpoint}",
                "GET",
                endpoint,
                200,
                params=params
            )
            end_time = time.time()
            
            if success:
                response_time = end_time - start_time
                self.log(f"Response time: {response_time:.2f}s")
                if response_time > 10:
                    self.log(f"⚠️  Slow response time: {response_time:.2f}s")
                else:
                    self.log(f"✅ Good response time: {response_time:.2f}s")

    def run_all_tests(self):
        """Run complete test suite"""
        self.log("=" * 60)
        self.log("FRACTAL HIERARCHICAL RESOLVER - Backend API Tests")
        self.log("=" * 60)
        
        test_methods = [
            self.test_health_check,
            self.test_multi_signal_basic,
            self.test_multi_signal_validation,
            self.test_regime_basic, 
            self.test_regime_validation,
            self.test_hierarchical_resolver_integration,
            self.test_response_times,
        ]
        
        for test_method in test_methods:
            try:
                result = test_method()
                self.log("-" * 40)
            except Exception as e:
                self.log(f"❌ Test method {test_method.__name__} failed: {e}", "ERROR")
                self.log("-" * 40)
        
        # Final summary
        self.log("=" * 60)
        self.log(f"TEST SUMMARY")
        self.log(f"Tests run: {self.tests_run}")
        self.log(f"Tests passed: {self.tests_passed}")
        self.log(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        self.log("=" * 60)
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = FractalAPITester()
    
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())