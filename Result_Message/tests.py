from django.test import TestCase, Client
from .models import ResultRequest
from Users.models import UserProfile, Star, Athlete
from Query.models import Meet, Project, Result
from django.http import HttpRequest, HttpResponse
import json
from unittest import skipIf
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.sessions.backends.db import SessionStore

# Create your tests here.


class FeedbackViewsTest(TestCase):
    def setUp(self):
        # 创建测试用户
        self.sender = UserProfile.objects.create(
            username="tigan",
            password=make_password("123456", salt="L_1OhYGyQhoHS_6_"),
            Is_Department_Official=True,
        )
        self.admin = UserProfile.objects.create(
            username="admin",
            password=make_password("123456", salt="L_1OhYGyQhoHS_6_"),
            Is_System_Admin=True,
        )
        self.unauthorized_user = UserProfile.objects.create(
            username="normal", password=make_password("123456", salt="L_1OhYGyQhoHS_6_")
        )
        # 创建测试赛事
        self.meet = Meet.objects.create(name="Test Meet", mid=1)
        self.contest_official = UserProfile.objects.create(
            username="contest",
            password=make_password("123456", salt="L_1OhYGyQhoHS_6_"),
            Is_Contest_Official=[self.meet.mid],
        )

        self.project = Project.objects.create(
            contest=self.meet,
            name="Test Project",
            leixing="TypeA",
            zubie="U20",
            xingbie="Male",
        )

        # 创建测试成绩
        self.result = Result.objects.create(
            project=self.project,
            result_type="group",
            name="Test Result",
            result="17:24.95",
            groupname="GroupA",
        )

        # 登录测试用户
        data_apply = {
            "username": "admin",
            "password": "123456",
        }
        res_admin = self.client.post("/users/login", data=data_apply)
        global session_key_admin
        session_key_admin = json.loads(res_admin.content.decode())["data"]["session"]
        # session_key_tigan
        self.client_tigan = Client()
        data_tigan = {
            "username": "tigan",
            "password": "123456",
        }
        res_tigan = self.client_tigan.post("/users/login", data=data_tigan)
        global session_key_tigan
        session_key_tigan = json.loads(res_tigan.content.decode())["data"]["session"]
        self.client_contest = Client()
        data_contest_official = {
            "username": "contest",
            "password": "123456",
        }
        res_contest_official = self.client_contest.post(
            "/users/login", data=data_contest_official
        )
        global session_key_contest
        session_key_contest = json.loads(res_contest_official.content.decode())["data"][
            "session"
        ]

    # ------------------------- feedback 视图测试 -------------------------
    def test_feedback_success(self):
        """测试正常提交反馈"""
        data = {
            "session": session_key_tigan,
            "result_id": self.result.id,
            "applyreason": "Valid reason",
        }
        response = self.client.post(
            "/result_message/feedback",
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ResultRequest.objects.exists())

    def test_feedback_invalid_params(self):
        """测试非法参数"""
        data = {"session": session_key_tigan, "invalid_param": "value"}
        response = self.client.post(
            "/result_message/feedback",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(json.loads(response.content.decode())["code"], -1)
        self.assertEqual(response.status_code, 400)

    def test_feedback_permission_denied(self):
        """测试无权限用户提交"""
        data = {
            "username": "normal",
            "password": "123456",
        }
        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        session_key = content["session"]
        data = {
            "result_id": self.result.id,
            "applyreason": "Test reason",
            "session": session_key,
        }
        response = self.client.post(
            "/result_message/feedback",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(json.loads(response.content.decode())["code"], -3)
        self.assertEqual(response.status_code, 401)

    def test_feedback_result_not_exist(self):
        """测试不存在的成绩"""
        data = {
            "result_id": 999,
            "session": session_key_tigan,
            "applyreason": "Test reason",
        }
        response = self.client.post(
            "/result_message/feedback",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(json.loads(response.content.decode())["code"], 3)

        # self.assertEqual(response.json()["code"], 3)
        self.assertEqual(response.status_code, 404)

    def test_feedback_reason_too_long(self):
        """测试超长申请理由"""
        data = {
            "result_id": self.result.id,
            "session": session_key_tigan,
            "applyreason": "A" * 301,
        }
        response = self.client.post(
            "/result_message/feedback",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(json.loads(response.content.decode())["code"], 5)

        # self.assertEqual(response.json()["code"], 5)
        self.assertEqual(response.status_code, 400)

    # ------------------------- reply_feedback 视图测试 -------------------------
    def create_test_request(self):
        """创建测试反馈请求"""
        return ResultRequest.objects.create(
            sender=self.sender, result=self.result, apply_reason="Test reason"
        )

    def test_approve_feedback(self):
        """测试批准反馈"""
        request = self.create_test_request()
        data = {
            "id": request.id,
            "approval": "True",
            "session": session_key_contest,
        }

        response = self.client.post(
            "/result_message/reply_feedback",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        updated_request = ResultRequest.objects.get(id=request.id)
        self.assertEqual(updated_request.status, ResultRequest.STATUS_APPROVED)
        self.assertIsNotNone(updated_request.replied_at)

    def test_reject_feedback(self):
        """测试拒绝反馈"""
        request = self.create_test_request()
        data = {
            "id": request.id,
            "approval": "False",
            "reject_reason": "Test rejection",
            "session": session_key_contest,
        }
        response = self.client.post(
            "/result_message/reply_feedback",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        updated_request = ResultRequest.objects.get(id=request.id)
        self.assertEqual(updated_request.status, ResultRequest.STATUS_REJECTED)
        self.assertEqual(updated_request.reject_reason, "Test rejection")

    def test_reply_invalid_approval(self):
        """测试非法审批值"""
        request = self.create_test_request()
        data = {
            "id": request.id,
            "approval": "Invalid",
            "session": session_key_contest,
        }

        response = self.client.post(
            "/result_message/reply_feedback",
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], -2)

    # ------------------------- get_feedback_sent 视图测试 -------------------------
    def test_get_sent_feedback(self):
        """测试获取已发送反馈"""
        self.create_test_request()
        url = "/result_message/get_feedback_sent"
        data = {"session": session_key_tigan}
        response = self.client.get(url, data=data)

        data = json.loads(response.content.decode())
        self.assertEqual(len(data["feedback_requests"]), 1)
        self.assertEqual(data["feedback_requests"][0]["projectname"], "Test Project")

    # ------------------------- get_feedback_received 视图测试 -------------------------
    def test_get_received_received(self):
        """测试获取接收的反馈"""
        self.create_test_request()
        url = "/result_message/get_feedback_received"
        data = {"session": session_key_contest}
        response = self.client.get(url, data=data)
        data = json.loads(response.content.decode())
        self.assertEqual(len(data["feedback_requests"]), 1)
        self.assertEqual(data["feedback_requests"][0]["sender"], "tigan")

    def test_get_received_no_permission(self):
        """测试无权限用户获取反馈"""
        self.create_test_request()
        url = "/result_message/get_feedback_received"
        data = {"session": session_key_tigan}
        response = self.client.get(url, data=data)
        data = json.loads(response.content.decode())
        self.assertEqual(len(data["feedback_requests"]), 0)
