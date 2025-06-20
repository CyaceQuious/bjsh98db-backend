from utils.utils_request import BAD_METHOD, request_failed, request_success
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_check import (
    CheckMethod,
    session_authenticated_required,
    session_authenticated_required_get,
    authenticate_request,
)
from IPython import embed
import json
from django.http import HttpRequest, HttpResponse
from .models import Meet, Project, Result
from Users.models import Star, Athlete
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
import requests
from requests.exceptions import RequestException
from django.db.models import F, Q
import re


def parse_time(time_str):
    """解析时间字符串，返回总秒数（float），失败返回None"""
    try:
        time_str = time_str.replace('"', ".").replace("'", ":")
        # 处理 mm:ss.ff 或 hh:mm:ss.ff 格式
        parts = re.split(r"[:：]", time_str)  # 支持中文冒号
        parts = [float(p) for p in parts]
        if len(parts) == 2:  # mm:ss.xx
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:  # hh:mm:ss.xx
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
    except (ValueError, AttributeError):
        return None
    return None


def parse_float(value_str):
    """尝试转换为float，失败返回None"""
    try:
        return float(value_str)
    except (ValueError, TypeError):
        return None


def parse_result_type(result_str):
    """判断结果类型：'time'/'number'/'other'"""
    # embed()
    result = parse_time(result_str)
    if result is not None:
        return "time", result
    result = parse_float(result_str)
    if parse_float(result_str) is not None:
        return "number", result
    return "other", None


@CheckRequire
@CheckMethod(permissions=["GET"])
def query_personal_web(req: HttpRequest):
    allowed_params = {"name"}
    if not set(req.GET.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(req.GET.keys()) - allowed_params}"
        )
    name = require(req.GET, "name", "string")
    queryset = Result.objects.select_related("project").filter(name=name)

    # 按project.xingbie和project.name分组
    groups = {}
    for result in queryset:
        key = (result.project.xingbie, result.project.name)
        if key not in groups:
            groups[key] = []
        groups[key].append(result)

    # 计算每个分组的最大值
    max_results = {}
    for key, results in groups.items():
        types = set()
        valid_results = []
        max_results[key] = {"result": None, "grade": None}
        for res in results:
            res_type, res_value = parse_result_type(res.result)
            types.add(res_type)
            valid_results.append((res_value, res.result))
            if res.grade == "健将":
                max_results[key]["grade"] = "健将"
            elif res.grade == "一级" and max_results[key]["grade"] != "健将":
                max_results[key]["grade"] = "一级"
            elif res.grade == "二级" and max_results[key]["grade"] not in [
                "健将",
                "一级",
            ]:
                max_results[key]["grade"] = "二级"
            elif res.grade == "三级" and max_results[key]["grade"] not in [
                "健将",
                "一级",
                "二级",
            ]:
                max_results[key]["grade"] = "三级"
        if "time" in types and "number" in types:
            continue
        res_type = types.pop()
        if res_type == "other":
            if len(types) == 0:
                continue
            else:
                res_type = types.pop()
        if res_type == "time":
            # 找最小时间
            min_time = float("inf")
            best_result = None
            for res_value, res_str in valid_results:
                if res_value:
                    if min_time is None or res_value < min_time:
                        min_time = res_value
                        best_result = res_str
            max_results[key]["result"] = (
                best_result if best_result is not None else None
            )

        elif res_type == "number":
            # 找最大数值
            max_value = -float("inf")
            best_result = None
            for res_value, res_str in valid_results:
                if res_value:
                    if max_value is None or res_value > max_value:
                        max_value = res_value
                        best_result = res_str
            max_results[key]["result"] = (
                best_result if best_result is not None else None
            )
    formatted_results = {
        f"{xingbie}{name}": value for (xingbie, name), value in max_results.items()
    }

    try:
        athlete = Athlete.objects.select_related("User").get(real_name=name)
        user = athlete.User
    except Athlete.DoesNotExist:
        user = None
    
    return request_success({
        "count": len(formatted_results),
        "results": formatted_results,
        "username": user.username if user else None,
        "email": user.email if user else None,
    })


@CheckRequire
@CheckMethod(permissions=["GET"])
def query_meet_list(req: HttpRequest):
    meet_list = Meet.objects.all().order_by("-mid")
    return_list = []
    for result in meet_list:
        return_list.append(
            {
                "name": result.name,
                "mid": result.mid,
            }
        )
    return request_success({"count": len(meet_list), "results": return_list})


@CheckRequire
@CheckMethod(permissions=["GET"])
def query_project_list(req: HttpRequest):
    allowed_params = {"mid"}
    if not set(req.GET.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(req.GET.keys()) - allowed_params}"
        )
    mid = require(req.GET, "mid", "int")
    meet = Meet.objects.all().filter(mid=mid)
    if len(meet) == 0:
        return request_failed(1, "比赛不存在", 404)
    meet_list = Project.objects.all().filter(contest__mid=mid)
    return_list = []
    for result in meet_list:
        return_list.append(
            {
                "name": result.name,
                "leixing": result.leixing,
                "zubie": result.zubie,
                "xingbie": result.xingbie,
                "id": result.id,
            }
        )
    return request_success({"count": len(meet_list), "results": return_list})


@CheckRequire
@CheckMethod(permissions=["GET"])
def query_project_zubie_list(req: HttpRequest):
    allowed_params = {"mid"}
    if not set(req.GET.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(req.GET.keys()) - allowed_params}"
        )
    mid = require(req.GET, "mid", "int")
    meet = Meet.objects.all().filter(mid=mid)
    if len(meet) == 0:
        return request_failed(1, "比赛不存在", 404)
    meet_queryset = Project.objects.filter(contest__mid=mid)
    zubie_list = meet_queryset.values_list("zubie", flat=True).distinct()

    # 转换为列表并返回结果
    return request_success({"count": len(zubie_list), "results": list(zubie_list)})


@CheckRequire
@CheckMethod(permissions=["GET"])
def query_meet_name(req: HttpRequest):
    allowed_params = {"mid"}
    if not set(req.GET.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(req.GET.keys()) - allowed_params}"
        )
    mid = require(req.GET, "mid", "int")
    meet = Meet.objects.all().filter(mid=mid)
    if len(meet) == 0:
        return request_failed(1, "比赛不存在", 404)
    return request_success({"name": meet[0].name})


@CheckRequire
@CheckMethod(permissions=["GET"])
def query(req: HttpRequest):
    name = req.GET.getlist("name")
    meet_name = req.GET.getlist("meet")
    project_name = req.GET.getlist("projectname")
    leixing = req.GET.get("leixing")
    zubie = req.GET.get("zubie")
    xingbie = req.GET.get("xingbie")
    groupname = req.GET.get("groupname")
    precise = req.GET.get("precise") is not None
    ranked = req.GET.get("ranked") is not None
    star = req.GET.get("star") is not None
    allowed_params = {
        "meet",
        "projectname",
        "leixing",
        "zubie",
        "xingbie",
        "name",
        "groupname",
        "ranked",
        "precise",
        "page",
        "page_size",
        "star",
        "session",
    }
    if not set(req.GET.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(req.GET.keys()) - allowed_params}"
        )
    try:
        page = int(req.GET.get("page", 1))
        page_size = int(req.GET.get("page_size", 10))
        if page < 1 or page_size < 1:
            raise ValueError
    except ValueError:
        return request_failed(4, "Invalid pagination parameters")

    queryset = Result.objects.all()
    if star:
        user, _ = authenticate_request(req)
        star_list = [star.Athlete.real_name for star in Star.objects.filter(User=user)]
        queryset = queryset.filter(name__in=star_list)
    if meet_name:
        for meet in meet_name:
            if precise:
                queryset = queryset.filter(project__contest__name=meet)
            else:
                queryset = queryset.filter(project__contest__name__contains=meet)

    # 按Project.name筛选
    if project_name:
        for project in project_name:
            if precise:
                queryset = queryset.filter(project__name=project)
            else:
                queryset = queryset.filter(project__name__contains=project)
    if xingbie:
        if precise:
            queryset = queryset.filter(project__xingbie=xingbie)
        else:
            queryset = queryset.filter(project__xingbie__contains=xingbie)
    if zubie:
        if precise:
            queryset = queryset.filter(project__zubie=zubie)
        else:
            queryset = queryset.filter(project__zubie__contains=zubie)
    if leixing:
        if precise:
            queryset = queryset.filter(project__leixing=leixing)
        else:
            queryset = queryset.filter(project__leixing__contains=leixing)
    # 按Result.name筛选
    if name:
        queryset = queryset.filter(name__in=name)

    # 按groupname筛选
    if groupname:
        if precise:
            queryset = queryset.filter(groupname=groupname)
        else:
            queryset = queryset.filter(groupname__contains=groupname)

    # 按result_type筛选
    if ranked:
        queryset = queryset.filter(result_type="top8")

    queryset = queryset.order_by(
        F("project__contest__mid"), F("rank").asc(nulls_last=True)
    )
    paginator = Paginator(queryset, page_size)
    try:
        current_page = paginator.page(page)
    except EmptyPage:
        # 返回最后一页数据
        current_page = paginator.page(paginator.num_pages)
    # 构造响应数据
    results = []
    for result in current_page.object_list:
        results.append(
            {
                "meet": result.project.contest.name,
                "mid": result.project.contest.mid,
                "projectname": result.project.name,
                "zubie": result.project.zubie,
                "leixing": result.project.leixing,
                "xingbie": result.project.xingbie,
                "name": result.name,
                "result": result.result,
                "grade": result.grade,
                "groupname": result.groupname,
                "rank": result.rank,
                "score": result.score,
                "projectid": result.project.id,
                "resultid": result.id,
            }
        )

    return request_success(
        {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": current_page.number,
            "results": results,
        }
    )


@CheckRequire
@CheckMethod(permissions=["GET"])
def query_team_score(req: HttpRequest):
    allowed_params = {"mid", "zubie", "xingbie"}
    if not set(req.GET.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(req.GET.keys()) - allowed_params}"
        )
    mid = require(req.GET, "mid", "int")
    meet = Meet.objects.filter(mid=mid).first()
    if not meet:
        return request_failed(1, "比赛不存在", 404)
    zubie = req.GET.get("zubie")
    xingbie = req.GET.get("xingbie")
    result_set = Result.objects.filter(project__contest=meet)
    if zubie:
        result_set = result_set.filter(project__zubie=zubie)
    if xingbie:
        result_set = result_set.filter(project__xingbie=xingbie)
    team_scores = (
        result_set.values("groupname")
        .annotate(total_score=Sum("score"))
        .order_by("-total_score")
    )
    return request_success(
        {
            "results": [
                {"team": score["groupname"], "total_score": score["total_score"]}
                for score in team_scores
                if score["total_score"] is not None
            ]
        }
    )


@transaction.atomic
@CheckRequire
@CheckMethod(permissions=["POST", "PUT", "DELETE"])
@session_authenticated_required
def manage_meet(req: HttpRequest):
    """综合管理比赛（创建/更新/删除）"""
    user = req.auth_user
    if not user.Is_System_Admin:
        return request_failed(-3, "权限不足", 401)
    params = json.loads(req.body)
    allowed_params = {"name", "mid", "session"}
    if not set(params.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(params.keys()) - allowed_params}"
        )
    if req.method == "POST":  # 创建
        try:
            meet = Meet.objects.create(name=require(params, "name", "string"))
            return request_success({"mid": meet.mid})
        except IntegrityError as e:
            return request_failed(1, f"比赛名称{e}已存在", 400)

    elif req.method == "PUT":  # 更新
        try:
            meet = Meet.objects.get(mid=require(params, "mid", "int"))
            meet.name = require(params, "name", "string")
            meet.save()
        except Meet.DoesNotExist:
            return request_failed(2, "比赛id不存在", 404)

    elif req.method == "DELETE":  # 删除
        try:
            meet = Meet.objects.get(mid=require(params, "mid", "int"))
            # 级联删除比赛及相关联的Project和Result记录
            meet.delete()
        except Meet.DoesNotExist:
            return request_failed(3, "比赛ID不存在", 404)

    return request_success()


@transaction.atomic
@CheckRequire
@CheckMethod(permissions=["POST", "PUT", "DELETE"])
@session_authenticated_required
def manage_project(req: HttpRequest):
    """综合管理项目（创建/更新/删除）"""
    user = req.auth_user
    params = json.loads(req.body)
    allowed_params = {"name", "mid", "leixing", "zubie", "xingbie", "id", "session"}
    if not set(params.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(params.keys()) - allowed_params}"
        )

    if req.method == "POST":  # 创建
        try:
            meet_id = require(params, "mid", "int")
            project_name = require(params, "name", "string")
            leixing = require(params, "leixing", "string")
            zubie = require(params, "zubie", "string")
            xingbie = require(params, "xingbie", "string")
            if (not user.Is_System_Admin) and (meet_id not in user.Is_Contest_Official):
                return request_failed(-3, "权限不足", 401)
            try:
                meet = Meet.objects.get(mid=meet_id)  # 检查比赛是否存在
            except Meet.DoesNotExist:
                return request_failed(1, "比赛不存在", 404)
            project = Project.objects.create(
                contest=meet,
                name=project_name,
                zubie=zubie,
                xingbie=xingbie,
                leixing=leixing,
            )
        except IntegrityError as e:
            return request_failed(1, f"项目已存在", 400)
    elif req.method == "PUT":  # 更新
        try:
            id = require(params, "id", "int")
            project = Project.objects.get(id=id)
            project.name = require(params, "name", "string")
            project.leixing = require(params, "leixing", "string")
            project.zubie = require(params, "zubie", "string")
            project.xingbie = require(params, "xingbie", "string")
            project.save()
        except Project.DoesNotExist:
            return request_failed(2, "项目不存在", 404)
        except Exception as e:
            return request_failed(2, "与已有项目冲突", 400)
    elif req.method == "DELETE":  # 删除
        try:
            id = require(params, "id", "int")
            project = Project.objects.get(id=id)
            # 级联删除相关联的Project和Result记录
            project.delete()
        except Project.DoesNotExist:
            return request_failed(2, "项目不存在", 404)
    return request_success()


@transaction.atomic
@CheckRequire
@CheckMethod(permissions=["POST", "PUT", "DELETE"])
@session_authenticated_required
def manage_result(req: HttpRequest):
    """综合管理成绩（创建/更新/删除）"""
    user = req.auth_user
    params = json.loads(req.body)
    allowed_params = {
        "name",
        "projectid",
        "resultid",
        "groupname",
        "rank",
        "score",
        "grade",
        "result",
        "commit",
        "session",
    }
    if not set(params.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(params.keys()) - allowed_params}"
        )

    if req.method == "POST":  # 创建
        projectid = require(params, "projectid", "int")
        try:
            project = Project.objects.get(id=projectid)
        except Project.DoesNotExist:
            return request_failed(2, "项目不存在", 404)
        if (not user.Is_System_Admin) and (
            project.contest.mid not in user.Is_Contest_Official
        ):
            return request_failed(-3, "权限不足", 401)
        name = require(params, "name", "string")
        commit = require(params, "commit", "string")
        groupname = require(params, "groupname", "string")
        rank = params.get("rank")
        if rank is not None:
            try:
                rank = int(rank)
                result_type = "top8" if rank <= 8 else "group"
            except ValueError:
                return request_failed(5, "排名必须为整数")
        else:
            result_type = "group"
        if "score" in params:
            try:
                score = float(params.get("score"))
            except (ValueError, TypeError):
                return request_failed(2, "score必须为数")
        else:
            score = None
        result_string = require(params, "result", "string")
        exist_results = Result.objects.filter(
            project=project, name=name, groupname=groupname
        )
        if exist_results and commit != "True":
            return request_failed(1, "该选手在该比赛项目中成绩已存在", 400)
        result = Result.objects.create(
            project=project,
            name=require(params, "name", "string"),
            groupname=require(params, "groupname", "string"),
            result_type=result_type,
            result=result_string,
            grade=params.get("grade", ""),
            rank=rank,
            score=score,
        )
        athlete, created = Athlete.objects.get_or_create(
            real_name=name, defaults={"User": None}
        )
    elif req.method == "PUT":  # 更新
        try:
            resultid = require(params, "resultid", "int")
            result = Result.objects.get(id=resultid)
            result.result = require(params, "result", "string")
            result.groupname = require(params, "groupname", "string")
            result.name=require(params, "name", "string")
            result.grade = params.get("grade", "")
            if "score" in params:
                try:
                    result.score = float(params.get("score"))
                except (ValueError, TypeError):
                    return request_failed(4, "score必须为数")
            else:
                result.score = None
            if "rank" in params:
                try:
                    rank = int(params["rank"])
                    result.rank = rank
                    result.result_type = "top8" if 1 <= rank <= 8 else "group"
                except ValueError:
                    return request_failed(3, "排名必须为整数")
            else:
                result.result_type = "group"
                result.rank = None
            result.save()
        except Result.DoesNotExist:
            return request_failed(3, "成绩不存在", 404)
    elif req.method == "DELETE":  # 删除
        try:
            resultid = require(params, "resultid", "int")
            result = Result.objects.get(id=resultid)
            result.delete()
        except Result.DoesNotExist:
            return request_failed(3, "成绩不存在", 404)
    return request_success()


def download(url):
    print(f"downloading {url}")
    try:
        response = requests.post(url)
        return response.text
    except RequestException as e:
        return ""


def update_result(results, project):
    found = set()
    if "mc" in results.keys():
        for record in results["mc"]:
            if not record["name"] in found:
                Result.objects.update_or_create(
                    project=project,
                    result_type="top8",
                    name=record["name"],
                    result=record["result"],
                    grade=record["grade"],
                    groupname=record["groupname"],
                    rank=record["publicnumber"],
                    score=record["score"],
                )
            found.add(record["name"])
    if "cj" in results.keys():
        for group in results["cj"]:
            for record in group["datas"]:
                if not record["name"] in found:
                    Result.objects.update_or_create(
                        project=project,
                        result_type="group",
                        name=record["name"],
                        result=record["result"],
                        grade=record["grade"],
                        groupname=record["groupname"],
                    )
                found.add(record["name"])
    for name in found:
        athlete, _ = Athlete.objects.get_or_create(real_name=name)


def update_project(meet, mid):
    cnt = 0
    try:
        matches = json.loads(
            download(f"https://wx.bjsh98.com/mobile/query/getAllSchedule?mid={mid}")
        )
    except json.decoder.JSONDecodeError:
        matches = []
    for match in matches:
        project, _ = Project.objects.get_or_create(
            contest=meet,
            name=match["projectname"],
            xingbie=["男子", "女子", "混合"][match["xingbie"] - 1],
            zubie=match["zubie"],
            leixing=match["leixing"],
        )
        if _ or not Result.objects.filter(project=project).exists():
            # 更新成绩数据
            try:
                results = json.loads(
                    download(
                        f"https://wx.bjsh98.com/mobile/query/getResultsById?type=all&mid={mid}&sid={match['sid']}"
                    )
                )
            except json.decoder.JSONDecodeError:
                results = {}
            if results:
                update_result(results, project)
                cnt += 1
    return cnt


@CheckRequire
@CheckMethod(permissions=["PUT"])
@session_authenticated_required
def update_new_meet_from_online(req: HttpRequest):
    user = req.auth_user
    if not user.Is_System_Admin:
        return request_failed(-3, "权限不足", 401)
    meet_data = json.loads(download("https://wx.bjsh98.com/mobile/query/getMeetInfo"))
    update_meet_num = {}
    for meet_info in meet_data:
        meet, created = Meet.objects.get_or_create(
            mid=meet_info["mid"], defaults={"name": meet_info["meetname"]}
        )
        if created:
            update_meet_num[meet_info["meetname"]] = update_project(
                meet, meet_info["mid"]
            )
    return request_success({"update_meet_num": update_meet_num})


@CheckRequire
@CheckMethod(permissions=["PUT"])
@session_authenticated_required
def update_new_result_from_online(req: HttpRequest):
    user = req.auth_user
    params = json.loads(req.body)

    meet_list = require(params, "meet_list", "list")
    for i in range(len(meet_list)):
        meet_list[i] = int(meet_list[i])
        if (not user.Is_System_Admin) and (
            meet_list[i] not in user.Is_Contest_Official
        ):
            return request_failed(-3, f"比赛{meet_list[i]}权限不足", 401)

    update_meet_num = {}
    for mid in meet_list:
        try:
            meet = Meet.objects.get(mid=mid)
        except Meet.DoesNotExist:
            return request_failed(1, f"比赛{mid}不存在", 404)
        update_meet_num[meet.name] = update_project(meet, mid)
    return request_success({"update_meet_num": update_meet_num})
