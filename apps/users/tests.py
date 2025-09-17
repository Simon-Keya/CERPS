from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(login_id='admin01', password='AdminPass123!')
        self.student = User.objects.create_user(login_id='ADM123', password='StdPass123!', is_student=True)
        self.staff = User.objects.create_user(login_id='EMP456', password='StaffPass123!', is_faculty=True)

    def test_login_with_admission_number(self):
        res = self.client.post(reverse('token_obtain_pair'), {'login_id': 'ADM123', 'password': 'StdPass123!'})
        self.assertEqual(res.status_code, 200)
        self.assertIn('access', res.data)

    def test_login_with_staff_number(self):
        res = self.client.post(reverse('token_obtain_pair'), {'login_id': 'EMP456', 'password': 'StaffPass123!'})
        self.assertEqual(res.status_code, 200)

    def test_me_endpoint(self):
        res = self.client.post(reverse('token_obtain_pair'), {'login_id': 'EMP456', 'password': 'StaffPass123!'})
        token = res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.get('/api/auth/users/me/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['login_id'], 'EMP456')

    def test_change_password(self):
        res = self.client.post(reverse('token_obtain_pair'), {'login_id': 'ADM123', 'password': 'StdPass123!'})
        token = res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res = self.client.post('/api/auth/users/change_password/', {'old_password': 'StdPass123!', 'new_password': 'NewPwd123!'})
        self.assertEqual(res.status_code, 200)
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password('NewPwd123!'))
