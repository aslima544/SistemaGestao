#!/usr/bin/env python3
"""
Specific test for C3 14:30 appointment slot issue
Tests appointment creation, conflict detection, and data persistence
"""

import requests
import json
from datetime import datetime, timedelta
import sys

class C3AppointmentTester:
    def __init__(self):
        self.base_url = "https://579d423c-bebf-48d6-96f5-a4eb007d717e.preview.emergentagent.com"
        self.token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}: {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
    def make_request(self, method, endpoint, data=None, expected_status=200):
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
                
            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
                
            return success, response_data, response.status_code
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}, 0
    
    def login(self):
        """Login to get authentication token"""
        login_data = {"username": "admin", "password": "admin123"}
        success, data, status_code = self.make_request('POST', '/api/auth/login', login_data)
        
        if success and 'access_token' in data:
            self.token = data['access_token']
            self.log_result("Authentication", True, f"Token received (Status: {status_code})")
            return True
        else:
            self.log_result("Authentication", False, f"Login failed (Status: {status_code})")
            return False
    
    def get_c3_consultorio_id(self):
        """Get the ID of consultorio C3"""
        success, data, status_code = self.make_request('GET', '/api/consultorios')
        
        if success and isinstance(data, list):
            for consultorio in data:
                if consultorio.get('name') == 'C3':
                    c3_id = consultorio.get('id')
                    schedule = consultorio.get('fixed_schedule', {})
                    self.log_result("Get C3 Consultorio", True, 
                                  f"Found C3 (ID: {c3_id[:8]}...) - Schedule: {schedule.get('start')}-{schedule.get('end')}")
                    return c3_id
            
            self.log_result("Get C3 Consultorio", False, "C3 not found in consultorio list")
            return None
        else:
            self.log_result("Get C3 Consultorio", False, f"Failed to get consultorios (Status: {status_code})")
            return None
    
    def create_test_patient(self):
        """Create a test patient for appointments"""
        patient_data = {
            "name": "Maria Silva",
            "email": "maria.silva@email.com",
            "phone": "(11) 98765-4321",
            "cpf": "987.654.321-00",
            "birth_date": "1985-05-20T00:00:00Z",
            "address": "Rua das Palmeiras, 456",
            "medical_history": "Paciente para teste de agendamento C3"
        }
        
        success, data, status_code = self.make_request('POST', '/api/patients', patient_data)
        
        if success and 'id' in data:
            patient_id = data['id']
            self.log_result("Create Test Patient", True, f"Patient created (ID: {patient_id[:8]}...)")
            return patient_id
        else:
            self.log_result("Create Test Patient", False, f"Failed to create patient (Status: {status_code})")
            return None
    
    def create_test_doctor(self):
        """Create a test doctor for appointments"""
        doctor_data = {
            "name": "Dr. Carlos Mendes",
            "email": "carlos.mendes@clinica.com",
            "phone": "(11) 91234-5678",
            "crm": "CRM/SP 654321",
            "specialty": "Clínica Geral"
        }
        
        success, data, status_code = self.make_request('POST', '/api/doctors', doctor_data)
        
        if success and 'id' in data:
            doctor_id = data['id']
            self.log_result("Create Test Doctor", True, f"Doctor created (ID: {doctor_id[:8]}...)")
            return doctor_id
        else:
            self.log_result("Create Test Doctor", False, f"Failed to create doctor (Status: {status_code})")
            return None
    
    def create_c3_appointment_1430(self, patient_id, doctor_id, consultorio_id):
        """Create appointment for C3 at 14:30 tomorrow"""
        # Calculate tomorrow at 14:30
        tomorrow = datetime.now() + timedelta(days=1)
        appointment_time = tomorrow.replace(hour=14, minute=30, second=0, microsecond=0)
        
        appointment_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "consultorio_id": consultorio_id,
            "appointment_date": appointment_time.isoformat() + "Z",
            "duration_minutes": 30,
            "notes": "Teste agendamento C3 14:30",
            "status": "scheduled"
        }
        
        success, data, status_code = self.make_request('POST', '/api/appointments', appointment_data)
        
        if success and 'id' in data:
            appointment_id = data['id']
            created_time = data.get('appointment_date', '')
            self.log_result("Create C3 14:30 Appointment", True, 
                          f"Appointment created (ID: {appointment_id[:8]}...) for {created_time}")
            return appointment_id, data
        else:
            error_detail = data.get('detail', 'Unknown error')
            self.log_result("Create C3 14:30 Appointment", False, 
                          f"Failed to create appointment (Status: {status_code}) - {error_detail}")
            return None, None
    
    def verify_appointment_in_database(self, appointment_id):
        """Verify appointment exists and has correct data"""
        success, data, status_code = self.make_request('GET', f'/api/appointments/{appointment_id}')
        
        if success:
            consultorio_id = data.get('consultorio_id', '')
            appointment_date = data.get('appointment_date', '')
            status = data.get('status', '')
            
            # Verify consultorio ID and time
            is_correct = (
                consultorio_id and 
                '14:30' in appointment_date and 
                status == 'scheduled'
            )
            
            if is_correct:
                self.log_result("Verify Appointment Data", True, 
                              f"Consultorio: {consultorio_id[:8]}..., Date: {appointment_date}, Status: {status}")
                return True, data
            else:
                self.log_result("Verify Appointment Data", False, 
                              f"Data mismatch - Consultorio: {consultorio_id}, Date: {appointment_date}, Status: {status}")
                return False, data
        else:
            self.log_result("Verify Appointment Data", False, f"Failed to get appointment (Status: {status_code})")
            return False, None
    
    def test_conflict_detection(self, patient_id, doctor_id, consultorio_id):
        """Test conflict detection by trying to create another appointment at same time"""
        # Try to create another appointment at the same time (14:30 tomorrow)
        tomorrow = datetime.now() + timedelta(days=1)
        appointment_time = tomorrow.replace(hour=14, minute=30, second=0, microsecond=0)
        
        appointment_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "consultorio_id": consultorio_id,
            "appointment_date": appointment_time.isoformat() + "Z",
            "duration_minutes": 30,
            "notes": "Teste conflito C3 14:30",
            "status": "scheduled"
        }
        
        # Expect 409 Conflict status
        success, data, status_code = self.make_request('POST', '/api/appointments', appointment_data, 409)
        
        if success and status_code == 409:
            error_detail = data.get('detail', '')
            self.log_result("Conflict Detection", True, 
                          f"Conflict properly detected (Status: {status_code}) - {error_detail}")
            return True
        else:
            self.log_result("Conflict Detection", False, 
                          f"Conflict not detected properly (Status: {status_code})")
            return False
    
    def verify_appointments_endpoint(self, appointment_id):
        """Verify /api/appointments endpoint returns the created appointment"""
        success, data, status_code = self.make_request('GET', '/api/appointments')
        
        if success and isinstance(data, list):
            # Look for our appointment in the list
            found_appointment = None
            for appointment in data:
                if appointment.get('id') == appointment_id:
                    found_appointment = appointment
                    break
            
            if found_appointment:
                consultorio_name = found_appointment.get('consultorio_name', 'N/A')
                appointment_date = found_appointment.get('appointment_date', '')
                self.log_result("Verify Appointments Endpoint", True, 
                              f"Appointment found in list - Consultorio: {consultorio_name}, Date: {appointment_date}")
                return True, found_appointment
            else:
                self.log_result("Verify Appointments Endpoint", False, 
                              f"Appointment not found in appointments list (Total: {len(data)})")
                return False, None
        else:
            self.log_result("Verify Appointments Endpoint", False, 
                          f"Failed to get appointments list (Status: {status_code})")
            return False, None
    
    def cleanup_test_data(self, patient_id, doctor_id, appointment_id):
        """Clean up test data"""
        cleanup_results = []
        
        # Delete appointment (cancel it)
        if appointment_id:
            success, _, status_code = self.make_request('PUT', f'/api/appointments/{appointment_id}/cancel')
            cleanup_results.append(f"Appointment cancel: {'✅' if success else '❌'}")
        
        # Delete patient
        if patient_id:
            success, _, status_code = self.make_request('DELETE', f'/api/patients/{patient_id}')
            cleanup_results.append(f"Patient delete: {'✅' if success else '❌'}")
        
        # Delete doctor
        if doctor_id:
            success, _, status_code = self.make_request('DELETE', f'/api/doctors/{doctor_id}')
            cleanup_results.append(f"Doctor delete: {'✅' if success else '❌'}")
        
        self.log_result("Cleanup Test Data", True, " | ".join(cleanup_results))
    
    def run_c3_appointment_test(self):
        """Run the complete C3 14:30 appointment test"""
        print("🔍 Testing C3 14:30 Appointment Slot Issue")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.login():
            return False
        
        # Step 2: Get C3 consultorio ID
        c3_id = self.get_c3_consultorio_id()
        if not c3_id:
            return False
        
        # Step 3: Create test patient and doctor
        patient_id = self.create_test_patient()
        doctor_id = self.create_test_doctor()
        
        if not patient_id or not doctor_id:
            return False
        
        # Step 4: Create C3 appointment at 14:30 tomorrow
        appointment_id, appointment_data = self.create_c3_appointment_1430(patient_id, doctor_id, c3_id)
        
        if not appointment_id:
            self.cleanup_test_data(patient_id, doctor_id, None)
            return False
        
        # Step 5: Verify appointment is saved correctly
        verify_success, _ = self.verify_appointment_in_database(appointment_id)
        
        # Step 6: Test conflict detection
        conflict_success = self.test_conflict_detection(patient_id, doctor_id, c3_id)
        
        # Step 7: Verify /api/appointments endpoint returns the appointment
        endpoint_success, _ = self.verify_appointments_endpoint(appointment_id)
        
        # Step 8: Cleanup
        self.cleanup_test_data(patient_id, doctor_id, appointment_id)
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 C3 14:30 Appointment Test Results:")
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        
        print(f"Tests passed: {passed_tests}/{total_tests}")
        
        critical_tests = [
            "Create C3 14:30 Appointment",
            "Verify Appointment Data", 
            "Conflict Detection",
            "Verify Appointments Endpoint"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        
        print(f"Critical backend tests: {critical_passed}/{len(critical_tests)}")
        
        if critical_passed == len(critical_tests):
            print("🎉 Backend functionality for C3 14:30 appointments is WORKING correctly!")
            print("✅ Appointments are created and saved properly")
            print("✅ Conflict detection prevents duplicate bookings")
            print("✅ API endpoints return correct data")
            print("\n💡 The issue appears to be frontend-related (visual state updates)")
            return True
        else:
            print("❌ Backend issues detected with C3 14:30 appointments")
            failed_tests = [result['test'] for result in self.test_results 
                          if result['test'] in critical_tests and not result['success']]
            print(f"Failed critical tests: {', '.join(failed_tests)}")
            return False

def main():
    """Main test execution"""
    print("Sistema de Gestão de Consultórios - C3 14:30 Slot Test")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = C3AppointmentTester()
    success = tester.run_c3_appointment_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())