from django.test import TestCase
from .models import UserProfile,Star,Athlete
from Query.models import Meet
from django.http import HttpRequest, HttpResponse
import json
from unittest import skipIf

from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from django.contrib.sessions.backends.db import SessionStore
# Create your tests here.


class UsersTest(TestCase):
    skip_tests = False

    def setUp(self):
        self.meet1 = Meet.objects.create(name="2023校运会", mid=1)
        self.meet2 = Meet.objects.create(name="2024马约翰杯", mid=2)
        self.admin = UserProfile.objects.create(username='admin_bjsh_test', password=make_password('222222', salt='L_1OhYGyQhoHS_6_'), Is_System_Admin=True)
        self.logintest = UserProfile.objects.create(username='test1', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'))
        self.modifytest = UserProfile.objects.create(username='test2', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'))
        self.profiletest = UserProfile.objects.create(username='profile_test', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'),email = 'test@123.com', org='test', Is_Department_Official=True, Is_Contest_Official=[1,2], Is_System_Admin=False)
        self.athlete1 = Athlete.objects.create(real_name='邹迦音')
        self.athlete2 = Athlete.objects.create(real_name='樊高凡')
        self.athlete3 = Athlete.objects.create(real_name='戎胤泽')
        self.athlete4 = Athlete.objects.create(real_name='陈柘宇')
        self.star1 = Star.objects.create(User=self.profiletest, Athlete=self.athlete1)
        self.star2 = Star.objects.create(User=self.profiletest, Athlete=self.athlete2)
        self.star3 = Star.objects.create(User=self.profiletest, Athlete=self.athlete3)
        self.passwordtest = UserProfile.objects.create(username='password_test', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'))
        data = {
            "username" : 'password_test',
            'password': '123456',
        }
        res = self.client.post('/users/login', data=data)
        global session_key
        session_key = json.loads(res.content.decode())['data']['session']
        data = {
            "username" : 'profile_test',
            'password': '123456',
        }
        res = self.client.post('/users/login', data=data)
        global session_key_email
        session_key_email = json.loads(res.content.decode())['data']['session']

    @skipIf(skip_tests, 'Skip tests')
    def test_register(self):
        data = {
            'username': 'test',
            'password': '123456',
        }
        res = self.client.post('/users/register', data=data)
        user = UserProfile.objects.filter(username='test')
        self.assertTrue(user.exists())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(user[0].username, 'test')

    @skipIf(skip_tests, 'Skip tests')
    def test_wrong_method(self):
        data = {
            'username': 'test',
            'password': '123456',
        }
        res = self.client.get('/users/register', data=data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(json.loads(res.content.decode())['code'], -3)
        self.assertEqual(json.loads(res.content.decode())['info'], 'Bad method')

    @skipIf(skip_tests, 'Skip tests')
    def test_wrong_param(self):
        data = {
            'username': 'test',
            'password': '123456',
            'extra_param': 'extra_value'
        }
        res = self.client.post('/users/register', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -1)
        self.assertEqual(json.loads(res.content.decode())['info'], '非法参数: {\'extra_param\'}')

    @skipIf(skip_tests, 'Skip tests')
    def test_lack_param(self):
        data = {
            'username': 'test',
        }
        res = self.client.post('/users/register', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -2)
        self.assertEqual(json.loads(res.content.decode())['info'], '请填写所有必填项')

    @skipIf(skip_tests, 'Skip tests')

    def test_register_wrong_password(self):
        data = {
            'username': 'test',
            'password': '123456……',
        }
        res = self.client.post('/users/register', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 4)
        self.assertEqual(json.loads(res.content.decode())['info'], '密码只能包含字母、数字、下划线')
    
    @skipIf(skip_tests, 'Skip tests')
    def test_register_wrong_username(self):
        data = {
            'username': 'test@123',
            'password': '123456',
        }
        res = self.client.post('/users/register', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 3)
        self.assertEqual(json.loads(res.content.decode())['info'], '用户名只能包含字母、数字、下划线')

    @skipIf(skip_tests, 'Skip tests')
    def test_register_short_password(self):
        data = {
            'username': '111',
            'password': 'aa'
        }
        res = self.client.post('/users/register', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 6)
        self.assertEqual(json.loads(res.content.decode())['info'], '密码长度不能超过16, 不能少于6')
    
    @skipIf(skip_tests, 'Skip tests')
    def test_register_long_password(self):
        data = {
            'username': '111',
            "password": '12345678901234567890'
        }
        res = self.client.post('/users/register', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 6)
        self.assertEqual(json.loads(res.content.decode())['info'], '密码长度不能超过16, 不能少于6')

    @skipIf(skip_tests, 'Skip tests')
    def test_register_long_username(self):
        data = {
            "username": "testtesttesttesttest",
            "password": "123456",
        }
        res = self.client.post('/users/register', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 5)
        self.assertEqual(json.loads(res.content.decode())['info'], '用户名长度不能超过15')
    
    @skipIf(skip_tests, 'Skip tests')
    def test_register_exist_username(self):
        data = {
            'username': 'test',
            'password': '123456',
        }
        res = self.client.post('/users/register', data=data)
        self.assertEqual(res.status_code, 200)
        res = self.client.post('/users/register', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 1)
        self.assertEqual(json.loads(res.content.decode())['info'], '用户名已存在')

    @skipIf(skip_tests, 'Skip tests')
    def test_login_right(self):
        data = {
            'username': 'test1',
            'password': '123456',
        }
        res = self.client.post('/users/login', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        self.assertEqual(json.loads(res.content.decode())['info'], 'Succeed')

    @skipIf(skip_tests, 'Skip tests')
    def test_login_wrong_method(self):
        data = {
            'username': 'test1',
            'password': '123456',
        }
        res = self.client.get('/users/login', data=data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(json.loads(res.content.decode())['code'], -3)
        self.assertEqual(json.loads(res.content.decode())['info'], 'Bad method')

    @skipIf(skip_tests, 'Skip tests')
    def test_login_wrong_param(self):
        data = {
            'username': 'test1',
            'password': '123456',
            'extra_param': 'extra_value'
        }
        res = self.client.post('/users/login', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -1)
        self.assertEqual(json.loads(res.content.decode())['info'], '非法参数: {\'extra_param\'}')

    @skipIf(skip_tests, 'Skip tests')
    def test_login_lack_param(self):
        data = {
            'username': 'test1',
        }
        res = self.client.post('/users/login', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -2)
        self.assertEqual(json.loads(res.content.decode())['info'], '请填写所有必填项')



            

    @skipIf(skip_tests, 'Skip tests')
    def test_login_unregistered(self):
        data = {
            'username': "111",
            'password': "aa",
        }
        res = self.client.post('/users/login', data=data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(json.loads(res.content.decode())['code'], -1)
        self.assertEqual(json.loads(res.content.decode())['info'], '用户名不存在')

    @skipIf(skip_tests, 'Skip tests')
    def test_login_wrong_password(self):
        data = {
            'username': 'test1',
            'password': '1234567',
        }
        res = self.client.post('/users/login', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 2)
        self.assertEqual(json.loads(res.content.decode())['info'], '用户名或密码错误')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }
        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(json.loads(res2.content.decode())['code'], 0)
        self.assertEqual(json.loads(res2.content.decode())['info'], 'Succeed')
        user = UserProfile.objects.filter(username='test2')
        self.assertTrue(user.exists())
        self.assertTrue(user[0].Is_Department_Official)
        self.assertFalse(user[0].Is_Contest_Official)
        self.assertFalse(user[0].Is_System_Admin)

    

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_wrong_method(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.get('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 405)
        self.assertEqual(json.loads(res2.content.decode())['code'], -3)
        self.assertEqual(json.loads(res2.content.decode())['info'], 'Bad method')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_wrong_param(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
            "extra_param": "extra_value",
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(json.loads(res2.content.decode())['code'], -1)
        self.assertEqual(json.loads(res2.content.decode())['info'], '非法参数: {\'extra_param\'}')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_lack_param(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(json.loads(res2.content.decode())['code'], -2)
        self.assertEqual(json.loads(res2.content.decode())['info'], '请填写所有必填项')
    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_lack_param_2(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }
        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(json.loads(res2.content.decode())['code'], -2)
        self.assertEqual(json.loads(res2.content.decode())['info'], '请填写所有必填项')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_session_unexisted(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = "1"
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 404)
        self.assertEqual(json.loads(res2.content.decode())['code'], -2)
        self.assertEqual(json.loads(res2.content.decode())['info'], 'session不存在')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_expired_session(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        session = Session.objects.get(session_key=session_key)
        session.expire_date = timezone.now() - timedelta(days=1)
        session.save()
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(json.loads(res2.content.decode())['code'], -6)
        self.assertEqual(json.loads(res2.content.decode())['info'], '会话已过期')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_illegal_session(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        # session = Session.objects.get(session_key=session_key)
        session = SessionStore(session_key=session_key)
        session['id'] = None
        session.save()
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(json.loads(res2.content.decode())['code'], -5)
        self.assertEqual(json.loads(res2.content.decode())['info'], '非法session')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_user_admin_unexisted(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        # session = Session.objects.get(session_key=session_key)
        session = SessionStore(session_key=session_key)
        session["id"] = 0
        session.save()
        data2 = {
            "session": session_key,
            "user_to_modify": "admin_bjsh_test",
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 404)
        self.assertEqual(json.loads(res2.content.decode())['code'], -1)
        self.assertEqual(json.loads(res2.content.decode())['info'], '请求用户不存在')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_user_admin_not_admin(self):
        data = {
            'username': 'test1',
            'password': '123456', 
        }
        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 401)
        self.assertEqual(json.loads(res2.content.decode())['code'], -3)
        self.assertEqual(json.loads(res2.content.decode())['info'], '权限不足')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_user_modify_unexisted(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "user_to_modify": "test",
            "Is_Department_Official": True,
            "Is_Contest_Official": [],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 404)
        self.assertEqual(json.loads(res2.content.decode())['code'], 2)
        self.assertEqual(json.loads(res2.content.decode())['info'], '被修改用户不存在')
    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_right_contest(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": False,
            "Is_Contest_Official": [1,2],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(json.loads(res2.content.decode())['code'], 0)
        self.assertEqual(json.loads(res2.content.decode())['info'], 'Succeed')
        user = UserProfile.objects.filter(username='test2')
        self.assertTrue(user.exists())
        self.assertEqual(user[0].Is_Contest_Official, [1,2])
    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_unexisted_contest(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": False,
            "Is_Contest_Official": [82],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 404)
        self.assertEqual(json.loads(res2.content.decode())['code'], 8)
    @skipIf(skip_tests, 'Skip tests')
    def test_modify_user_status_wrong_contest(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
        }

        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "user_to_modify": "test2",
            "Is_Department_Official": False,
            "Is_Contest_Official":["wrong_contest"],
            "Is_System_Admin": False,
        }
        res2 = self.client.post('/users/modify_user_status', data=data2)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(json.loads(res2.content.decode())['code'], 7)
    @skipIf(skip_tests, 'Skip tests')
    def test_get_user_status(self):
        data = {
            'username': 'admin_bjsh_test',
        }
        res2 = self.client.get('/users/get_user_status', data=data)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(json.loads(res2.content.decode())['code'], 0)
        self.assertEqual(json.loads(res2.content.decode())['info'], 'Succeed')

    @skipIf(skip_tests, 'Skip tests')
    def test_get_user_status_wrong_method(self):
        data = {
            'username': 'admin_bjsh_test',
        }
        res2 = self.client.post('/users/get_user_status', data=data)
        self.assertEqual(res2.status_code, 405)
        self.assertEqual(json.loads(res2.content.decode())['code'], -3)
        self.assertEqual(json.loads(res2.content.decode())['info'], 'Bad method')

    @skipIf(skip_tests, 'Skip tests')
    def test_get_user_status_wrong_param(self):
        data = {
            'username': 'admin_bjsh_test',
            'password': '222222',
            }
        res2 = self.client.get('/users/get_user_status', data=data)
        self.assertEqual(res2.status_code, 400)

    @skipIf(skip_tests, 'Skip tests')
    def test_get_user_status_unexisted_user(self):
        data = {
            'username': 'test3',
        }
        res2 = self.client.get('/users/get_user_status', data=data)
        self.assertEqual(res2.status_code, 404)
        self.assertEqual(json.loads(res2.content.decode())['code'], 2)
        self.assertEqual(json.loads(res2.content.decode())['info'], '用户不存在')

    @skipIf(skip_tests, 'Skip tests')
    def test_get_user_status_lack_param(self):
        data = {}
        res2 = self.client.get('/users/get_user_status', data=data)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(json.loads(res2.content.decode())['code'], -2)

    @skipIf(skip_tests, 'Skip tests')
    def test_get_user_profile(self):
        data = {
            'username': 'profile_test',
            'password': '123456',
        }
        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
        }
        res2 = self.client.get('/users/get_user_profile', data=data2)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(json.loads(res2.content.decode())['code'], 0)
        self.assertEqual(json.loads(res2.content.decode())['info'], 'Succeed')
        self.assertEqual(json.loads(res2.content.decode())['data']['username'], 'profile_test')

    @skipIf(skip_tests, 'Skip tests')
    def test_get_user_profile_2(self):
        data = {
            'username': 'test2',
            'password': '123456',
        }
        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
        }
        res2 = self.client.get('/users/get_user_profile', data=data2)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(json.loads(res2.content.decode())['code'], 0)
        self.assertEqual(json.loads(res2.content.decode())['info'], 'Succeed')

    @skipIf(skip_tests, 'Skip tests')
    def test_get_user_profile_wrong_param(self):
        data = {
            'username': 'profile_test',
            'password': '123456',
        }
        res = self.client.post('/users/login', data=data)
        session_key = json.loads(res.content.decode())['data']['session']
        data2 = {
            "session": session_key,
            "extra_param": "extra_value",
        }
        res2 = self.client.get('/users/get_user_profile', data=data2)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(json.loads(res2.content.decode())['code'], -1)

    #---modify_password---
    @skipIf(skip_tests, 'Skip tests')
    def test_modify_password_right(self):
        data = {
            'session': session_key,
            'password': '123457',
        }
        res = self.client.post('/users/modify_password', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        data2 = {
            'username': 'profile_test',
            'password': '123457',
        }
        res2 = self.client.post('/users/login', data=data2)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(json.loads(res2.content.decode())['code'], 0)
        self.assertEqual(json.loads(res2.content.decode())['info'], 'Succeed')
        

    
    @skipIf(skip_tests, 'Skip tests')
    def test_modify_password_wrong_param(self):
        data = {
            'session': session_key,
            'extra_param': 'extra_value'
        }
        res = self.client.post('/users/modify_password', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -1)
        self.assertEqual(json.loads(res.content.decode())['info'], 'Invalid parameter: {\'extra_param\'}')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_password_lack_param(self):
        data = {
            'session': session_key,
        }
        res = self.client.post('/users/modify_password', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -2)

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_password_wrong_password(self):
        data = {
            'session': session_key,
            'password': '123456……',
        }
        res = self.client.post('/users/modify_password', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 4)
        self.assertEqual(json.loads(res.content.decode())['info'], '密码只能包含字母、数字、下划线')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_password_short_password(self):
        data = {
            'session': session_key,
            'password': 'aa'
        }
        res = self.client.post('/users/modify_password', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 6)
        self.assertEqual(json.loads(res.content.decode())['info'], '密码长度不能超过16, 不能少于6')
    
    @skipIf(skip_tests, 'Skip tests')
    def test_modify_password_long_password(self):
        data = {
            'session': session_key,
            "password": '12345678901234567890'
        }
        res = self.client.post('/users/modify_password', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 6)
        self.assertEqual(json.loads(res.content.decode())['info'], '密码长度不能超过16, 不能少于6')

    #---modify_email---
    @skipIf(skip_tests, 'Skip tests')
    def test_modify_email_right(self):
        data = {
            'session': session_key_email,
             'email': 'new_email@bjsh.com'
        }
        res = self.client.post('/users/modify_user_profile', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        user = UserProfile.objects.filter(username='profile_test')
        user = user[0]
        self.assertEqual(user.email, 'new_email@bjsh.com')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_email_wrong_param(self):
        data = {
            'session': session_key_email,
            'extra_param': 'extra_value'
        }
        res = self.client.post('/users/modify_user_profile', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -1)
        self.assertEqual(json.loads(res.content.decode())['info'], 'Invalid parameter: {\'extra_param\'}')

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_email_lack_param(self):
        data = {
            'session': session_key_email,
        }
        res = self.client.post('/users/modify_user_profile', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -2)

    @skipIf(skip_tests, 'Skip tests')
    def test_modify_email_wrong_email(self):
        data = {
            'session': session_key_email,
             'email': 'new_email@bjsh'
        }
        res = self.client.post('/users/modify_user_profile', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 9)
        self.assertEqual(json.loads(res.content.decode())['info'], '请填写正确的邮箱')
    
    #---modify_star---
    @skipIf(skip_tests, 'Skip tests')
    def test_modify_star_add_right(self):
        data = {
            'session': session_key_email,
            'athlete_name': '陈柘宇',
        }
        res = self.client.post('/users/add_star', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        user = UserProfile.objects.filter(username='profile_test')
        user = user[0]
        star_list = [star.Athlete.real_name for star in Star.objects.filter(User=user)]
        set_star = set(star_list)
        set_star2 = set(['邹迦音', '樊高凡', '戎胤泽', '陈柘宇'])
        self.assertEqual(set_star, set_star2)

    @skipIf(skip_tests, 'Skip tests')
    def test_add_star_add_wrong_param(self):
        data = {
            'session': session_key_email,
            'athlete_name': '陈柘宇',
            'extra_param': 'extra_value'
        }
        res = self.client.post('/users/add_star', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -1)
        self.assertEqual(json.loads(res.content.decode())['info'], 'Invalid parameter: {\'extra_param\'}')

    @skipIf(skip_tests, 'Skip tests')
    def test_add_star_add_lack_param(self):
        data = {
            'session': session_key_email,
        }
        res = self.client.post('/users/add_star', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -2)

    @skipIf(skip_tests, 'Skip tests')
    def test_add_star_add_wrong_athlete(self):
        data = {
            'session': session_key_email,
            'athlete_name': 'wrong_athlete'
        }
        res = self.client.post('/users/add_star', data=data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(json.loads(res.content.decode())['code'], 2)

    @skipIf(skip_tests, 'Skip tests')
    def test_add_star_add_existed_athlete(self):
        data = {
            'session': session_key_email,
            'athlete_name': '邹迦音',
        }
        res = self.client.post('/users/add_star', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 3)

    @skipIf(skip_tests, 'Skip tests')
    def test_add_star_delete_right(self):
        data = {
            'session': session_key_email,
            'athlete_name': '陈柘宇',
        }
        res = self.client.post('/users/add_star', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        data = {
            'session': session_key_email,
            'athlete_name': '陈柘宇',
        }
        res = self.client.post('/users/delete_star', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        user = UserProfile.objects.filter(username='profile_test')
        user = user[0]
        star_list = [star.Athlete.real_name for star in Star.objects.filter(User=user)]
        set_star = set(star_list)
        set_star2 = set(['邹迦音', '樊高凡', '戎胤泽'])
        self.assertEqual(set_star, set_star2)

    @skipIf(skip_tests, 'Skip tests')
    def test_delete_star_delete_wrong_param(self):
        data = {
            'session': session_key_email,
            'athlete_name': '陈柘宇',
            'extra_param': 'extra_value'
        }
        res = self.client.post('/users/delete_star', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -1)
        self.assertEqual(json.loads(res.content.decode())['info'], 'Invalid parameter: {\'extra_param\'}')

    @skipIf(skip_tests, 'Skip tests')
    def test_delete_star_delete_lack_param(self):
        data = {
            'session': session_key_email,
        }
        res = self.client.post('/users/delete_star', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -2)

    @skipIf(skip_tests, 'Skip tests')
    def test_delete_star_delete_wrong_athlete(self):
        data = {
            'session': session_key_email,
            'athlete_name': 'wrong_athlete'
        }
        res = self.client.post('/users/delete_star', data=data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(json.loads(res.content.decode())['code'], 2)

    @skipIf(skip_tests, 'Skip tests')
    def test_delete_star_delete_not_exist(self):
        data = {
            'session': session_key_email,
            'athlete_name': '陈柘宇',
        }
        res = self.client.post('/users/delete_star', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 4)