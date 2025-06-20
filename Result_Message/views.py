from django.http import HttpResponse, HttpRequest
from utils.utils_request import request_failed, request_success
from django.utils import timezone
from utils.utils_check import (
    CheckMethod,
    session_authenticated_required,
    session_authenticated_required_get,
)
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from Users.models import UserProfile, Star, Athlete
from Result_Message.models import ResultRequest
import json

# Create your views here.
from Query.models import Result, Meet, Project


@CheckMethod(permissions=["POST"])
@CheckRequire
@session_authenticated_required
def feedback(req: HttpRequest):
    params = json.loads(req.body)
    allowed_params = {"applyreason", "result_id", "session"}
    if not set(params.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(params.keys()) - allowed_params}"
        )
    user = req.auth_user
    if (not user.Is_System_Admin) and (not user.Is_Department_Official):
        return request_failed(-3, "权限不足", 401)
    result_id = require(params, "result_id", "int")
    applyreason = require(params, "applyreason", "string")

    try:
        result = Result.objects.get(id=result_id)
    except Result.DoesNotExist:
        return request_failed(3, "成绩不存在", 404)
    Message_count = ResultRequest.objects.filter(sender=user, status=0).count()
    if Message_count >= 10:
        return request_failed(8, f"申请已达上限数量", 400)
    if len(applyreason) > 300:
        return request_failed(5, "理由长度超过300字符限制", 400)  # HTTP 400 Bad Request

    ResultRequest.objects.create(sender=user, result=result, apply_reason=applyreason)
    return request_success()


@CheckMethod(permissions=["POST"])
@CheckRequire
@session_authenticated_required
def reply_feedback(req: HttpRequest):
    params = json.loads(req.body)
    allowed_params = {"reject_reason", "approval", "id", "session"}
    if not set(params.keys()).issubset(allowed_params):
        return request_failed(
            -1, f"Invalid parameter: {set(params.keys()) - allowed_params}"
        )
    user = req.auth_user
    message_id = require(params, "id", "int")
    approval = require(params, "approval", "string")
    try:
        message = ResultRequest.objects.get(id=message_id)
        result = message.result
        meet_id = result.project.contest.mid
    except ResultRequest.DoesNotExist:
        return request_failed(3, f"成绩反馈{message_id}不存在", 404)
    if (not user.Is_System_Admin) and (meet_id not in user.Is_Contest_Official):
        return request_failed(-3, "权限不足", 401)
    if approval == "True":
        message.status = ResultRequest.STATUS_APPROVED
        message.replied_at = timezone.now()
        message.save()
    elif approval == "False":
        message.status = ResultRequest.STATUS_REJECTED
        message.replied_at = timezone.now()
        reject_reason = require(params, "reject_reason", "string")
        if len(reject_reason) > 300:
            return request_failed(
                5, "理由长度超过300字符限制", 400
            )  # HTTP 400 Bad Request
        message.reject_reason = reject_reason
        message.save()
    else:
        return request_failed(-2, f"approval is not True or False")
    return request_success()


@CheckMethod(permissions=["GET"])
@session_authenticated_required_get
def get_feedback_sent(request: HttpRequest):
    user = request.auth_user
    result_requests = ResultRequest.objects.filter(sender=user)
    result_requests_data = []
    for result_request in result_requests:
        result_requests_data.append(
            {
                "meet": result_request.result.project.contest.name,
                "mid": result_request.result.project.contest.mid,
                "projectname": result_request.result.project.name,
                "zubie": result_request.result.project.zubie,
                "leixing": result_request.result.project.leixing,
                "xingbie": result_request.result.project.xingbie,
                "name": result_request.result.name,
                "groupname": result_request.result.groupname,
                "applied_at": result_request.applied_at,
                "status": result_request.status,
                "reject_reason": result_request.reject_reason,
                "replied_at": result_request.replied_at,
                "apply_reason":result_request.apply_reason,
                "id": result_request.id,
                "resultid":result_request.result.id
            }
        )
    return request_success({"feedback_requests": result_requests_data})


@CheckMethod(permissions=["GET"])
@session_authenticated_required_get
def get_feedback_received(request: HttpRequest):
    user = request.auth_user
    result_requests = ResultRequest.objects.filter(
        result__project__contest__mid__in=user.Is_Contest_Official
    )
    result_requests_data = []
    for result_request in result_requests:
        result_requests_data.append(
            {
                "meet": result_request.result.project.contest.name,
                "mid": result_request.result.project.contest.mid,
                "projectname": result_request.result.project.name,
                "zubie": result_request.result.project.zubie,
                "leixing": result_request.result.project.leixing,
                "xingbie": result_request.result.project.xingbie,
                "name": result_request.result.name,
                "groupname": result_request.result.groupname,
                "sender": result_request.sender.username,
                "applied_at": result_request.applied_at,
                "status": result_request.status,
                "reject_reason": result_request.reject_reason,
                "apply_reason":result_request.apply_reason,
                "replied_at": result_request.replied_at,
                "id": result_request.id,
                "resultid":result_request.result.id
            }
        )
    return request_success({"feedback_requests": result_requests_data})
