from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.models import Group
from apps.users.models import User
from apps.hr.models import Department, Employee, LeaveRequest
from apps.hr.serializers import DepartmentSerializer, EmployeeSerializer, LeaveRequestSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date

class HRModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            username='testuser',
            password='testpass123'
        )
        self.hr_user = User.objects.create_user(
            login_id='hruser',
            username='hruser',
            password='hrpass123'
        )
        self.hr_group = Group.objects.create(name='HR')
        self.hr_user.groups.add(self.hr_group)
        self.department = Department.objects.create(name='IT', description='IT Department')
        self.employee = Employee.objects.create(
            user=self.user,
            department=self.department,
            employee_id='EMP001',
            position='Developer',
            hire_date=date(2025, 1, 1),
            phone_number='1234567890'
        )

    def test_department_creation(self):
        """Test Department model creation and string representation."""
        dept = Department.objects.create(name='Finance', description='Finance Department')
        self.assertEqual(str(dept), 'Finance')
        self.assertTrue(dept.created_at)
        self.assertTrue(dept.updated_at)

    def test_employee_creation(self):
        """Test Employee model creation and string representation."""
        self.assertEqual(str(self.employee), 'testuser - Developer')
        self.assertEqual(self.employee.user, self.user)
        self.assertEqual(self.employee.department, self.department)

    def test_leave_request_creation(self):
        """Test LeaveRequest model creation and string representation."""
        leave = LeaveRequest.objects.create(
            employee=self.employee,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 5),
            reason='Vacation',
            status='pending'
        )
        self.assertEqual(str(leave), f'Leave Request for {self.employee} - pending')
        self.assertEqual(leave.employee, self.employee)
        self.assertEqual(leave.status, 'pending')

class HRSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            login_id='testuser',
            username='testuser',
            password='testpass123'
        )
        self.department = Department.objects.create(name='IT', description='IT Department')
        self.employee = Employee.objects.create(
            user=self.user,
            department=self.department,
            employee_id='EMP001',
            position='Developer',
            hire_date=date(2025, 1, 1)
        )

    def test_department_serializer(self):
        """Test DepartmentSerializer serialization and deserialization."""
        serializer = DepartmentSerializer(self.department)
        data = serializer.data
        self.assertEqual(data['name'], 'IT')
        self.assertEqual(data['description'], 'IT Department')

        new_data = {'name': 'HR', 'description': 'Human Resources'}
        serializer = DepartmentSerializer(data=new_data)
        self.assertTrue(serializer.is_valid())
        dept = serializer.save()
        self.assertEqual(dept.name, 'HR')

    def test_employee_serializer(self):
        """Test EmployeeSerializer serialization and deserialization."""
        serializer = EmployeeSerializer(self.employee)
        data = serializer.data
        self.assertEqual(data['employee_id'], 'EMP001')
        self.assertEqual(data['position'], 'Developer')
        self.assertEqual(data['user'], 'testuser')

        new_user = User.objects.create_user(login_id='newuser', username='newuser', password='newpass123')
        new_data = {
            'user_id': new_user.id,
            'department_id': self.department.id,
            'employee_id': 'EMP002',
            'position': 'Manager',
            'hire_date': '2025-02-01',
            'phone_number': '0987654321'
        }
        serializer = EmployeeSerializer(data=new_data)
        self.assertTrue(serializer.is_valid())
        emp = serializer.save()
        self.assertEqual(emp.employee_id, 'EMP002')

    def test_leave_request_serializer(self):
        """Test LeaveRequestSerializer serialization and deserialization."""
        leave = LeaveRequest.objects.create(
            employee=self.employee,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 5),
            reason='Vacation',
            status='pending'
        )
        serializer = LeaveRequestSerializer(leave)
        data = serializer.data
        self.assertEqual(data['reason'], 'Vacation')
        self.assertEqual(data['status'], 'pending')

        new_data = {
            'employee_id': self.employee.id,
            'start_date': '2025-10-01',
            'end_date': '2025-10-03',
            'reason': 'Sick Leave',
            'status': 'pending'
        }
        serializer = LeaveRequestSerializer(data=new_data)
        self.assertTrue(serializer.is_valid())
        leave = serializer.save()
        self.assertEqual(leave.reason, 'Sick Leave')

class HRViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            login_id='testuser',
            username='testuser',
            password='testpass123'
        )
        self.hr_user = User.objects.create_user(
            login_id='hruser',
            username='hruser',
            password='hrpass123'
        )
        self.superuser = User.objects.create_superuser(
            login_id='superuser',
            username='superuser',
            password='superpass123'
        )
        self.hr_group = Group.objects.create(name='HR')
        self.hr_user.groups.add(self.hr_group)
        self.department = Department.objects.create(name='IT')
        self.employee = Employee.objects.create(
            user=self.user,
            department=self.department,
            employee_id='EMP001',
            position='Developer',
            hire_date=date(2025, 1, 1)
        )
        self.hr_employee = Employee.objects.create(
            user=self.hr_user,
            department=self.department,
            employee_id='EMP002',
            position='HR Manager',
            hire_date=date(2025, 1, 1)
        )

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_department_list_unauthenticated(self):
        """Test department list is accessible without authentication."""
        response = self.client.get('/api/hr/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_department_create_hr_user(self):
        """Test HR user can create a department."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.hr_user)}')
        data = {'name': 'Finance', 'description': 'Finance Department'}
        response = self.client.post('/api/hr/departments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)

    def test_department_create_non_hr_user(self):
        """Test non-HR user cannot create a department."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.user)}')
        data = {'name': 'Finance', 'description': 'Finance Department'}
        response = self.client.post('/api/hr/departments/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_list_authenticated(self):
        """Test authenticated user can list employees."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.user)}')
        response = self.client.get('/api/hr/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_employee_create_hr_user(self):
        """Test HR user can create an employee."""
        new_user = User.objects.create_user(login_id='newuser', username='newuser', password='newpass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.hr_user)}')
        data = {
            'user_id': new_user.id,
            'department_id': self.department.id,
            'employee_id': 'EMP003',
            'position': 'Analyst',
            'hire_date': '2025-02-01',
            'phone_number': '1234567890'
        }
        response = self.client.post('/api/hr/employees/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 3)

    def test_leave_request_create_employee(self):
        """Test employee can create their own leave request."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.user)}')
        data = {
            'employee_id': self.employee.id,
            'start_date': '2025-09-01',
            'end_date': '2025-09-05',
            'reason': 'Vacation',
            'status': 'pending'
        }
        response = self.client.post('/api/hr/leaverequests/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LeaveRequest.objects.count(), 1)

    def test_leave_request_list_non_hr_employee(self):
        """Test non-HR employee only sees their own leave requests."""
        LeaveRequest.objects.create(
            employee=self.employee,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 5),
            reason='Vacation',
            status='pending'
        )
        LeaveRequest.objects.create(
            employee=self.hr_employee,
            start_date=date(2025, 9, 10),
            end_date=date(2025, 9, 12),
            reason='Sick Leave',
            status='pending'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.user)}')
        response = self.client.get('/api/hr/leaverequests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['employee'], str(self.employee))

    def test_leave_request_list_hr_user(self):
        """Test HR user sees all leave requests."""
        LeaveRequest.objects.create(
            employee=self.employee,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 5),
            reason='Vacation',
            status='pending'
        )
        LeaveRequest.objects.create(
            employee=self.hr_employee,
            start_date=date(2025, 9, 10),
            end_date=date(2025, 9, 12),
            reason='Sick Leave',
            status='pending'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.hr_user)}')
        response = self.client.get('/api/hr/leaverequests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_leave_request_update_non_owner(self):
        """Test non-owner employee cannot update another's leave request."""
        leave = LeaveRequest.objects.create(
            employee=self.hr_employee,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 5),
            reason='Vacation',
            status='pending'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.user)}')
        data = {'status': 'approved'}
        response = self.client.patch(f'/api/hr/leaverequests/{leave.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_leave_request_update_hr_user(self):
        """Test HR user can update any leave request."""
        leave = LeaveRequest.objects.create(
            employee=self.employee,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 5),
            reason='Vacation',
            status='pending'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.hr_user)}')
        data = {'status': 'approved'}
        response = self.client.patch(f'/api/hr/leaverequests/{leave.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leave.refresh_from_db()
        self.assertEqual(leave.status, 'approved')