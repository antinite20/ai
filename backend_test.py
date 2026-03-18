#!/usr/bin/env python3
"""
Backend API Testing for House Socioeconomic Analyzer
Tests all FastAPI endpoints using the public URL
"""

import requests
import sys
import base64
from datetime import datetime
import json

class HouseAnalyzerAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_image_path = "/tmp/test_house.png"

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details:
            print(f"   Details: {details}")
        print()

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                expected_message = "House Socioeconomic Analyzer API is running!"
                success = data.get("message") == expected_message
                details = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Root Endpoint (/api/)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Root Endpoint (/api/)", False, str(e))
            return False

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                has_status = "status" in data
                has_api_key = "api_key_configured" in data
                api_key_configured = data.get("api_key_configured", False)
                
                success = has_status and has_api_key and api_key_configured
                details = f"Status: {data.get('status')}, API Key Configured: {api_key_configured}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Health Check (/api/health)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Health Check (/api/health)", False, str(e))
            return False

    def test_analyze_endpoint_no_file(self):
        """Test analyze endpoint without file (should fail)"""
        try:
            response = requests.post(f"{self.api_url}/analyze", timeout=10)
            # Should return 422 for missing file
            success = response.status_code == 422
            details = f"Status: {response.status_code} (Expected 422 for missing file)"
            
            self.log_test("Analyze Endpoint - No File", success, details)
            return success
            
        except Exception as e:
            self.log_test("Analyze Endpoint - No File", False, str(e))
            return False

    def test_analyze_endpoint_with_image(self):
        """Test analyze endpoint with actual image"""
        try:
            # Read the test image
            with open(self.test_image_path, 'rb') as f:
                image_data = f.read()
            
            # Prepare multipart form data
            files = {
                'file': ('test_house.png', image_data, 'image/png')
            }
            data = {
                'context': 'Test house image for socioeconomic analysis'
            }
            
            print(f"📤 Uploading image ({len(image_data)} bytes) for analysis...")
            response = requests.post(
                f"{self.api_url}/analyze", 
                files=files, 
                data=data,
                timeout=60  # Longer timeout for AI analysis
            )
            
            success = response.status_code == 200
            
            if success:
                result = response.json()
                has_success = "success" in result
                has_filename = "filename" in result
                has_result = "result" in result
                
                analysis_success = result.get("success", False)
                filename = result.get("filename", "")
                analysis_result = result.get("result", "")
                
                # Check if we got a valid analysis result
                valid_analysis = (
                    analysis_success and 
                    filename == "test_house.png" and 
                    len(analysis_result) > 50  # Should have substantial content
                )
                
                success = has_success and has_filename and has_result and valid_analysis
                
                details = f"Analysis Success: {analysis_success}, Filename: {filename}, Result Length: {len(analysis_result)}"
                
                if valid_analysis:
                    # Try to extract classification info
                    classification_found = any(term in analysis_result.lower() for term in 
                                             ['low income', 'middle', 'high income', 'desil'])
                    details += f", Classification Found: {classification_found}"
                    
                    # Print first 200 chars of result for verification
                    print(f"   Analysis Preview: {analysis_result[:200]}...")
                
            else:
                details = f"Status: {response.status_code}"
                if response.text:
                    details += f", Response: {response.text[:200]}"
                
            self.log_test("Analyze Endpoint - With Image", success, details)
            return success
            
        except Exception as e:
            self.log_test("Analyze Endpoint - With Image", False, str(e))
            return False

    def test_analyze_endpoint_invalid_file(self):
        """Test analyze endpoint with invalid file type"""
        try:
            # Create a fake text file
            fake_file_data = b"This is not an image file"
            
            files = {
                'file': ('test.txt', fake_file_data, 'text/plain')
            }
            
            response = requests.post(
                f"{self.api_url}/analyze", 
                files=files,
                timeout=10
            )
            
            # Should return 400 for invalid file type
            success = response.status_code == 400
            details = f"Status: {response.status_code} (Expected 400 for invalid file type)"
            
            if response.status_code == 200:
                # Check if error is in response body
                result = response.json()
                if not result.get("success", True):
                    success = True
                    details += f", Error in response: {result.get('error', 'N/A')}"
            
            self.log_test("Analyze Endpoint - Invalid File", success, details)
            return success
            
        except Exception as e:
            self.log_test("Analyze Endpoint - Invalid File", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🏠 House Socioeconomic Analyzer - Backend API Testing")
        print("=" * 60)
        print(f"Testing API at: {self.api_url}")
        print(f"Test Image: {self.test_image_path}")
        print()
        
        # Test basic endpoints first
        root_ok = self.test_root_endpoint()
        health_ok = self.test_health_endpoint()
        
        # Test analyze endpoint variations
        no_file_ok = self.test_analyze_endpoint_no_file()
        invalid_file_ok = self.test_analyze_endpoint_invalid_file()
        
        # Test with actual image (most important test)
        image_analysis_ok = self.test_analyze_endpoint_with_image()
        
        # Summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All backend tests PASSED!")
            return True
        else:
            print("⚠️  Some backend tests FAILED!")
            
            # Identify critical failures
            critical_failures = []
            if not root_ok:
                critical_failures.append("Root endpoint not accessible")
            if not health_ok:
                critical_failures.append("Health check failed or API key not configured")
            if not image_analysis_ok:
                critical_failures.append("Image analysis not working")
                
            if critical_failures:
                print("🚨 Critical Issues:")
                for issue in critical_failures:
                    print(f"   - {issue}")
                    
            return False

def main():
    """Main test execution"""
    tester = HouseAnalyzerAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())