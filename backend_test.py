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

    def test_c3_slots_time_logic(self):
        """Test C3 slots endpoint with specific focus on time comparison logic for current time 15:47"""
        print("\n" + "🎯" * 60)
        print("🎯 CRITICAL TEST: C3 Slots Time Logic for Current Time 15:47")
        print("🎯" * 60)
        
        # C3 consultorio ID
        c3_consultorio_id = "0f85e815-9efc-42fa-bdc9-11a924683e03"
        test_date = "2025-08-07"  # Today
        
        # Test the slots endpoint
        endpoint = f"/api/consultorios/{c3_consultorio_id}/slots?date={test_date}"
        success, data, details = self.make_request('GET', endpoint)
        
        if not success:
            self.log_test("C3 Slots Endpoint", False, f"{details}")
            return False
        
        self.log_test("C3 Slots Endpoint", True, f"{details} - Retrieved slots data")
        
        # Verify response structure
        expected_keys = ['consultorio_id', 'consultorio_name', 'date', 'slots']
        if not all(key in data for key in expected_keys):
            self.log_test("C3 Slots Response Structure", False, f"Missing keys: {set(expected_keys) - set(data.keys())}")
            return False
        
        self.log_test("C3 Slots Response Structure", True, "All required keys present")
        
        # Verify consultorio info
        if data['consultorio_id'] != c3_consultorio_id:
            self.log_test("C3 Consultorio ID", False, f"Expected {c3_consultorio_id}, got {data['consultorio_id']}")
            return False
        
        if data['consultorio_name'] != 'C3':
            self.log_test("C3 Consultorio Name", False, f"Expected C3, got {data['consultorio_name']}")
            return False
        
        self.log_test("C3 Consultorio Info", True, f"ID: {data['consultorio_id']}, Name: {data['consultorio_name']}")
        
        # Verify date
        if data['date'] != test_date:
            self.log_test("C3 Slots Date", False, f"Expected {test_date}, got {data['date']}")
            return False
        
        self.log_test("C3 Slots Date", True, f"Date: {data['date']}")
        
        # Analyze slots
        slots = data.get('slots', [])
        if not slots:
            self.log_test("C3 Slots Data", False, "No slots returned")
            return False
        
        print(f"\n📊 SLOT ANALYSIS for C3 on {test_date}")
        print("-" * 80)
        
        # Expected C3 schedule: 08:00-17:00 (ends at 17:00, so last slot is 16:45)
        expected_first_slot = "08:00"
        expected_last_slot = "16:45"
        
        slot_times = [slot['time'] for slot in slots]
        first_slot = slot_times[0] if slot_times else None
        last_slot = slot_times[-1] if slot_times else None
        
        print(f"🕐 Total slots: {len(slots)}")
        print(f"🕐 First slot: {first_slot} (expected: {expected_first_slot})")
        print(f"🕐 Last slot: {last_slot} (expected: {expected_last_slot})")
        
        # Verify schedule boundaries
        schedule_correct = first_slot == expected_first_slot and last_slot == expected_last_slot
        if schedule_correct:
            self.log_test("C3 Schedule Boundaries", True, f"Correct schedule: {first_slot} to {last_slot}")
        else:
            self.log_test("C3 Schedule Boundaries", False, f"Incorrect schedule: {first_slot} to {last_slot}, expected: {expected_first_slot} to {expected_last_slot}")
        
        # CRITICAL TEST: Time comparison logic for current time 15:47
        print(f"\n🎯 CRITICAL TIME LOGIC TEST (Current time: 15:47)")
        print("-" * 80)
        
        # Slots that should be is_past=true (before 15:47)
        past_slots_expected = []
        # Slots that should be is_past=false (15:47 and after)
        future_slots_expected = ["16:00", "16:15", "16:30", "16:45"]
        
        # Generate expected past slots (08:00 to 15:45)
        for hour in range(8, 16):  # 8 to 15
            for minute in [0, 15, 30, 45]:
                past_slots_expected.append(f"{hour:02d}:{minute:02d}")
        past_slots_expected.append("15:45")  # Last past slot
        
        print(f"📋 Expected past slots (is_past=true): {len(past_slots_expected)} slots")
        print(f"📋 Expected future slots (is_past=false): {future_slots_expected}")
        
        # Analyze each slot
        past_slots_actual = []
        future_slots_actual = []
        occupied_slots = []
        
        for slot in slots:
            slot_time = slot['time']
            is_past = slot.get('is_past', False)
            is_occupied = slot.get('is_occupied', False)
            is_available = slot.get('is_available', False)
            occupancy_info = slot.get('occupancy_info')
            
            if is_past:
                past_slots_actual.append(slot_time)
            else:
                future_slots_actual.append(slot_time)
            
            if is_occupied:
                occupied_slots.append({
                    'time': slot_time,
                    'is_past': is_past,
                    'occupancy_info': occupancy_info
                })
        
        print(f"\n📊 ACTUAL SLOT ANALYSIS:")
        print(f"🔴 Past slots (is_past=true): {len(past_slots_actual)}")
        print(f"🟢 Future slots (is_past=false): {len(future_slots_actual)}")
        print(f"🔴 Occupied slots: {len(occupied_slots)}")
        
        # Test critical future slots (16:00, 16:15, 16:30, 16:45)
        critical_test_passed = True
        for expected_future_slot in future_slots_expected:
            if expected_future_slot in future_slots_actual:
                print(f"✅ {expected_future_slot}: Correctly marked as is_past=false")
            else:
                print(f"❌ {expected_future_slot}: INCORRECTLY marked as is_past=true")
                critical_test_passed = False
        
        if critical_test_passed:
            self.log_test("Critical Time Logic (16:00-16:45)", True, "All critical slots correctly marked as future")
        else:
            self.log_test("Critical Time Logic (16:00-16:45)", False, "Some critical slots incorrectly marked as past")
        
        # Test that 15:45 is marked as past
        slot_1545_past = "15:45" in past_slots_actual
        if slot_1545_past:
            self.log_test("15:45 Slot Time Logic", True, "15:45 correctly marked as is_past=true")
        else:
            self.log_test("15:45 Slot Time Logic", False, "15:45 incorrectly marked as is_past=false")
        
        # Analyze occupied slots
        print(f"\n🏥 OCCUPIED SLOTS ANALYSIS:")
        print("-" * 40)
        
        if occupied_slots:
            for occupied in occupied_slots:
                occupancy_info = occupied['occupancy_info']
                past_status = "PAST" if occupied['is_past'] else "FUTURE"
                
                print(f"🔴 {occupied['time']} ({past_status})")
                if occupancy_info:
                    print(f"   👤 Patient: {occupancy_info.get('patient_name', 'N/A')}")
                    print(f"   👨‍⚕️ Doctor: {occupancy_info.get('doctor_name', 'N/A')}")
                    print(f"   📝 Status: {occupancy_info.get('status', 'N/A')}")
                    print(f"   ⏱️ Duration: {occupancy_info.get('duration', 'N/A')} min")
                    print(f"   🆔 Appointment ID: {occupancy_info.get('appointment_id', 'N/A')}")
                else:
                    print(f"   ⚠️ No occupancy info provided")
                print()
            
            self.log_test("Occupied Slots Info", True, f"Found {len(occupied_slots)} occupied slots with details")
        else:
            print("✅ No occupied slots found")
            self.log_test("Occupied Slots Info", True, "No occupied slots (clean schedule)")
        
        # Summary
        print(f"\n🎯 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Endpoint accessible: {success}")
        print(f"✅ Response structure: Valid")
        print(f"✅ Consultorio info: C3 ({c3_consultorio_id})")
        print(f"✅ Date: {test_date}")
        print(f"✅ Schedule boundaries: {schedule_correct}")
        print(f"✅ Critical time logic: {critical_test_passed}")
        print(f"✅ 15:45 past logic: {slot_1545_past}")
        print(f"📊 Total slots: {len(slots)}")
        print(f"📊 Past slots: {len(past_slots_actual)}")
        print(f"📊 Future slots: {len(future_slots_actual)}")
        print(f"📊 Occupied slots: {len(occupied_slots)}")
        
        overall_success = success and schedule_correct and critical_test_passed and slot_1545_past
        
        if overall_success:
            self.log_test("C3 Slots Time Logic Overall", True, "All time logic tests passed")
        else:
            self.log_test("C3 Slots Time Logic Overall", False, "Some time logic tests failed")
        
        print("🎯" * 60)
        
        return overall_success

    def investigate_missing_1530_appointment(self):
        """URGENT: Investigate missing 15:30 appointment for C3 today (2025-08-07)"""
        print("\n" + "🚨" * 60)
        print("🚨 URGENT INVESTIGATION: Missing 15:30 C3 Appointment (2025-08-07)")
        print("🚨" * 60)
        
        # Target consultorio C3 ID
        c3_consultorio_id = "0f85e815-9efc-42fa-bdc9-11a924683e03"
        
        # Get all appointments
        success, appointments_data, details = self.make_request('GET', '/api/appointments')
        
        if not success:
            print(f"❌ Failed to fetch appointments: {details}")
            return False
        
        print(f"✅ Successfully fetched {len(appointments_data)} total appointments")
        
        # Current date analysis
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 Today's date: {today}")
        print(f"🎯 Looking for: C3 15:30 appointment on {today}")
        print(f"🏥 C3 Consultorio ID: {c3_consultorio_id}")
        
        # 1. Search ALL appointments for 15:30 on ANY date
        print(f"\n🔍 STEP 1: Searching ALL appointments for 15:30 slots (any date, any consultorio)")
        print("-" * 80)
        all_1530_appointments = []
        
        for apt in appointments_data:
            apt_date = apt.get('appointment_date', 'N/A')
            if apt_date != 'N/A':
                try:
                    if isinstance(apt_date, str):
                        parsed_date = datetime.fromisoformat(apt_date.replace('Z', '+00:00'))
                    else:
                        parsed_date = apt_date
                    
                    apt_time = parsed_date.strftime('%H:%M')
                    if apt_time == '15:30':
                        all_1530_appointments.append({
                            'time': apt_time,
                            'date': parsed_date.strftime('%Y-%m-%d'),
                            'id': apt.get('id', 'N/A'),
                            'consultorio_id': apt.get('consultorio_id', 'N/A'),
                            'consultorio_name': apt.get('consultorio_name', 'N/A'),
                            'patient_name': apt.get('patient_name', 'N/A'),
                            'status': apt.get('status', 'N/A'),
                            'created_at': apt.get('created_at', 'N/A')
                        })
                except Exception as e:
                    print(f"⚠️  Error parsing appointment date: {e}")
        
        if all_1530_appointments:
            print(f"✅ Found {len(all_1530_appointments)} appointments at 15:30:")
            for i, apt in enumerate(all_1530_appointments, 1):
                day_type = "TODAY" if apt['date'] == today else "OTHER DATE"
                is_c3 = "✅ C3" if apt['consultorio_id'] == c3_consultorio_id else "❌ NOT C3"
                print(f"  {i}. {apt['date']} ({day_type}) - {is_c3}")
                print(f"     🏥 Consultorio: {apt['consultorio_name']} (ID: {apt['consultorio_id']})")
                print(f"     👤 Patient: {apt['patient_name']}")
                print(f"     📝 Status: {apt['status']}")
                print(f"     🆔 ID: {apt['id']}")
                print(f"     📅 Created: {apt['created_at']}")
                print()
        else:
            print("❌ NO 15:30 appointments found in entire system!")
        
        # 2. Search specifically for C3 appointments on ANY date
        print(f"\n🔍 STEP 2: Searching ALL C3 appointments (any date)")
        print("-" * 80)
        c3_appointments = [apt for apt in appointments_data if apt.get('consultorio_id') == c3_consultorio_id]
        
        print(f"📋 Found {len(c3_appointments)} total appointments for C3")
        
        if c3_appointments:
            # Group by date
            c3_by_date = {}
            for apt in c3_appointments:
                apt_date = apt.get('appointment_date', 'N/A')
                if apt_date != 'N/A':
                    try:
                        if isinstance(apt_date, str):
                            parsed_date = datetime.fromisoformat(apt_date.replace('Z', '+00:00'))
                        else:
                            parsed_date = apt_date
                        
                        date_str = parsed_date.strftime('%Y-%m-%d')
                        time_str = parsed_date.strftime('%H:%M')
                        
                        if date_str not in c3_by_date:
                            c3_by_date[date_str] = []
                        
                        c3_by_date[date_str].append({
                            'time': time_str,
                            'id': apt.get('id', 'N/A'),
                            'patient_name': apt.get('patient_name', 'N/A'),
                            'status': apt.get('status', 'N/A'),
                            'created_at': apt.get('created_at', 'N/A')
                        })
                    except Exception as e:
                        print(f"⚠️  Error parsing C3 appointment: {e}")
            
            # Display by date
            for date_str in sorted(c3_by_date.keys()):
                day_type = "TODAY" if date_str == today else "OTHER DATE"
                appointments = sorted(c3_by_date[date_str], key=lambda x: x['time'])
                print(f"\n📅 {date_str} ({day_type}) - {len(appointments)} appointments:")
                
                for apt in appointments:
                    is_target = "🎯 TARGET!" if apt['time'] == '15:30' and date_str == today else ""
                    print(f"    🕐 {apt['time']} - {apt['patient_name']} ({apt['status']}) {is_target}")
                    print(f"       ID: {apt['id']}")
        
        # 3. Check confirmed existing appointments for today
        print(f"\n🔍 STEP 3: Confirmed existing C3 appointments for TODAY ({today})")
        print("-" * 80)
        
        confirmed_today = [
            "15:45 (canceled)",
            "17:30", "17:45", "18:00", "18:30", "18:45", "19:00"
        ]
        
        print("📋 Expected appointments based on user report:")
        for apt_time in confirmed_today:
            print(f"  ✅ {apt_time}")
        
        # Verify these in actual data
        today_c3_appointments = []
        for apt in c3_appointments:
            apt_date = apt.get('appointment_date', 'N/A')
            if apt_date != 'N/A':
                try:
                    if isinstance(apt_date, str):
                        parsed_date = datetime.fromisoformat(apt_date.replace('Z', '+00:00'))
                    else:
                        parsed_date = apt_date
                    
                    if parsed_date.strftime('%Y-%m-%d') == today:
                        today_c3_appointments.append({
                            'time': parsed_date.strftime('%H:%M'),
                            'status': apt.get('status', 'N/A'),
                            'patient_name': apt.get('patient_name', 'N/A'),
                            'id': apt.get('id', 'N/A')
                        })
                except:
                    pass
        
        print(f"\n📊 ACTUAL C3 appointments found for TODAY:")
        if today_c3_appointments:
            today_c3_appointments.sort(key=lambda x: x['time'])
            for apt in today_c3_appointments:
                print(f"  🕐 {apt['time']} - {apt['patient_name']} ({apt['status']}) - ID: {apt['id']}")
        else:
            print("  ❌ NO C3 appointments found for today!")
        
        # 4. Search for recent failed attempts or deleted appointments
        print(f"\n🔍 STEP 4: Analysis of appointment creation patterns")
        print("-" * 80)
        
        # Look for appointments created recently that might have been deleted
        recent_appointments = []
        cutoff_date = datetime.now() - timedelta(days=2)  # Last 2 days
        
        for apt in appointments_data:
            created_at = apt.get('created_at', 'N/A')
            if created_at != 'N/A':
                try:
                    if isinstance(created_at, str):
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_date = created_at
                    
                    if created_date >= cutoff_date:
                        recent_appointments.append({
                            'created': created_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'consultorio_id': apt.get('consultorio_id', 'N/A'),
                            'consultorio_name': apt.get('consultorio_name', 'N/A'),
                            'appointment_date': apt.get('appointment_date', 'N/A'),
                            'status': apt.get('status', 'N/A'),
                            'id': apt.get('id', 'N/A')
                        })
                except:
                    pass
        
        print(f"📊 Recent appointments (last 2 days): {len(recent_appointments)}")
        c3_recent = [apt for apt in recent_appointments if apt['consultorio_id'] == c3_consultorio_id]
        
        if c3_recent:
            print(f"🏥 Recent C3 appointments: {len(c3_recent)}")
            for apt in c3_recent:
                print(f"  📅 Created: {apt['created']}")
                print(f"  🕐 Scheduled: {apt['appointment_date']}")
                print(f"  📝 Status: {apt['status']}")
                print(f"  🆔 ID: {apt['id']}")
                print()
        else:
            print("❌ No recent C3 appointments found")
        
        # 5. Final conclusion
        print(f"\n🚨 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        # Check if 15:30 appointment exists for C3 today
        target_found = False
        for apt in all_1530_appointments:
            if apt['date'] == today and apt['consultorio_id'] == c3_consultorio_id:
                target_found = True
                print(f"✅ FOUND: 15:30 C3 appointment for today!")
                print(f"   🆔 ID: {apt['id']}")
                print(f"   👤 Patient: {apt['patient_name']}")
                print(f"   📝 Status: {apt['status']}")
                break
        
        if not target_found:
            print(f"❌ CONFIRMED: NO 15:30 C3 appointment found for today ({today})")
            print(f"🔍 Possible explanations:")
            print(f"   1. Appointment was never successfully created")
            print(f"   2. Appointment was created but later deleted/canceled")
            print(f"   3. Appointment was created for wrong date")
            print(f"   4. Frontend/backend synchronization issue")
            print(f"   5. Database inconsistency")
        
        print("\n" + "🚨" * 60)
        print("🚨 URGENT INVESTIGATION COMPLETE")
        print("🚨" * 60)
        
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
    
    # URGENT investigation mode for missing 15:30 appointment
    if len(sys.argv) > 1 and sys.argv[1] == "--investigate-1530":
        print("\n🚨 RUNNING URGENT 15:30 INVESTIGATION MODE")
        if not tester.test_login():
            print("❌ Login failed - cannot investigate")
            return 1
        
        tester.investigate_missing_1530_appointment()
        return 0
    
    # Quick investigation mode for C3 appointments (legacy)
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