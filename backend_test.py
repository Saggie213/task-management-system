import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class TaskManagementAPITester:
    def __init__(self, base_url="https://new-upload-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f", Expected: {expected_status}"
                try:
                    error_data = response.json()
                    details += f", Response: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"

            self.log_test(name, success, details)
            
            if success:
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check"""
        success, response = self.run_test(
            "API Health Check",
            "GET",
            "",
            200
        )
        return success

    def test_signup(self):
        """Test user signup"""
        test_user_data = {
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        
        success, response = self.run_test(
            "User Signup",
            "POST",
            "auth/signup",
            201,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            self.test_user_data = test_user_data
            return True
        return False

    def test_login(self):
        """Test user login"""
        if not hasattr(self, 'test_user_data'):
            self.log_test("User Login", False, "No user data available for login test")
            return False
            
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_get_current_user(self):
        """Test get current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_get_user_profile(self):
        """Test get user profile"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "user/profile",
            200
        )
        return success

    def test_update_user_profile(self):
        """Test update user profile"""
        update_data = {
            "full_name": "Updated Test User"
        }
        
        success, response = self.run_test(
            "Update User Profile",
            "PUT",
            "user/profile",
            200,
            data=update_data
        )
        return success

    def test_create_task(self):
        """Test create task"""
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "status": "pending",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        success, response = self.run_test(
            "Create Task",
            "POST",
            "tasks",
            201,
            data=task_data
        )
        
        if success and 'id' in response:
            self.test_task_id = response['id']
            return True
        return False

    def test_get_tasks(self):
        """Test get all tasks"""
        success, response = self.run_test(
            "Get All Tasks",
            "GET",
            "tasks",
            200
        )
        return success

    def test_get_tasks_with_filter(self):
        """Test get tasks with status filter"""
        success, response = self.run_test(
            "Get Tasks with Filter",
            "GET",
            "tasks?status_filter=pending",
            200
        )
        return success

    def test_get_single_task(self):
        """Test get single task"""
        if not hasattr(self, 'test_task_id'):
            self.log_test("Get Single Task", False, "No task ID available")
            return False
            
        success, response = self.run_test(
            "Get Single Task",
            "GET",
            f"tasks/{self.test_task_id}",
            200
        )
        return success

    def test_update_task(self):
        """Test update task"""
        if not hasattr(self, 'test_task_id'):
            self.log_test("Update Task", False, "No task ID available")
            return False
            
        update_data = {
            "title": "Updated Test Task",
            "status": "in-progress"
        }
        
        success, response = self.run_test(
            "Update Task",
            "PUT",
            f"tasks/{self.test_task_id}",
            200,
            data=update_data
        )
        return success

    def test_delete_task(self):
        """Test delete task"""
        if not hasattr(self, 'test_task_id'):
            self.log_test("Delete Task", False, "No task ID available")
            return False
            
        success, response = self.run_test(
            "Delete Task",
            "DELETE",
            f"tasks/{self.test_task_id}",
            200
        )
        return success

    def test_logout(self):
        """Test logout"""
        success, response = self.run_test(
            "User Logout",
            "POST",
            "auth/logout",
            200
        )
        return success

    def test_delete_user_profile(self):
        """Test delete user profile (should be last test)"""
        success, response = self.run_test(
            "Delete User Profile",
            "DELETE",
            "user/profile",
            200
        )
        return success

    def test_invalid_endpoints(self):
        """Test invalid endpoints return proper errors"""
        # Test invalid task ID
        success, response = self.run_test(
            "Invalid Task ID",
            "GET",
            "tasks/invalid-id",
            404
        )
        
        # Test unauthorized access (without token)
        old_token = self.token
        self.token = None
        success2, response2 = self.run_test(
            "Unauthorized Access",
            "GET",
            "tasks",
            401
        )
        self.token = old_token
        
        return success and success2

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Task Management API Tests...")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)

        # Test sequence
        tests = [
            self.test_health_check,
            self.test_signup,
            self.test_login,
            self.test_get_current_user,
            self.test_get_user_profile,
            self.test_update_user_profile,
            self.test_create_task,
            self.test_get_tasks,
            self.test_get_tasks_with_filter,
            self.test_get_single_task,
            self.test_update_task,
            self.test_invalid_endpoints,
            self.test_delete_task,
            self.test_logout,
            self.test_delete_user_profile
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Exception: {str(e)}")

        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed!")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
            return 1

def main():
    tester = TaskManagementAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())