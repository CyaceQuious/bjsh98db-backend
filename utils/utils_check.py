from django.http import HttpRequest
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from Users.models import UserProfile
from utils.utils_request import request_failed
import json
from utils.utils_request import BAD_METHOD
def session_authenticated_required(view_func):
    """基于Session的鉴权装饰器"""
    def wrapper(request: HttpRequest, *args, **kwargs):
        # 检查session_key参数
        session_key = request.POST.get('session')
        if not session_key:
            try:
                body = json.loads(request.body.decode('utf-8'))
                session_key = body.get('session')
            except Exception:
                pass
        if not session_key:
            return request_failed(-2, "请填写session", 400)
        try:
            session = Session.objects.get(session_key=session_key)
        except ObjectDoesNotExist:
            return request_failed(-2, "session不存在", 404)
        # 检查会话过期
        if session.expire_date < timezone.now():
            return request_failed(-6, "会话已过期", 400)
        # 解码session数据
        user_id = session.get_decoded().get('id')
        if user_id is None:
            return request_failed(-5, "非法session", 400)

        user = UserProfile.objects.filter(id=user_id)
        if user.count() == 0:
            return request_failed(-1, "请求用户不存在", 404)   
        # 附加用户对象到请求
        request.auth_user = user[0]
        return view_func(request, *args, **kwargs)
    return wrapper

def CheckMethod(permissions):
    def decorator(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            if request.method not in permissions:
                return BAD_METHOD
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator 

def authenticate_request(request):
    session_key = request.GET.get('session')
    if not session_key:
        try:
            body = json.loads(request.body.decode('utf-8'))
            session_key = body.get('session')
        except Exception:
            pass
    if not session_key:
        return None, request_failed(-2, "请填写session", 400)
    try:
        session = Session.objects.get(session_key=session_key)
    except ObjectDoesNotExist:
        return None, request_failed(-2, "session不存在", 404)
    if session.expire_date < timezone.now():
        return None, request_failed(-6, "会话已过期", 400)
    user_id = session.get_decoded().get('id')
    if user_id is None:
        return None, request_failed(-5, "非法session", 400)
    user = UserProfile.objects.filter(id=user_id).first()
    if not user:
        return None, request_failed(-1, "请求用户不存在", 404)
    return user, None

def session_authenticated_required_get(view_func):
    """基于Session的鉴权装饰器get"""
    def wrapper(request: HttpRequest, *args, **kwargs):
        # 检查session_key参数
        user, error = authenticate_request(request)
        if error:
            return error
        request.auth_user = user
        return view_func(request, *args, **kwargs)
    return wrapper


