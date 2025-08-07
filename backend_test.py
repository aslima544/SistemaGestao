#!/usr/bin/env python3
"""
Sistema de Gestão de Consultórios - Backend API Tests
Tests all API endpoints for the medical clinic management system
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any

class ConsultorioAPITester:
    def __init__(self, base_url="https://579d423c-bebf-48d6-96f5-a4eb007d717e.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = {
            'patients': [],
            'doctors': [],
            'appointments': []
        }

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None, expected_status: int = 200) -> tuple:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return False, {}, f"Unsupported method: {method}"

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}

            details = f"Status: {response.status_code}"
            if not success:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            return success, response_data, details

        except requests.exceptions.RequestException as e:
            return False, {}, f"Request failed: {str(e)}"

    def test_health_check(self):
        """Test health endpoint"""
        success, data, details = self.make_request('GET', '/api/health')
        self.log_test("Health Check", success, details)
        return success

    def test_login(self, username: str = "admin", password: str = "admin123"):
        """Test login endpoint"""
        login_data = {"username": username, "password": password}
        success, data, details = self.make_request('POST', '/api/auth/login', login_data)
        
        if success and 'access_token' in data:
            self.token = data['access_token']
            self.log_test("Login", True, f"{details} - Token received")
            return True
        else:
            self.log_test("Login", False, details)
            return False

    def test_get_current_user(self):
        """Test get current user endpoint"""
        success, data, details = self.make_request('GET', '/api/auth/me')
        
        if success and 'username' in data:
            self.log_test("Get Current User", True, f"{details} - User: {data.get('username')}")
            return True
        else:
            self.log_test("Get Current User", False, details)
            return False

    def test_create_patient(self):
        """Test create patient endpoint"""
        patient_data = {
            "name": "João Silva",
            "email": "joao.silva@email.com",
            "phone": "(11) 99999-9999",
            "cpf": "123.456.789-00",
            "birth_date": "1990-01-15T00:00:00Z",
            "address": "Rua das Flores, 123",
            "medical_history": "Histórico médico de teste"
        }
        
        success, data, details = self.make_request('POST', '/api/patients', patient_data, 200)
        
        if success and 'id' in data:
            self.created_resources['patients'].append(data['id'])
            self.log_test("Create Patient", True, f"{details} - Patient ID: {data['id']}")
            return data['id']
        else:
            self.log_test("Create Patient", False, details)
            return None

    def test_get_patients(self):
        """Test get all patients endpoint"""
        success, data, details = self.make_request('GET', '/api/patients')
        
        if success and isinstance(data, list):
            self.log_test("Get Patients", True, f"{details} - Found {len(data)} patients")
            return True
        else:
            self.log_test("Get Patients", False, details)
            return False

    def test_get_patient_by_id(self, patient_id: str):
        """Test get patient by ID endpoint"""
        success, data, details = self.make_request('GET', f'/api/patients/{patient_id}')
        
        if success and data.get('id') == patient_id:
            self.log_test("Get Patient by ID", True, f"{details} - Patient: {data.get('name')}")
            return True
        else:
            self.log_test("Get Patient by ID", False, details)
            return False

    def test_update_patient(self, patient_id: str):
        """Test update patient endpoint"""
        update_data = {
            "name": "João Silva Atualizado",
            "email": "joao.silva.updated@email.com",
            "phone": "(11) 88888-8888",
            "cpf": "123.456.789-00",
            "birth_date": "1990-01-15T00:00:00Z",
            "address": "Rua das Flores, 456",
            "medical_history": "Histórico médico atualizado"
        }
        
        success, data, details = self.make_request('PUT', f'/api/patients/{patient_id}', update_data)
        
        if success and data.get('name') == update_data['name']:
            self.log_test("Update Patient", True, f"{details} - Updated name: {data.get('name')}")
            return True
        else:
            self.log_test("Update Patient", False, details)
            return False

    def test_create_doctor(self):
        """Test create doctor endpoint"""
        doctor_data = {
            "name": "Dr. Maria Santos",
            "email": "maria.santos@clinica.com",
            "phone": "(11) 77777-7777",
            "crm": "CRM/SP 123456",
            "specialty": "Cardiologia"
        }
        
        success, data, details = self.make_request('POST', '/api/doctors', doctor_data, 200)
        
        if success and 'id' in data:
            self.created_resources['doctors'].append(data['id'])
            self.log_test("Create Doctor", True, f"{details} - Doctor ID: {data['id']}")
            return data['id']
        else:
            self.log_test("Create Doctor", False, details)
            return None

    def test_get_doctors(self):
        """Test get all doctors endpoint"""
        success, data, details = self.make_request('GET', '/api/doctors')
        
        if success and isinstance(data, list):
            self.log_test("Get Doctors", True, f"{details} - Found {len(data)} doctors")
            return True
        else:
            self.log_test("Get Doctors", False, details)
            return False

    def test_get_doctor_by_id(self, doctor_id: str):
        """Test get doctor by ID endpoint"""
        success, data, details = self.make_request('GET', f'/api/doctors/{doctor_id}')
        
        if success and data.get('id') == doctor_id:
            self.log_test("Get Doctor by ID", True, f"{details} - Doctor: {data.get('name')}")
            return True
        else:
            self.log_test("Get Doctor by ID", False, details)
            return False

    def test_create_appointment(self, patient_id: str, doctor_id: str):
        """Test create appointment endpoint"""
        # Schedule appointment for tomorrow at 10:00 AM
        tomorrow = datetime.now() + timedelta(days=1)
        appointment_date = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        
        appointment_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_date": appointment_date.isoformat() + "Z",
            "duration_minutes": 30,
            "notes": "Consulta de rotina",
            "status": "scheduled"
        }
        
        success, data, details = self.make_request('POST', '/api/appointments', appointment_data, 200)
        
        if success and 'id' in data:
            self.created_resources['appointments'].append(data['id'])
            self.log_test("Create Appointment", True, f"{details} - Appointment ID: {data['id']}")
            return data['id']
        else:
            self.log_test("Create Appointment", False, details)
            return None

    def test_get_appointments(self):
        """Test get all appointments endpoint"""
        success, data, details = self.make_request('GET', '/api/appointments')
        
        if success and isinstance(data, list):
            self.log_test("Get Appointments", True, f"{details} - Found {len(data)} appointments")
            return True
        else:
            self.log_test("Get Appointments", False, details)
            return False

    def test_get_appointment_by_id(self, appointment_id: str):
        """Test get appointment by ID endpoint"""
        success, data, details = self.make_request('GET', f'/api/appointments/{appointment_id}')
        
        if success and data.get('id') == appointment_id:
            self.log_test("Get Appointment by ID", True, f"{details} - Status: {data.get('status')}")
            return True
        else:
            self.log_test("Get Appointment by ID", False, details)
            return False

    def test_update_appointment(self, appointment_id: str, patient_id: str, doctor_id: str, consultorio_id: str = None):
        """Test update appointment endpoint"""
        # Update appointment for day after tomorrow at 2:00 PM
        day_after_tomorrow = datetime.now() + timedelta(days=2)
        appointment_date = day_after_tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        
        update_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_date": appointment_date.isoformat() + "Z",
            "duration_minutes": 45,
            "notes": "Consulta de retorno - atualizada",
            "status": "scheduled"
        }
        
        # Add consultorio_id if provided
        if consultorio_id:
            update_data["consultorio_id"] = consultorio_id
        
        success, data, details = self.make_request('PUT', f'/api/appointments/{appointment_id}', update_data)
        
        if success and data.get('duration_minutes') == 45:
            self.log_test("Update Appointment", True, f"{details} - Duration updated to 45 min")
            return True
        else:
            self.log_test("Update Appointment", False, details)
            return False

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        success, data, details = self.make_request('GET', '/api/dashboard/stats')
        
        expected_keys = ['total_patients', 'total_doctors', 'total_appointments', 'today_appointments', 'recent_appointments']
        
        if success and all(key in data for key in expected_keys):
            stats_info = f"Patients: {data['total_patients']}, Doctors: {data['total_doctors']}, Appointments: {data['total_appointments']}"
            self.log_test("Dashboard Stats", True, f"{details} - {stats_info}")
            return True
        else:
            self.log_test("Dashboard Stats", False, details)
            return False

    def test_get_consultorios(self):
        """Test get all consultorios endpoint"""
        success, data, details = self.make_request('GET', '/api/consultorios')
        
        if success and isinstance(data, list):
            # Should have 8 predefined consultorios (C1-C8)
            expected_count = 8
            actual_count = len(data)
            if actual_count >= expected_count:
                self.log_test("Get Consultorios", True, f"{details} - Found {actual_count} consultorios (expected >= {expected_count})")
                return True, data
            else:
                self.log_test("Get Consultorios", False, f"{details} - Found {actual_count} consultorios, expected >= {expected_count}")
                return False, data
        else:
            self.log_test("Get Consultorios", False, details)
            return False, []

    def test_weekly_schedule(self):
        """Test weekly schedule endpoint"""
        success, data, details = self.make_request('GET', '/api/consultorios/weekly-schedule')
        
        expected_keys = ['fixed_consultorios', 'rotative_consultorios', 'schedule_grid']
        
        if success and all(key in data for key in expected_keys):
            fixed_count = len(data.get('fixed_consultorios', []))
            rotative_count = len(data.get('rotative_consultorios', []))
            schedule_grid_count = len(data.get('schedule_grid', {}))
            
            # Should have 5 fixed (C1-C5) and 3 rotative (C6-C8)
            if fixed_count >= 5 and rotative_count >= 3:
                self.log_test("Weekly Schedule", True, f"{details} - Fixed: {fixed_count}, Rotative: {rotative_count}, Grid: {schedule_grid_count}")
                return True, data
            else:
                self.log_test("Weekly Schedule", False, f"{details} - Fixed: {fixed_count} (expected >=5), Rotative: {rotative_count} (expected >=3)")
                return False, data
        else:
            self.log_test("Weekly Schedule", False, details)
            return False, {}

    def test_consultorio_availability(self):
        """Test consultorio availability for specific day"""
        success, data, details = self.make_request('GET', '/api/consultorios/availability/monday')
        
        if success and isinstance(data, list):
            # Should return availability for all consultorios
            if len(data) >= 8:
                self.log_test("Consultorio Availability (Monday)", True, f"{details} - Found availability for {len(data)} consultorios")
                return True
            else:
                self.log_test("Consultorio Availability (Monday)", False, f"{details} - Found availability for {len(data)} consultorios, expected >= 8")
                return False
        else:
            self.log_test("Consultorio Availability (Monday)", False, details)
            return False

    def test_create_appointment_with_consultorio(self, patient_id: str, doctor_id: str, consultorio_id: str):
        """Test create appointment with specific consultorio"""
        # Schedule appointment for tomorrow at 10:00 AM
        tomorrow = datetime.now() + timedelta(days=1)
        appointment_date = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        
        appointment_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "consultorio_id": consultorio_id,
            "appointment_date": appointment_date.isoformat() + "Z",
            "duration_minutes": 30,
            "notes": "Consulta com consultório específico",
            "status": "scheduled"
        }
        
        success, data, details = self.make_request('POST', '/api/appointments', appointment_data, 200)
        
        if success and 'id' in data and data.get('consultorio_id') == consultorio_id:
            self.created_resources['appointments'].append(data['id'])
            self.log_test("Create Appointment with Consultorio", True, f"{details} - Appointment ID: {data['id']}, Consultorio: {consultorio_id}")
            return data['id']
        else:
            self.log_test("Create Appointment with Consultorio", False, details)
            return None

    def test_appointment_conflict(self, patient_id: str, doctor_id: str, consultorio_id: str):
        """Test appointment conflict detection"""
        # Try to schedule at the same time as previous appointment
        tomorrow = datetime.now() + timedelta(days=1)
        appointment_date = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        
        appointment_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "consultorio_id": consultorio_id,
            "appointment_date": appointment_date.isoformat() + "Z",
            "duration_minutes": 30,
            "notes": "Consulta conflitante",
            "status": "scheduled"
        }
        
        success, data, details = self.make_request('POST', '/api/appointments', appointment_data, 409)  # Expect conflict
        
        if success:  # Success means we got the expected 409 status
            self.log_test("Appointment Conflict Detection", True, f"{details} - Conflict properly detected")
            return True
        else:
            self.log_test("Appointment Conflict Detection", False, f"{details} - Conflict not detected properly")
            return False

    def test_delete_patient(self, patient_id: str):
        """Test delete patient endpoint"""
        success, data, details = self.make_request('DELETE', f'/api/patients/{patient_id}', expected_status=200)
        
        if success:
            self.log_test("Delete Patient", True, f"{details} - Patient deleted")
            return True
        else:
            self.log_test("Delete Patient", False, details)
            return False

    def investigate_c3_appointments(self):
        """Investigate C3 appointments and their dates - CRITICAL DEBUG"""
        print("\n" + "🔍" * 60)
        print("🔍 CRITICAL INVESTIGATION: C3 Appointments Date Analysis")
        print("🔍" * 60)
        
        # Target consultorio C3 ID
        c3_consultorio_id = "0f85e815-9efc-42fa-bdc9-11a924683e03"
        
        # Get all appointments
        success, appointments_data, details = self.make_request('GET', '/api/appointments')
        
        if not success:
            print(f"❌ Failed to fetch appointments: {details}")
            return False
        
        print(f"✅ Successfully fetched {len(appointments_data)} total appointments")
        
        # Filter C3 appointments
        c3_appointments = [apt for apt in appointments_data if apt.get('consultorio_id') == c3_consultorio_id]
        
        print(f"\n📋 Found {len(c3_appointments)} appointments for Consultorio C3")
        print(f"📋 Target C3 ID: {c3_consultorio_id}")
        
        if not c3_appointments:
            print("⚠️  No appointments found for C3 - this might be the issue!")
            return False
        
        # Analyze each C3 appointment
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"\n📅 Date Analysis (Today: {today}, Tomorrow: {tomorrow}):")
        print("-" * 80)
        
        for i, apt in enumerate(c3_appointments, 1):
            apt_date = apt.get('appointment_date', 'N/A')
            apt_time = "N/A"
            apt_day = "N/A"
            
            # Parse appointment date
            if apt_date != 'N/A':
                try:
                    if isinstance(apt_date, str):
                        # Handle ISO format
                        parsed_date = datetime.fromisoformat(apt_date.replace('Z', '+00:00'))
                    else:
                        # Handle datetime object
                        parsed_date = apt_date
                    
                    apt_day = parsed_date.strftime('%Y-%m-%d')
                    apt_time = parsed_date.strftime('%H:%M')
                    
                    # Determine if today or tomorrow
                    if apt_day == today:
                        day_label = "TODAY"
                    elif apt_day == tomorrow:
                        day_label = "TOMORROW"
                    else:
                        day_label = "OTHER"
                    
                except Exception as e:
                    day_label = f"PARSE_ERROR: {str(e)}"
            
            print(f"  {i}. Appointment ID: {apt.get('id', 'N/A')}")
            print(f"     📅 Date: {apt_day} ({day_label})")
            print(f"     🕐 Time: {apt_time}")
            print(f"     👤 Patient: {apt.get('patient_name', 'N/A')}")
            print(f"     👨‍⚕️ Doctor: {apt.get('doctor_name', 'N/A')}")
            print(f"     📝 Status: {apt.get('status', 'N/A')}")
            print(f"     ⏱️  Duration: {apt.get('duration_minutes', 'N/A')} minutes")
            print(f"     🏥 Consultorio: {apt.get('consultorio_name', 'N/A')}")
            print(f"     📊 Raw Date: {apt_date}")
            print("-" * 80)
        
        # Check for specific times mentioned in the issue (14:30 and 14:45)
        target_times = ['14:30', '14:45']
        found_target_times = []
        
        for apt in c3_appointments:
            apt_date = apt.get('appointment_date', 'N/A')
            if apt_date != 'N/A':
                try:
                    if isinstance(apt_date, str):
                        parsed_date = datetime.fromisoformat(apt_date.replace('Z', '+00:00'))
                    else:
                        parsed_date = apt_date
                    
                    apt_time = parsed_date.strftime('%H:%M')
                    if apt_time in target_times:
                        found_target_times.append({
                            'time': apt_time,
                            'date': parsed_date.strftime('%Y-%m-%d'),
                            'id': apt.get('id', 'N/A'),
                            'status': apt.get('status', 'N/A')
                        })
                except:
                    pass
        
        print(f"\n🎯 TARGET TIMES ANALYSIS (14:30 and 14:45):")
        print("-" * 50)
        if found_target_times:
            for target in found_target_times:
                day_type = "TODAY" if target['date'] == today else "TOMORROW" if target['date'] == tomorrow else "OTHER"
                print(f"  ✅ Found {target['time']} on {target['date']} ({day_type})")
                print(f"     ID: {target['id']}, Status: {target['status']}")
        else:
            print("  ❌ No appointments found at 14:30 or 14:45")
        
        print("\n" + "🔍" * 60)
        print("🔍 INVESTIGATION COMPLETE")
        print("🔍" * 60)
        
        return True

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Sistema de Gestão de Consultórios API Tests")
        print("=" * 60)
        
        # Test health check
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False
        
        # Test authentication
        if not self.test_login():
            print("❌ Login failed - stopping tests")
            return False
        
        if not self.test_get_current_user():
            print("❌ Get current user failed")
            return False
        
        # Test patient operations
        patient_id = self.test_create_patient()
        if not patient_id:
            print("❌ Patient creation failed - stopping patient tests")
        else:
            self.test_get_patients()
            self.test_get_patient_by_id(patient_id)
            self.test_update_patient(patient_id)
        
        # Test doctor operations
        doctor_id = self.test_create_doctor()
        if not doctor_id:
            print("❌ Doctor creation failed - stopping doctor tests")
        else:
            self.test_get_doctors()
            self.test_get_doctor_by_id(doctor_id)
        
        # Test consultorio operations
        consultorio_success, consultorios_data = self.test_get_consultorios()
        self.test_weekly_schedule()
        self.test_consultorio_availability()
        
        # Test appointment operations with consultorio (requires patient, doctor, and consultorio)
        if patient_id and doctor_id and consultorio_success and consultorios_data:
            # Use the first available consultorio
            first_consultorio_id = consultorios_data[0]['id'] if consultorios_data else None
            if first_consultorio_id:
                appointment_id = self.test_create_appointment_with_consultorio(patient_id, doctor_id, first_consultorio_id)
                if appointment_id:
                    self.test_get_appointments()
                    self.test_get_appointment_by_id(appointment_id)
                    self.test_update_appointment(appointment_id, patient_id, doctor_id, first_consultorio_id)
                    # Test conflict detection
                    self.test_appointment_conflict(patient_id, doctor_id, first_consultorio_id)
        elif patient_id and doctor_id:
            # Fallback to original appointment test without consultorio
            appointment_id = self.test_create_appointment(patient_id, doctor_id)
            if appointment_id:
                self.test_get_appointments()
                self.test_get_appointment_by_id(appointment_id)
                self.test_update_appointment(appointment_id, patient_id, doctor_id)
        
        # Test dashboard
        self.test_dashboard_stats()
        
        # Clean up - delete created patient (this will test delete functionality)
        if patient_id:
            self.test_delete_patient(patient_id)
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests PASSED! Backend API is working correctly.")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests FAILED. Please check the issues above.")
            return False

def main():
    """Main test execution"""
    print("Sistema de Gestão de Consultórios - Backend API Testing")
    print(f"Testing against: https://579d423c-bebf-48d6-96f5-a4eb007d717e.preview.emergentagent.com")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = ConsultorioAPITester()
    
    # Quick investigation mode for C3 appointments
    if len(sys.argv) > 1 and sys.argv[1] == "--investigate-c3":
        print("\n🔍 RUNNING C3 INVESTIGATION MODE")
        if not tester.test_login():
            print("❌ Login failed - cannot investigate")
            return 1
        
        tester.investigate_c3_appointments()
        return 0
    
    # Full test suite
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())