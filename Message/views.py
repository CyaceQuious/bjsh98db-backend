from django.http import HttpResponse, HttpRequest
from utils.utils_request import request_failed, request_success
from utils.utils_check import CheckMethod,session_authenticated_required,session_authenticated_required_get
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require,get_param
from Users.models import UserProfile,Star,Athlete
from Query.models import Meet
from Message.models import AuthRequest
import re
import json
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# import datetime
from django.utils import timezone
# Create your views here.

@CheckMethod(permissions=["POST"])
@CheckRequire
@session_authenticated_required
def apply_auth(request: HttpRequest):
    allowed_params = {'session','real_name','invited_reviewer'}
    if not set(request.POST.keys()).issubset(allowed_params):
        return request_failed(-1, f"Invalid parameter: {set(request.POST.keys()) - allowed_params}")
    sender = request.auth_user
    sender_username = sender.username
    user_Athlete = Athlete.objects.filter(User=sender).first()
    if user_Athlete:
        return request_failed(6, f"您已经绑定了：{user_Athlete.real_name}",400)
    real_name = get_param(request,'real_name')
    athlete = Athlete.objects.filter(real_name=real_name).first()
    if not athlete:
        return request_failed(3, f"申请运动员不存在",404)
    if athlete.User:
        return request_failed(7, f"运动员已有绑定用户",400)
    invited_reviewer = get_param(request,'invited_reviewer')
    reviewer = UserProfile.objects.filter(username=invited_reviewer).first()
    if not reviewer:
        return request_failed(4, f"受邀审核体干不存在",404)
    if not reviewer.Is_Department_Official and not reviewer.Is_System_Admin:
        return request_failed(5, f"受邀审核用户无权限",401)
    Message_count = AuthRequest.objects.filter(sender=sender,status=0).count()
    if Message_count >= 5:
        return request_failed(8, f"申请已达上限数量",400)
    authrequest = AuthRequest.objects.create(Athlete=athlete,sender=sender,invited_reviewer=reviewer)

    return request_success({"data":{"message_id":authrequest.id}})

@CheckMethod(permissions=["GET"])
@session_authenticated_required_get
def get_auth_sent(request: HttpRequest):
    sender = request.auth_user
    auth_requests = AuthRequest.objects.filter(sender=sender)
    auth_requests_data = []
    for auth_request in auth_requests:
        auth_requests_data.append({
            "message_id":auth_request.id,
            "real_name":auth_request.Athlete.real_name,
            "invited_reviewer":auth_request.invited_reviewer.username,
            "applied_at":timezone.localtime(auth_request.applied_at),
            "status":auth_request.status,
            "reject_reason":auth_request.reject_reason,
            "replied_at":timezone.localtime(auth_request.replied_at)
        })
    return request_success({
        "data":{
            "auth_requests":auth_requests_data
            }
        }
    )

@CheckMethod(permissions=["POST"])
@CheckRequire
@session_authenticated_required
def authenticate(request: HttpRequest):
    invited_reviewer = request.auth_user
    if not invited_reviewer.Is_Department_Official and not invited_reviewer.Is_System_Admin:
        return request_failed(5, f"您无权限",401)
    allowed_params = {'session','message_id','status','reject_reason'}
    if not set(request.POST.keys()).issubset(allowed_params):
        return request_failed(-1, f"Invalid parameter: {set(request.POST.keys()) - allowed_params}")
    message_id = get_param(request,'message_id')
    if not message_id.isdigit():
        return request_failed(-2, f"message_id不合法",400)
    message_id = int(message_id)
    This_request = AuthRequest.objects.filter(id = message_id).first()
    if not This_request:
        return request_failed(1, f"申请不存在",404)
    reviewer = This_request.invited_reviewer
    if reviewer != invited_reviewer:
        if not invited_reviewer.Is_System_Admin:
            return request_failed(4, f"您不是指定体干",401)
    sender = This_request.sender
    if not sender:
        return request_failed(2, f"申请用户不存在",404)
    sender_athlete = Athlete.objects.filter(User=sender).first()
    athlete = This_request.Athlete
    
    status = get_param(request,'status')
    if status not in ['1','2']:
        return request_failed(8, f"状态不合法",400)
    
    if status == '1':#审核通过

        if sender_athlete:
            return request_failed(6, f"申请用户已经绑定了：{sender_athlete.real_name}",400)
        if not athlete:
            return request_failed(3, f"申请运动员不存在",404)
        if athlete.User:
            return request_failed(7, f"运动员已有绑定用户",400)
        athlete.User = sender
        athlete.save()
        This_request.status = 1

    else:#审核不通过
        pre_status = This_request.status
        if pre_status == 1:
            athlete.User = None
            athlete.save()
        This_request.status = 2
        try:
            This_request.reject_reason = get_param(request,'reject_reason')
            This_request.full_clean()
        except ValidationError:
            return request_failed(9, f"驳回理由超过100字",400)

    This_request.replied_at = timezone.now()
    This_request.save()

        

    return request_success({"data":{
            "message_id":This_request.id,
            "sender_username":sender.username,
            "real_name":athlete.real_name,
            "invited_reviewer":invited_reviewer.username,
            "applied_at":timezone.localtime(This_request.applied_at),
            "status":status,
            "reject_reason":This_request.reject_reason,
            "replied_at":timezone.localtime(This_request.replied_at)
            }})


@CheckMethod(permissions=["GET"])
@session_authenticated_required_get
def get_auth_received(request: HttpRequest):
    invited_reviewer = request.auth_user
    auth_requests = AuthRequest.objects.filter(invited_reviewer=invited_reviewer)
    auth_requests_data = []
    for auth_request in auth_requests:
        auth_requests_data.append({
            "sender_username":auth_request.sender.username,
            "message_id":auth_request.id,
            "real_name":auth_request.Athlete.real_name,
            "applied_at":timezone.localtime(auth_request.applied_at),
            "status":auth_request.status,
            "reject_reason":auth_request.reject_reason,
            "replied_at":timezone.localtime(auth_request.replied_at)
        })
    return request_success({
        "data":{
            "auth_requests":auth_requests_data
            }
        }
    )