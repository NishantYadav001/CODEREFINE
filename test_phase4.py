#!/usr/bin/env python3
"""
Phase 4: Comprehensive End-to-End Testing
Full stack validation of routing system across all user types
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Phase4Tester:
    def __init__(self):
        self.results = []
        self.admin_token = None
        self.user_token = None
        
    def log_test(self, section, test_name, status, details=""):
        """Log test result"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "timestamp": timestamp,
            "section": section,
            "test": test_name,
            "status": status,
            "details": details
        }
        self.results.append(result)
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} [{section}] {test_name}: {status} {details}")
        
    def section_1_guest_routes(self):
        """Section 1: Guest User Has Limited Routes"""
        print("\n" + "="*60)
        print("[SECTION 1] GUEST USER ROUTES TEST")
        print("="*60)
        
        try:
            resp = requests.get(f"{BASE_URL}/api/routes/config")
            data = resp.json()
            
            # Test 1.1: Guest role
            if data['data']['role'] == 'guest':
                self.log_test("Section 1", "Guest role detected", "PASS")
            else:
                self.log_test("Section 1", "Guest role detected", "FAIL", f"Got {data['data']['role']}")
                
            # Test 1.2: 4 routes for guest
            routes_count = len(data['data']['routes'])
            if routes_count == 4:
                self.log_test("Section 1", "Guest has 4 routes", "PASS")
            else:
                self.log_test("Section 1", "Guest has 4 routes", "FAIL", f"Got {routes_count}")
                
            # Test 1.3: Route names
            routes = list(data['data']['routes'].keys())
            expected = ['landing', 'login', 'signup', 'help']
            if set(routes) == set(expected):
                self.log_test("Section 1", "Correct route names", "PASS", f"{', '.join(routes)}")
            else:
                self.log_test("Section 1", "Correct route names", "FAIL", f"Got {routes}")
                
            # Test 1.4: Daily limit
            daily_limit = data['data']['permissions']['daily_requests']
            if daily_limit == 5:
                self.log_test("Section 1", "Guest daily limit 5", "PASS")
            else:
                self.log_test("Section 1", "Guest daily limit 5", "FAIL", f"Got {daily_limit}")
                
        except Exception as e:
            self.log_test("Section 1", "Guest routes test", "FAIL", str(e))
            
    def section_2_login_flow(self):
        """Section 2: User Login"""
        print("\n" + "="*60)
        print("[SECTION 2] LOGIN FLOW TEST")
        print("="*60)
        
        try:
            # Test 2.1: Admin login
            login_data = {"username": "admin", "password": "admin123"}  # From .env ADMIN_PASSWORD
            resp = requests.post(f"{BASE_URL}/api/login", json=login_data)
            
            if resp.status_code == 200:
                self.log_test("Section 2", "Admin login succeeds", "PASS")
                data = resp.json()
                self.admin_token = data.get('token')
                
                # Test 2.2: Token generated
                if self.admin_token:
                    self.log_test("Section 2", "JWT token generated", "PASS")
                else:
                    self.log_test("Section 2", "JWT token generated", "FAIL", "No token in response")
                    
                # Test 2.3: Role is admin
                if data.get('role') == 'admin':
                    self.log_test("Section 2", "Admin role assigned", "PASS")
                else:
                    self.log_test("Section 2", "Admin role assigned", "FAIL", f"Got {data.get('role')}")
                    
                # Test 2.4: Username stored
                if data.get('username') == 'admin':
                    self.log_test("Section 2", "Username in response", "PASS")
                else:
                    self.log_test("Section 2", "Username in response", "FAIL")
            else:
                self.log_test("Section 2", "Admin login succeeds", "FAIL", f"Status {resp.status_code}")
                
        except Exception as e:
            self.log_test("Section 2", "Login flow test", "FAIL", str(e))
            
    def section_3_admin_routes(self):
        """Section 3: Admin Has All Routes"""
        print("\n" + "="*60)
        print("[SECTION 3] ADMIN ROUTES TEST")
        print("="*60)
        
        if not self.admin_token:
            self.log_test("Section 3", "Admin routes check", "FAIL", "No admin token")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            resp = requests.get(f"{BASE_URL}/api/routes/config", headers=headers)
            data = resp.json()
            
            # Test 3.1: Admin role
            if data['data']['role'] == 'admin':
                self.log_test("Section 3", "Admin role verified", "PASS")
            else:
                self.log_test("Section 3", "Admin role verified", "FAIL", f"Got {data['data']['role']}")
                
            # Test 3.2: All routes available
            routes_count = len(data['data']['routes'])
            if routes_count > 8:  # Admin should have more routes than user
                self.log_test("Section 3", "Admin has 8+ routes", "PASS", f"{routes_count} routes")
            else:
                self.log_test("Section 3", "Admin has 8+ routes", "FAIL", f"Got {routes_count}")
                
            # Test 3.3: Can access all route types
            routes = list(data['data']['routes'].keys())
            has_auth = any('profile' in r for r in routes)
            has_admin = any('admin' in r for r in routes)
            
            if has_auth and has_admin:
                self.log_test("Section 3", "Admin routes include user & admin", "PASS")
            else:
                self.log_test("Section 3", "Admin routes include user & admin", "FAIL")
                
        except Exception as e:
            self.log_test("Section 3", "Admin routes test", "FAIL", str(e))
            
    def section_4_route_access_check(self):
        """Section 4: Route Access Validation"""
        print("\n" + "="*60)
        print("[SECTION 4] ROUTE ACCESS CHECK TEST")
        print("="*60)
        
        try:
            # Test 4.1: Guest cannot access dashboard
            resp = requests.post(f"{BASE_URL}/api/routes/check", json={"route": "dashboard"})
            data = resp.json()
            
            if not data['can_access']:
                self.log_test("Section 4", "Guest cannot access dashboard", "PASS")
            else:
                self.log_test("Section 4", "Guest cannot access dashboard", "FAIL", "Access granted to guest")
                
            # Test 4.2: Guest cannot access admin
            resp = requests.post(f"{BASE_URL}/api/routes/check", json={"route": "admin"})
            data = resp.json()
            
            if not data['can_access']:
                self.log_test("Section 4", "Guest cannot access admin", "PASS")
            else:
                self.log_test("Section 4", "Guest cannot access admin", "FAIL", "Access granted to guest")
                
            # Test 4.3: Guest can access login
            resp = requests.post(f"{BASE_URL}/api/routes/check", json={"route": "login"})
            data = resp.json()
            
            if data['can_access']:
                self.log_test("Section 4", "Guest can access login", "PASS")
            else:
                self.log_test("Section 4", "Guest can access login", "FAIL", "Access denied to guest")
                
            # Test 4.4: Admin can access protected routes
            if self.admin_token:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                resp = requests.post(f"{BASE_URL}/api/routes/check", 
                                   json={"route": "dashboard"}, 
                                   headers=headers)
                data = resp.json()
                
                if data['can_access']:
                    self.log_test("Section 4", "Admin can access dashboard", "PASS")
                else:
                    self.log_test("Section 4", "Admin can access dashboard", "FAIL")
                    
        except Exception as e:
            self.log_test("Section 4", "Route access check test", "FAIL", str(e))
            
    def section_5_navigation_menus(self):
        """Section 5: Navigation Menu Structure"""
        print("\n" + "="*60)
        print("[SECTION 5] NAVIGATION MENUS TEST")
        print("="*60)
        
        try:
            # Test 5.1: Guest navigation
            resp = requests.get(f"{BASE_URL}/api/routes/navigation")
            data = resp.json()
            
            nav_items = len(data['navigation'])
            if nav_items == 4:  # Home, Login, Signup, Help
                self.log_test("Section 5", "Guest has 4 nav items", "PASS")
            else:
                self.log_test("Section 5", "Guest has 4 nav items", "FAIL", f"Got {nav_items}")
                
            # Test 5.2: Navigation structure
            has_names = all('name' in item for item in data['navigation'])
            has_routes = all('route' in item for item in data['navigation'])
            
            if has_names and has_routes:
                self.log_test("Section 5", "Navigation items have name & route", "PASS")
            else:
                self.log_test("Section 5", "Navigation items have name & route", "FAIL")
                
            # Test 5.3: Admin navigation
            if self.admin_token:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                resp = requests.get(f"{BASE_URL}/api/routes/navigation", headers=headers)
                data = resp.json()
                
                # Should have more items than guest
                nav_items_admin = len(data['navigation'])
                if nav_items_admin > 4:
                    self.log_test("Section 5", "Admin has more nav items than guest", "PASS", 
                                 f"Guest: 4, Admin: {nav_items_admin}")
                else:
                    self.log_test("Section 5", "Admin has more nav items than guest", "FAIL")
                    
        except Exception as e:
            self.log_test("Section 5", "Navigation menus test", "FAIL", str(e))
            
    def run_all_tests(self):
        """Execute all test sections"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║     PHASE 4: COMPREHENSIVE END-TO-END TESTING              ║")
        print("║     Full Stack Validation of Routing System                ║")
        print("╚" + "="*58 + "╝")
        
        self.section_1_guest_routes()
        self.section_2_login_flow()
        self.section_3_admin_routes()
        self.section_4_route_access_check()
        self.section_5_navigation_menus()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        total = len(self.results)
        
        print(f"✅ PASSED: {passed}/{total}")
        print(f"❌ FAILED: {failed}/{total}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed - review details above")
            
        print("\n" + "="*60)

if __name__ == "__main__":
    tester = Phase4Tester()
    tester.run_all_tests()
