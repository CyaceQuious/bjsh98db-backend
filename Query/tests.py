from django.test import TestCase, Client
from django.http import HttpRequest, HttpResponse
import json
from unittest import skipIf

import os
import django
from django.urls import reverse
from Query.models import Meet, Project, Result
from Users.models import UserProfile, Athlete, Star
from django.contrib.auth.hashers import make_password


class QueryAPITestCase(TestCase):
    skip_tests = False

    def setUp(self):
        # 创建测试赛事
        self.meet1 = Meet.objects.create(name="2023校运会", mid=1)
        self.meet2 = Meet.objects.create(name="2024马约翰杯", mid=2)
        self.admin = UserProfile.objects.create(
            username="admin_bjsh_test",
            password=make_password("222222", salt="L_1OhYGyQhoHS_6_"),
            Is_System_Admin=True,
        )

        # 创建测试项目
        self.project1 = Project.objects.create(
            contest=self.meet1,
            leixing="决赛",
            xingbie="男子",
            zubie="甲组",
            name="100米",
        )
        self.project2 = Project.objects.create(
            contest=self.meet2,
            leixing="决赛",
            xingbie="女子",
            zubie="乙组",
            name="跳高",
        )
        self.project3 = Project.objects.create(
            contest=self.meet2,
            leixing="决赛",
            xingbie="混合",
            zubie="乙组",
            name="4x400米接力",
        )
        self.result1 = Result.objects.create(
            project=self.project1,
            name="张三",
            groupname="计算机系",
            result="00:11.23",
            score=9,
            rank=1,
            result_type="top8",
        )
        self.result2 = (
            Result.objects.create(
                project=self.project1,
                name="李四",
                groupname="电子系",
                result="00:11.45",
                score=7,
                rank=2,
                result_type="top8",
            ),
        )
        self.result3 = Result.objects.create(
            project=self.project2,
            name="王五",
            groupname="计算机系",
            result="1.75",
            rank=3,
            score=5,
            result_type="top8",
        )
        self.result4 = Result.objects.create(
            project=self.project2,
            name="赵六",
            groupname="电子系",
            result="1.80",
            rank=6,
            score=10,
            result_type="top8",
        )
        self.result5 = Result.objects.create(
            project=self.project2,
            name="邹迦音",
            groupname="计算机系",
            result="1.75",
            rank=4,
            score=8,
            result_type="top8",
        )
        self.result6 = Result.objects.create(
            project=self.project3,
            name="樊高凡",
            groupname="计算机系",
            result="03:40.23",
            rank=1,
            score=10,
            result_type="top8",
        )
        self.result7 = Result.objects.create(
            project=self.project3,
            name="戎胤泽",
            groupname="计算机系",
            result="03:45.23",
            rank=2,
            score=8,
            result_type="top8",
        )
        self.result8 = Result.objects.create(
            project=self.project3,
            name="张三",
            groupname="计算机系",
            result="03:50.23",
            rank=3,
            score=9,
            result_type="top8",
        )
        self.profiletest = UserProfile.objects.create(
            username="profile_test",
            password=make_password("123456", salt="L_1OhYGyQhoHS_6_"),
            email="test@123.com",
            org="test",
            Is_Department_Official=True,
            Is_Contest_Official=[1, 2],
            Is_System_Admin=False,
        )
        self.athlete1 = Athlete.objects.create(real_name="邹迦音")
        self.athlete2 = Athlete.objects.create(real_name="樊高凡")
        self.athlete3 = Athlete.objects.create(real_name="戎胤泽")
        self.star1 = Star.objects.create(User=self.profiletest, Athlete=self.athlete1)
        self.star2 = Star.objects.create(User=self.profiletest, Athlete=self.athlete2)
        self.star3 = Star.objects.create(User=self.profiletest, Athlete=self.athlete3)
        data = {
            "username": "profile_test",
            "password": "123456",
        }
        res = self.client.post("/users/login", data=data)
        global session_key
        session_key = json.loads(res.content.decode())["data"]["session"]

    # ---------------------- query_meet_list 测试 ----------------------
    @skipIf(skip_tests, "Skip tests")
    def test_query_meet_list_success(self):
        url = reverse("query_meet_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["results"]), 2)
        # 验证按mid倒序
        self.assertEqual(data["results"][0]["mid"], 2)
        self.assertEqual(data["results"][1]["mid"], 1)

    # ---------------------- query_meet_name 测试 ----------------------
    @skipIf(skip_tests, "Skip tests")
    def test_query_meet_name_success(self):
        url = reverse("query_meet_name") + "?mid=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["name"], "2023校运会")

    @skipIf(skip_tests, "Skip tests")
    def test_query_meet_name_not_exist(self):
        url = reverse("query_meet_name") + "?mid=3"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @skipIf(skip_tests, "Skip tests")
    def test_query_meet_name_not_allowed(self):
        url = reverse("query_meet_name") + "?miid=3"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        # ---------------------- query_personal_web 测试 ----------------------

    def _make_request(self, name):
        url = reverse("query_personal_web") + f"?name={name}"
        response = self.client.get(url)
        return json.loads(response.content)

    @skipIf(skip_tests, "Skip tests")
    def test_invalid_parameters(self):
        """测试非法参数"""
        url = reverse("query_personal_web") + "?name=张三&age=20"  # 添加非法参数
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)["code"], -1)

    @skipIf(skip_tests, "Skip tests")
    def test_valid_time_results(self):
        """测试有效时间结果"""
        data = self._make_request("张三")
        self.assertEqual(
            data["results"]["男子100米"]["result"], "00:11.23"
        )  # 验证最小时间被选中

    @skipIf(skip_tests, "Skip tests")
    def test_valid_number_results(self):
        """测试有效数值结果"""
        data = self._make_request("赵六")
        self.assertEqual(
            data["results"]["女子跳高"]["result"], "1.80"
        )  # 验证最大数值被选中

    def test_mixed_result_types(self):
        """测试混合结果类型"""
        Result.objects.create(
            project=self.project1,
            name="张三",
            groupname="测试组",
            result="invalid_data",
            grade="三级",
            result_type="top8",
        )
        url = reverse("query_personal_web") + "?name=张三"
        response = self.client.get(url)
        data = json.loads(response.content)
        self.assertEqual(response.json()["info"], "Succeed")
        self.assertEqual(data["results"]["男子100米"]["result"], "00:11.23")

    def test_multiple_athletes(self):
        """测试多运动员数据处理"""
        data = self._make_request("王五")
        self.assertEqual(
            data["results"]["女子跳高"]["result"], "1.75"
        )  # 验证多个结果中最大值

    def test_non_existent_name(self):
        """测试不存在的姓名"""
        data = self._make_request("不存在的名字")
        self.assertEqual(data["results"], {})  # 空结果应返回空字典

    def test_special_time_format(self):
        """测试特殊时间格式"""
        Result.objects.create(
            project=self.project1,
            name="张三",
            groupname="测试组",
            result="2'04\"46",  # 添加特殊格式时间
            result_type="top8",
        )
        data = self._make_request("张三")
        self.assertEqual(
            data["results"]["男子100米"]["result"], "00:11.23"
        )  # 仍应选择最小时间

    # ---------------------- query_project_list 测试 ----------------------
    @skipIf(skip_tests, "Skip tests")
    def test_query_project_list_success(self):
        url = reverse("query_project_list") + "?mid=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["name"], "100米")

    @skipIf(skip_tests, "Skip tests")
    def test_query_project_list_not_allowed(self):
        url = reverse("query_project_list") + "?miid=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["code"], -1)

    @skipIf(skip_tests, "Skip tests")
    def test_query_project_list_not_exist(self):
        url = reverse("query_project_list") + "?mid=3"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["code"], 1)

    @skipIf(skip_tests, "Skip tests")
    def test_query_project_list_wrong_param(self):
        url = reverse("query_project_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["code"], -2)
        # ---------------------- query_project_zubie_list 测试 ----------------------

    @skipIf(skip_tests, "Skip tests")
    def test_query_project_zubie_list_success(self):
        url = reverse("query_project_zubie_list") + "?mid=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0], "甲组")

    @skipIf(skip_tests, "Skip tests")
    def test_query_project_zubie_list_not_allowed(self):
        url = reverse("query_project_zubie_list") + "?miid=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["code"], -1)

    @skipIf(skip_tests, "Skip tests")
    def test_query_project_zubie_list_not_exist(self):
        url = reverse("query_project_zubie_list") + "?mid=3"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["code"], 1)

    @skipIf(skip_tests, "Skip tests")
    def test_query_project_zubie_list_wrong_param(self):
        url = reverse("query_project_zubie_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["code"], -2)

    # ---------------------- query 测试 ----------------------
    @skipIf(skip_tests, "Skip tests")
    def test_basic_query(self):
        url = reverse("query") + "?name=张三&zubie=甲组&leixing=决赛&xingbie=男子"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "张三")

    @skipIf(skip_tests, "Skip tests")
    def test_basic_query_my(self):
        url = reverse("query")
        data = {"name": ["邹迦音", "张三"], "session": session_key, "star": True}
        response = self.client.get(url, data=data)
        data = response.json()
        # self.assertEqual(response.json()["info"], "success")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "邹迦音")

    @skipIf(skip_tests, "Skip tests")
    def test_basic_query_meet(self):
        url = reverse("query") + "?meet=2023校运会&ranked=true"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["results"][0]["name"], "张三")

    @skipIf(skip_tests, "Skip tests")
    def test_basic_query_team(self):
        url = reverse("query") + "?groupname=计算机系&projectname=100米"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "张三")

    @skipIf(skip_tests, "Skip tests")
    def test_precise_query(self):
        url = (
            reverse("query")
            + "?projectname=100米&precise=true&meet=2023校运会&groupname=计算机系&&zubie=甲组&leixing=决赛&xingbie=男子"
        )
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 1)

    @skipIf(skip_tests, "Skip tests")
    def test_pagination(self):
        url = reverse("query") + "?page=2&page_size=2"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["current_page"], 2)
        self.assertEqual(len(data["results"]), 2)

    @skipIf(skip_tests, "Skip tests")
    def test_empty_page(self):
        url = reverse("query") + "?page=10&page_size=2"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["current_page"], 4)
        self.assertEqual(len(data["results"]), 2)

    @skipIf(skip_tests, "Skip tests")
    def test_invalid_pagination(self):
        url = reverse("query") + "?page=0&page_size=2"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["code"], 4)

    @skipIf(skip_tests, "Skip tests")
    def test_invalid_parameter(self):
        url = reverse("query") + "?invalid_param=1"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data["code"], -1)

    # ---------------------- query_team_score 测试 ----------------------
    @skipIf(skip_tests, "Skip tests")
    def test_team_score_success(self):
        url = reverse("query_team_score") + "?mid=2&zubie=乙组&xingbie=女子"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data["results"][0]["team"], "计算机系")
        self.assertEqual(data["results"][0]["total_score"], 13)
        self.assertEqual(data["results"][1]["total_score"], 10)

    @skipIf(skip_tests, "Skip tests")
    def test_team_score_no_meet(self):
        url = reverse("query_team_score") + "?mid=3"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["code"], 1)

    @skipIf(skip_tests, "Skip tests")
    def test_team_score_bad_mid(self):
        url = reverse("query_team_score") + "?mid=3a"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["code"], -2)

    @skipIf(skip_tests, "Skip tests")
    def test_team_score_bad_meet(self):
        url = reverse("query_team_score") + "?miid=3"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["code"], -1)

    @skipIf(skip_tests, "Skip tests")
    def test_team_score_missing_param(self):
        url = reverse("query_team_score")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data["code"], -2)

    # @skipIf(skip_tests, 'Skip tests')
    def test_create_project_success(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }
        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        response = self.client.post(
            reverse("manage_project"),
            json.dumps(
                {
                    "name": "新项目",
                    "mid": 1,
                    "session": self.admin_session_key,
                    "zubie": "乙组",
                    "leixing": "决赛",
                    "xingbie": "女子",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 4)

    @skipIf(skip_tests, "Skip tests")
    def test_create_duplicate_project(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        self.client.post(
            reverse("manage_project"),
            json.dumps(
                {
                    "name": "重复项目",
                    "mid": 1,
                    "session": self.admin_session_key,
                    "zubie": "乙组",
                    "leixing": "决赛",
                    "xingbie": "女子",
                }
            ),
            content_type="application/json",
        )
        response = self.client.post(
            reverse("manage_project"),
            json.dumps(
                {
                    "name": "重复项目",
                    "mid": 1,
                    "session": self.admin_session_key,
                    "zubie": "乙组",
                    "leixing": "决赛",
                    "xingbie": "女子",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], 1)

    @skipIf(skip_tests, "Skip tests")
    def test_update_project_duplicate(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        update_data = {
            "mid": 2,
            "id": self.project3.id,
            "name": "跳高",
            "zubie": "乙组",
            "leixing": "决赛",
            "xingbie": "女子",
            "session": self.admin_session_key,
        }
        response = self.client.put(
            reverse("manage_project"),
            json.dumps(update_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], 2)

    @skipIf(skip_tests, "Skip tests")
    def test_update_project_success(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        update_data = {
            "mid": 1,
            "id": self.project1.id,
            "name": "更新后的名称",
            "zubie": "乙组",
            "leixing": "决赛",
            "xingbie": "女子",
            "session": self.admin_session_key,
        }
        response = self.client.put(
            reverse("manage_project"),
            json.dumps(update_data),
            content_type="application/json",
        )
        updated_meet = Meet.objects.get(mid=1)
        updated_project = Project.objects.get(contest=updated_meet, name="更新后的名称")
        self.assertEqual(response.json()["code"], 0)
        self.assertEqual(updated_project.name, "更新后的名称")

    @skipIf(skip_tests, "Skip tests")
    def test_update_nonexistent_project(self):
        """测试更新不存在的项目"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        response = self.client.put(
            reverse("manage_project"),
            json.dumps(
                {
                    "mid": 1,
                    "id": 1999,
                    "name": "不存在的",
                    "zubie": "乙组",
                    "leixing": "决赛",
                    "xingbie": "女子",
                    "session": self.admin_session_key,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.json()["info"], "项目不存在")
        self.assertEqual(response.json()["code"], 2)

    @skipIf(skip_tests, "Skip tests")
    def test_delete_project_success(self):
        """测试成功删除项目及级联删除"""
        # 先验证关联数据存在
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]

        self.assertEqual(Project.objects.count(), 3)
        self.assertEqual(Result.objects.count(), 8)

        response = self.client.delete(
            reverse("manage_project"),
            json.dumps(
                {
                    "mid": 1,
                    "id": self.project1.id,
                    "session": self.admin_session_key,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 0)

        # 验证级联删除
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Result.objects.count(), 6)

    @skipIf(skip_tests, "Skip tests")
    def test_delete_nonexistent_project(self):
        """测试删除不存在的项目"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        response = self.client.delete(
            reverse("manage_project"),
            json.dumps(
                {
                    "mid": 1,
                    "id": 19999,
                    "session": self.admin_session_key,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 2)

    @skipIf(skip_tests, "Skip tests")
    def test_create_meet_success(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }
        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        response = self.client.post(
            reverse("manage_meet"),
            json.dumps({"name": "新比赛", "session": self.admin_session_key}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 0)
        self.assertEqual(Meet.objects.count(), 3)

    @skipIf(skip_tests, "Skip tests")
    def test_create_meet_no_session(self):
        response = self.client.post(
            reverse("manage_meet"),
            json.dumps({"name": "新比赛"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], -2)

    @skipIf(skip_tests, "Skip tests")
    def test_create_meet_bad_method(self):
        response = self.client.get(reverse("manage_meet"))
        self.assertEqual(response.status_code, 405)

    @skipIf(skip_tests, "Skip tests")
    def test_create_duplicate_meet(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        self.client.post(
            reverse("manage_meet"),
            json.dumps({"name": "重复比赛", "session": self.admin_session_key}),
            content_type="application/json",
        )
        response = self.client.post(
            reverse("manage_meet"),
            json.dumps({"name": "重复比赛", "session": self.admin_session_key}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], 1)

    @skipIf(skip_tests, "Skip tests")
    def test_update_meet_success(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        update_data = {
            "mid": 1,
            "name": "更新后的名称",
            "session": self.admin_session_key,
        }
        response = self.client.put(
            reverse("manage_meet"),
            json.dumps(update_data),
            content_type="application/json",
        )
        updated_meet = Meet.objects.get(mid=1)
        self.assertEqual(response.json()["code"], 0)
        self.assertEqual(updated_meet.name, "更新后的名称")

    @skipIf(skip_tests, "Skip tests")
    def test_update_nonexistent_meet(self):
        """测试更新不存在的比赛"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        response = self.client.put(
            reverse("manage_meet"),
            json.dumps(
                {"mid": 1999, "name": "不存在的", "session": self.admin_session_key}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.json()["info"], "比赛id不存在")
        self.assertEqual(response.json()["code"], 2)

    @skipIf(skip_tests, "Skip tests")
    def test_update_nonexistent_meet_invalid_mid(self):
        """测试更新不存在的比赛"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }
        self.client.post("/users/create_system_admin_temporary", data=data)
        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        response = self.client.put(
            reverse("manage_meet"),
            json.dumps(
                {
                    "mid": "aaa",
                    "name": "不存在的",
                    "session": self.admin_session_key,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], -2)

    @skipIf(skip_tests, "Skip tests")
    def test_update_nonexistent_meet_lack_param(self):
        """缺少必要参数"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }
        self.client.post("/users/create_system_admin_temporary", data=data)
        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        response = self.client.put(
            reverse("manage_meet"),
            json.dumps({"mid": 1, "session": self.admin_session_key}),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], -2)

    @skipIf(skip_tests, "Skip tests")
    def test_delete_meet_success(self):
        """测试成功删除比赛及级联删除"""
        # 先验证关联数据存在
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]

        self.assertEqual(Project.objects.count(), 3)
        self.assertEqual(Result.objects.count(), 8)

        response = self.client.delete(
            reverse("manage_meet"),
            json.dumps({"mid": 1, "session": self.admin_session_key}),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 0)
        self.assertEqual(Meet.objects.count(), 1)
        # 验证级联删除
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Result.objects.count(), 6)

    @skipIf(skip_tests, "Skip tests")
    def test_delete_nonexistent_meet(self):
        """测试删除不存在的比赛"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        response = self.client.delete(
            reverse("manage_meet"),
            json.dumps({"mid": 999, "session": self.admin_session_key}),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 3)

    # @skipIf(skip_tests, 'Skip tests')

    # -------------------------- manage_result --------------------------
    @skipIf(skip_tests, "Skip tests")
    def test_create_result_success(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        data = {
            "session": self.admin_session_key,
            "projectid": self.project1.id,
            "name": "新选手",
            "groupname": "新队伍",
            "result": "10.01",
            "score": 9.5,
            "rank": 1,
            "commit": "True",
        }
        response = self.client.post(
            reverse("manage_result"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.json()["info"], "Succeed")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 0)
        self.assertEqual(Result.objects.count(), 9)
        self.assertEqual(Athlete.objects.filter(real_name="新选手").count(), 1)

    @skipIf(skip_tests, "Skip tests")
    def test_create_result_not_auth(self):
        data = {
            "username": "test",
            "password": "222222",
        }
        self.client.post("/users/register", data=data)
        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        data = {
            "session": self.admin_session_key,
            "projectid": self.project1.id,
            "name": "新选手",
            "groupname": "新队伍",
            "result": "10.01",
            "score": 9.5,
            "rank": 1,
            "commit": "True",
        }
        response = self.client.post(
            reverse("manage_result"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["code"], -3)
        self.assertEqual(Athlete.objects.filter(real_name="新选手").count(), 0)

    @skipIf(skip_tests, "Skip tests")
    def test_create_result_invalid_score(self):
        """测试更新无效分数类型"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        invalid_data = {
            "projectid": self.project1.id,
            "name": "张三",
            "groupname": "计算机系",
            "result": 12.07,
            "score": "invalid_score",
            "session": self.admin_session_key,
            "commit": "True",
        }
        response = self.client.post(
            reverse("manage_result"),
            json.dumps(invalid_data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 2)
        self.assertIn("score必须为数", response.json()["info"])

    @skipIf(skip_tests, "Skip tests")
    def test_update_result_invalid_rank(self):
        """测试更新无效排名"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]

        invalid_data = {
            "resultid": self.result1.id,
            "name": "张三",
            "groupname": "计算机系",
            "result": 12.07,
            "rank": "invalid_score",
            "session": self.admin_session_key,
        }
        response = self.client.put(
            reverse("manage_result"),
            json.dumps(invalid_data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 3)
        self.assertIn("排名必须为整数", response.json()["info"])

    @skipIf(skip_tests, "Skip tests")
    def test_create_result_invalid_rank(self):
        """测试创建无效排名"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        invalid_data = {
            "projectid": self.project1.id,
            "name": "张三",
            "groupname": "计算机系",
            "result": 12.07,
            "rank": "invalid_score",
            "session": self.admin_session_key,
            "commit": True,
        }
        response = self.client.post(
            reverse("manage_result"),
            json.dumps(invalid_data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 5)
        self.assertIn("排名必须为整数", response.json()["info"])

    @skipIf(skip_tests, "Skip tests")
    def test_update_result_score(self):
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        data = {
            "resultid": self.result1.id,
            "name": "张三",
            "groupname": "计算机系",
            "result": "9.99",
            "score": 15.0,
            "session": self.admin_session_key,
        }
        response = self.client.put(
            reverse("manage_result"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        updated = Result.objects.get(pk=self.result1.pk)
        self.assertEqual(updated.score, 15.0)

    @skipIf(skip_tests, "Skip tests")
    def test_update_result_rank_type(self):
        """测试更新排名自动修改result_type"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        update_data = {
            "resultid": self.result1.id,
            "name": "张三",
            "groupname": "计算机系",
            "result": "9.99",
            "rank": 5,
            "session": self.admin_session_key,
        }
        response = self.client.put(
            reverse("manage_result"),
            json.dumps(update_data),
            content_type="application/json",
        )
        updated = Result.objects.get(pk=self.result1.pk)
        self.assertEqual(updated.result_type, "top8")
        self.assertEqual(updated.rank, 5)

    @skipIf(skip_tests, "Skip tests")
    def test_update_result_invalid_score(self):
        """测试更新无效分数类型"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        invalid_data = {
            "resultid": self.result1.id,
            "name": "张三",
            "groupname": "计算机系",
            "result": 12.07,
            "score": "invalid_score",
            "session": self.admin_session_key,
        }
        response = self.client.put(
            reverse("manage_result"),
            json.dumps(invalid_data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 4)
        self.assertIn("score必须为数", response.json()["info"])

    @skipIf(skip_tests, "Skip tests")
    def test_update_result_invalid_rank(self):
        """测试更新无效排名"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        invalid_data = {
            "resultid": self.result1.id,
            "name": "张三",
            "groupname": "计算机系",
            "result": 12.07,
            "rank": "invalid_score",
            "session": self.admin_session_key,
        }
        response = self.client.put(
            reverse("manage_result"),
            json.dumps(invalid_data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 3)
        self.assertIn("排名必须为整数", response.json()["info"])

    @skipIf(skip_tests, "Skip tests")
    def test_put_non_existent_result(self):
        """测试更新不存在的成绩"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        delete_data = {
            "resultid": 1999999999,
            "name": "张四",
            "groupname": "计算机系",
            "result": 13.07,
            "session": self.admin_session_key,
        }
        response = self.client.put(
            reverse("manage_result"),
            json.dumps(delete_data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["info"], "成绩不存在")
        self.assertEqual(response.json()["code"], 3)

    @skipIf(skip_tests, "Skip tests")
    def test_delete_result_success(self):
        """测试成功删除成绩"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        delete_data = {
            "resultid": self.result1.id,
            "session": self.admin_session_key,
        }
        response = self.client.delete(
            reverse("manage_result"),
            json.dumps(delete_data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 0)
        self.assertEqual(Result.objects.count(), 7)

    @skipIf(skip_tests, "Skip tests")
    def test_delete_nonexistent_result_name(self):
        """测试删除不存在的成绩"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        delete_data = {
            "resultid": 19999,
            "session": self.admin_session_key,
        }
        response = self.client.delete(
            reverse("manage_result"),
            json.dumps(delete_data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["code"], 3)

    @skipIf(skip_tests, "Skip tests")
    def test_create_result_duplicate(self):
        """测试创建重复成绩"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }

        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        duplicate_data = {
            "projectid": self.project1.id,
            "name": "张三",
            "groupname": "计算机系",
            "result": "10.01",
            "session": self.admin_session_key,
            "commit": False,
        }
        response = self.client.post(
            reverse("manage_result"),
            json.dumps(duplicate_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("该选手在该比赛项目中成绩已存在", response.json()["info"])

    @skipIf(skip_tests, "Skip tests")
    def test_update_result_from_online(self):
        """从原始网站同步数据"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }
        self.client.post("/users/create_system_admin_temporary", data=data)
        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        data = {"meet_list": [1, 2], "session": self.admin_session_key}
        response = self.client.put(
            reverse("update_new_result_from_online"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["info"], "Succeed")
        self.assertEqual(response.status_code, 200)

    @skipIf(skip_tests, "Skip tests")
    def test_update_result_from_online_not_auth(self):
        data = {
            "username": "meeee",
            "password": "222222",
        }
        self.client.post("/users/register", data=data)
        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        data = {"meet_list": [1, 2], "session": self.admin_session_key}
        response = self.client.put(
            reverse("update_new_result_from_online"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["code"], -3)

    @skipIf(skip_tests, "Skip tests")
    def test_update_result_from_online_meet_not_exist(self):
        """从原始网站同步数据"""
        data = {
            "username": "admin_bjsh_test",
            "password": "222222",
        }
        self.client.post("/users/create_system_admin_temporary", data=data)
        res = self.client.post("/users/login", data=data)
        content = json.loads(res.content.decode())["data"]
        self.admin_session_key = content["session"]
        data = {"meet_list": [3], "session": self.admin_session_key}
        response = self.client.put(
            reverse("update_new_result_from_online"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.json()["info"], "比赛3不存在")
