from django.test import TestCase, Client
from .models import AuthRequest
from Users.models import UserProfile,Star,Athlete
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


class MessagesTest(TestCase):
    skip_tests = False

    def setUp(self):
        self.apply_test = UserProfile.objects.create(username='apply_test', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'))
        self.apply_test2 = UserProfile.objects.create(username='apply_test2', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'), email="fgf22@pku.edu.cn")
        self.apply_test3 = UserProfile.objects.create(username='apply_test3', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'))
        self.tigan = UserProfile.objects.create(username='tigan', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'),Is_Department_Official=True)
        self.admin = UserProfile.objects.create(username='admin', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'),Is_System_Admin=True)
        self.sender_to_delete = UserProfile.objects.create(username='sender_to_d', password=make_password('123456', salt='L_1OhYGyQhoHS_6_'))

        self.athlete1 = Athlete.objects.create(real_name='邹迦音')
        self.athlete2 = Athlete.objects.create(real_name='樊高凡')
        self.athlete3 = Athlete.objects.create(real_name='戎胤泽')
        self.athlete4 = Athlete.objects.create(User = self.apply_test3,real_name='陈柘宇')
        self.athlete_to_delete = Athlete.objects.create(real_name='马平川')

        self.message1 = AuthRequest.objects.create(Athlete=self.athlete1, sender=self.apply_test2, invited_reviewer=self.tigan, status=AuthRequest.STATUS_PENDING)
        self.message2 = AuthRequest.objects.create(Athlete=self.athlete2, sender=self.apply_test2, invited_reviewer=self.admin, status=AuthRequest.STATUS_REJECTED, reject_reason='测试拒绝理由',replied_at=timezone.now())
        self.message3 = AuthRequest.objects.create(Athlete=self.athlete3, sender=self.apply_test2, invited_reviewer=self.tigan, status=AuthRequest.STATUS_APPROVED,replied_at=timezone.now())
        self.message4 = AuthRequest.objects.create(Athlete=self.athlete4, sender=self.apply_test2, invited_reviewer=self.tigan, status=AuthRequest.STATUS_PENDING)
        self.message_not_tigan = AuthRequest.objects.create(Athlete=self.athlete2, sender=self.apply_test2, invited_reviewer=self.admin, status=AuthRequest.STATUS_PENDING)
        self.message6 = AuthRequest.objects.create(Athlete=self.athlete2, sender=self.apply_test2, invited_reviewer=self.tigan, status=AuthRequest.STATUS_PENDING)
        self.message7 = AuthRequest.objects.create(Athlete=self.athlete2, sender=self.apply_test2, invited_reviewer=self.tigan, status=AuthRequest.STATUS_PENDING)
        
        self.message_no_sender = AuthRequest.objects.create(sender=self.sender_to_delete, Athlete=self.athlete2, invited_reviewer=self.tigan, status=AuthRequest.STATUS_PENDING)
        self.message_no_athlete = AuthRequest.objects.create(sender=self.apply_test,Athlete=self.athlete_to_delete, invited_reviewer=self.tigan, status=AuthRequest.STATUS_PENDING)
        self.sender_to_delete.delete()
        self.athlete_to_delete.delete()

        self.message_user_has_athlete = AuthRequest.objects.create(Athlete=self.athlete2, sender=self.apply_test3, invited_reviewer=self.tigan, status=AuthRequest.STATUS_PENDING)
        self.message_athlete_has_user = AuthRequest.objects.create(Athlete=self.athlete4, sender=self.apply_test, invited_reviewer=self.tigan, status=AuthRequest.STATUS_PENDING)
        
        data_apply = {
            "username" : 'apply_test',
            'password': '123456',
        }
        res_apply = self.client.post('/users/login', data=data_apply)
        global session_key_apply
        session_key_apply = json.loads(res_apply.content.decode())['data']['session']
        #session_key_tigan
        self.client_tigan = Client()
        data_tigan = {
            "username" : 'tigan',
            'password': '123456',
        }
        res_tigan = self.client_tigan.post('/users/login', data=data_tigan)
        global session_key_tigan
        session_key_tigan = json.loads(res_tigan.content.decode())['data']['session']



    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth(self):
        data = {
            'session':session_key_apply,
            'real_name': '邹迦音',
            'invited_reviewer': 'tigan',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(AuthRequest.objects.count(), 10)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth2(self):
        data = {
            'session':session_key_apply,
            'real_name': '樊高凡',
            'invited_reviewer': 'admin',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(AuthRequest.objects.count(), 10)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth_invalid_params(self):
        data = {
            'session':session_key_apply,
            'real_name': '邹迦音',
            'invited_reviewer': 'tigan',
            'invalid_param': 'invalid_value',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -1)
        self.assertEqual(AuthRequest.objects.count(), 9)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth_lack_invited_reviewer(self):
        data = {
            'session':session_key_apply,
            'real_name': '邹迦音',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -2)
        self.assertEqual(AuthRequest.objects.count(), 9)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth_lack_real_name(self):
        data = {
            'session':session_key_apply,
            'invited_reviewer': 'tigan',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -2)
        self.assertEqual(AuthRequest.objects.count(), 9)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth_athlete_unexist(self):
        data = {
            'session':session_key_apply,
            'real_name': '张三',
            'invited_reviewer': 'tigan',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(json.loads(res.content.decode())['code'], 3)
        self.assertEqual(AuthRequest.objects.count(), 9)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth_reviewer_unexist(self):
        data = {
            'session':session_key_apply,
            'real_name': '邹迦音',
            'invited_reviewer': 'tigan2',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(json.loads(res.content.decode())['code'], 4)
        self.assertEqual(AuthRequest.objects.count(), 9)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth_reviewer_not_official(self):
        data = {
            'session':session_key_apply,
            'real_name': '邹迦音',
            'invited_reviewer': 'apply_test2',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(json.loads(res.content.decode())['code'], 5)
        self.assertEqual(AuthRequest.objects.count(), 9)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth_sender_has_athlete(self):
        data_apply3 = {
            "username" : 'apply_test3',
            'password': '123456',
        }
        res_apply3 = self.client.post('/users/login', data=data_apply3)
        session_key_apply3 = json.loads(res_apply3.content.decode())['data']['session']
        data = {
            'session':session_key_apply3,
            'real_name': '邹迦音',
            'invited_reviewer': 'tigan',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 6)
        self.assertEqual(json.loads(res.content.decode())['info'], '您已经绑定了：陈柘宇')
        self.assertEqual(AuthRequest.objects.count(), 9)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth_athlete_has_user(self):
        data = {
            'session':session_key_apply,
            'real_name': '陈柘宇',
            'invited_reviewer': 'tigan',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 7)
        self.assertEqual(AuthRequest.objects.count(), 9)

    @skipIf(skip_tests, 'Skip tests')
    def test_apply_auth_pending_over_limit(self):
        data_apply2 = {
            "username" : 'apply_test2',
            'password': '123456',
        }
        res_apply2 = self.client.post('/users/login', data=data_apply2)
        session_key_apply2 = json.loads(res_apply2.content.decode())['data']['session']
        data = {
            'session':session_key_apply2,
            'real_name': '邹迦音',
            'invited_reviewer': 'tigan',
        }
        res = self.client.post('/message/apply_auth', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 8)
        self.assertEqual(AuthRequest.objects.count(), 9)

    @skipIf(skip_tests, 'Skip tests')
    def test_get_auth_requests(self):
        data_apply2 = {
            "username" : 'apply_test2',
            'password': '123456',
        }
        res_apply2 = self.client.post('/users/login', data=data_apply2)
        session_key_apply2 = json.loads(res_apply2.content.decode())['data']['session']
        data = {
            'session':session_key_apply2,
        }
        res = self.client.get('/message/get_auth_sent', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)


    #---Authenticate---#

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_pending2accept(self):
        data = {
            'session':session_key_tigan,
            'message_id':self.message6.id,
            'status':1,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        self.assertEqual(AuthRequest.objects.get(id=self.message6.id).status, 1)
        self.athlete2.refresh_from_db()
        self.assertEqual(self.athlete2.User, self.apply_test2)
        data = {
            'name':self.athlete2.real_name,
        }
        res = self.client_tigan.get('/query_personal_web', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        self.assertEqual(json.loads(res.content.decode())['username'], self.apply_test2.username)
        self.assertEqual(json.loads(res.content.decode())['email'], self.apply_test2.email)


    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_pending2reject(self):
        data = {
            'session':session_key_tigan,
            'message_id':self.message7.id,
            'status':2,
            'reject_reason':'测试拒绝理由',
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        self.assertEqual(AuthRequest.objects.get(id=self.message7.id).status, 2)
        self.assertEqual(AuthRequest.objects.get(id=self.message7.id).reject_reason, '测试拒绝理由')
    
    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_invalid_params(self):
        data = {
            'session':session_key_tigan,
            'message_id':self.message6.id,
            'status':1,
            'invalid_param': 'invalid_value',
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -1)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_invalid_message_id_type(self):
        data = {
            'session':session_key_tigan,
            'message_id':"invalid_message_id",
            'status':1,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], -2)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_message_unexist(self):
        data = {
            'session':session_key_tigan,
            'message_id':9999,
            'status':1,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(json.loads(res.content.decode())['code'], 1)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_sender_unexist(self):
        data = {
            'session':session_key_tigan,
            'message_id':self.message_no_sender.id,
            'status':1,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(json.loads(res.content.decode())['code'], 1)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_athlete_unexist(self):
        data = {
            'session':session_key_tigan,
            'message_id':self.message_no_athlete.id,
            'status':1,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(json.loads(res.content.decode())['code'], 1)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_reviewer_not_invited(self):
        data = {
            'session':session_key_tigan,
            'message_id':self.message_not_tigan.id,
            'status':1,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(json.loads(res.content.decode())['code'], 4)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_reviewer_not_official(self):
        data = {
            'session':session_key_apply,
            'message_id':self.message6.id,
            'status':1,
        }
        res = self.client.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(json.loads(res.content.decode())['code'], 5)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_user_has_athlete(self):
        data = {
            'session':session_key_tigan,
            'message_id':self.message_user_has_athlete.id,
            'status':1,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 6)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_athlete_has_user(self):
        data = {
            'session':session_key_tigan,
           'message_id':self.message_athlete_has_user.id,
           'status':1,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 7)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_status_unexist(self):
        data = {
            'session':session_key_tigan,
            'message_id':self.message6.id,
            'status':3,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 8)

    @skipIf(skip_tests, 'Skip tests')
    def test_authenticate_reject_reason_too_long(self):
        data = {
            'session':session_key_tigan,
            'message_id':self.message6.id,
            'status':2,
            'reject_reason':'a'*301,
        }
        res = self.client_tigan.post('/message/authenticate', data=data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.content.decode())['code'], 9)

    #---Get Auth Received---#
    @skipIf(skip_tests, 'Skip tests')
    def  test_get_auth_received(self):
        data = {
            'session':session_key_tigan,
        }
        res = self.client_tigan.get('/message/get_auth_received', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        self.assertEqual(len(json.loads(res.content.decode())['data']["auth_requests"]), 7)

    @skipIf(skip_tests, 'Skip tests')
    def  test_get_auth_received_no_auth_requests(self):
        data = {
            'session':session_key_apply,
        }
        res = self.client.get('/message/get_auth_received', data=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode())['code'], 0)
        self.assertEqual(len(json.loads(res.content.decode())['data']["auth_requests"]), 0)
# Create your tests here.
