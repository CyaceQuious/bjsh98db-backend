from django.http import HttpResponse, HttpRequest
from utils.utils_request import request_failed, request_success
from utils.utils_check import CheckMethod,session_authenticated_required,session_authenticated_required_get
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from .models import UserProfile,Star,Athlete
from Query.models import Meet
import re
import json
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# Create your views here.

@CheckMethod(permissions=["POST"])
def login(request: HttpRequest):
    param_set = {"username", "password"}
    params_illegal = set(request.POST.keys()) - param_set
    if params_illegal:
        return request_failed(-1, f"非法参数: {params_illegal}", 400)
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username is None or password is None:
        return request_failed(-2, "请填写所有必填项", 400)
    Users = UserProfile.objects.filter(username=username)
    if Users.count() == 0:
        return request_failed(-1, "用户名不存在", 404)
    password_hash = make_password(password, salt="L_1OhYGyQhoHS_6_",hasher='default')
    Users = Users.filter(password=password_hash)
    if Users.count() == 0:
        return request_failed(2, "用户名或密码错误", 400)

    request.session['id'] = Users[0].id
    request.session.save()
    response_session = request.session.session_key
    return request_success({
        "data": {
            "session": response_session,
            "username": username,
            "email": Users[0].email,
            "create_time": Users[0].create_time,
            "org": Users[0].org,
            "Is_Department_Official": Users[0].Is_Department_Official,
            "Is_Contest_Official": Users[0].Is_Contest_Official,
            "Is_System_Admin": Users[0].Is_System_Admin,
        }
    })


def is_alnum_and_underline(s):
    return re.fullmatch(r'[a-zA-Z0-9_]+', s)

@CheckMethod(permissions=["POST"])
def register(request: HttpRequest):
    param_set = {"username", "password"}
    params_illegal = set(request.POST.keys()) - param_set
    if params_illegal:
        return request_failed(-1, f"非法参数: {params_illegal}", 400)
        # do something with the form data
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username is None or password is None:
        return request_failed(-2, "请填写所有必填项", 400)
    if is_alnum_and_underline(username) is None:
        return request_failed(3, "用户名只能包含字母、数字、下划线", 400)
    if is_alnum_and_underline(password) is None:
        return request_failed(4, "密码只能包含字母、数字、下划线", 400)
    if len(username) > 15:
        return request_failed(5, "用户名长度不能超过15", 400)
    if len(password) > 16 or len(password) < 6:
        return request_failed(6, "密码长度不能超过16, 不能少于6", 400)
    if UserProfile.objects.filter(username=username).exists():
        return request_failed(1, "用户名已存在", 400)
    password_hash = make_password(password=password, salt="L_1OhYGyQhoHS_6_",hasher='default')
    UserProfile.objects.create(username=username, password=password_hash)
    return request_success({
        "data": {
            "username": username,
        }
    }
    )


@CheckMethod(permissions=["POST"])
@session_authenticated_required
def modify_user_status(request: HttpRequest):
    param_set = {"session", "user_to_modify", "Is_Department_Official",
                 "Is_Contest_Official", "Is_System_Admin"}
    params_illegal = set(request.POST.keys()) - param_set
    if params_illegal:
        return request_failed(-1, f"非法参数: {params_illegal}", 400)
    user = request.auth_user
    if not user.Is_System_Admin:
        return request_failed(-3, "权限不足", 401)
    user_to_modify = request.POST.get('user_to_modify')
    if user_to_modify is None:
        return request_failed(-2, "请填写所有必填项", 400)
    user_m = UserProfile.objects.filter(username=user_to_modify)
    if user_m.count() == 0:
        return request_failed(2, "被修改用户不存在", 404)
    user_m = user_m[0]
    Is_Department_Official = request.POST.get('Is_Department_Official')
    Is_Contest_Official = request.POST.getlist('Is_Contest_Official')
    try:
        Is_Contest_Official = list(map(int, Is_Contest_Official))
    except ValueError:
        return request_failed(7, "Is_Contest_Official数据类型错误", 400)

    Is_System_Admin = request.POST.get('Is_System_Admin')
    if Is_Department_Official is None or Is_Contest_Official is None or Is_System_Admin is None:
        return request_failed(-2, "请填写所有必填项", 400)
    user_m.Is_Department_Official = Is_Department_Official
    user_m.Is_System_Admin = Is_System_Admin
    existing = set(Meet.objects.filter(mid__in=Is_Contest_Official).values_list('mid', flat=True))
    missing = set(Is_Contest_Official) - existing
    if missing:
        missing_str = ",".join(map(str, missing))
        return request_failed(8, f"比赛{missing_str}不存在", 404)
    user_m.Is_Contest_Official = Is_Contest_Official
    user_m.save()
    return request_success()

@CheckMethod(permissions=["GET"])
@CheckRequire
def get_user_status(request: HttpRequest):
    allowed_params = {'username'}
    if not set(request.GET.keys()).issubset(allowed_params):
        return request_failed(-1, f"Invalid parameter: {set(request.GET.keys()) - allowed_params}")
    username = request.GET.get('username')
    if username is None:
        return request_failed(-2, "请填写所有必填项", 400)
    user = UserProfile.objects.filter(username=username)
    if user.count() == 0:
        return request_failed(2, "用户不存在", 404)
    user = user[0]
    return request_success({
        "data": {
            "username": user.username,
            "Is_Department_Official": user.Is_Department_Official,
            "Is_Contest_Official": user.Is_Contest_Official,
            "Is_System_Admin": user.Is_System_Admin,
        }
        })

@CheckMethod(permissions=["GET"])
@CheckRequire
@session_authenticated_required_get
def get_user_profile(request: HttpRequest):
    allowed_params = {'session'}
    if not set(request.GET.keys()).issubset(allowed_params):
        return request_failed(-1, f"Invalid parameter: {set(request.GET.keys()) - allowed_params}")
    user = request.auth_user
    star_list = [star.Athlete.real_name for star in Star.objects.filter(User=user)]
    return request_success({
        "data": {
            "username": user.username,
            "email": user.email,
            "create_time": user.create_time,
            "real_name": user.athlete_user if hasattr(user, 'athelete_user') else None,
            "org": user.org,
            "Is_Department_Official": user.Is_Department_Official,
            "Is_Contest_Official": user.Is_Contest_Official,
            "Is_System_Admin": user.Is_System_Admin, 
            "star_list": star_list
        }
        })

@CheckMethod(permissions=["POST"])
@CheckRequire
@session_authenticated_required
def modify_password(request: HttpRequest):
    allowed_params = {"session", "password"}
    if not set(request.POST.keys()).issubset(allowed_params):
        return request_failed(-1, f"Invalid parameter: {set(request.POST.keys()) - allowed_params}")
    user = request.auth_user
    password = request.POST.get('password')
    if is_alnum_and_underline(password) is None:
        return request_failed(4, "密码只能包含字母、数字、下划线", 400)
    if len(password) > 16 or len(password) < 6:
        return request_failed(6, "密码长度不能超过16, 不能少于6", 400)
    password_hash = make_password(password=password, salt="L_1OhYGyQhoHS_6_",hasher='default')
    user.password = password_hash
    user.save()
    return request_success({
        "data": {
            "username": user.username,
        }
    }
    )

def is_valid_email(value):
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False

@CheckMethod(permissions=["POST"])
@CheckRequire
@session_authenticated_required
def modify_user_profile(request: HttpRequest):
    allowed_params = {"session", "email"}
    if not set(request.POST.keys()).issubset(allowed_params):
        return request_failed(-1, f"Invalid parameter: {set(request.POST.keys()) - allowed_params}")
    user = request.auth_user
    email = request.POST.get('email')
    if email is None:
        return request_failed(-2, "请填写所有必填项", 400)
    if not is_valid_email(email):
        return request_failed(9, "请填写正确的邮箱", 400)
    user.email = email
    user.save()
    return request_success({
        "data": {
            "username": user.username,
            "email": user.email,
            "create_time": user.create_time,
            "Is_Department_Official": user.Is_Department_Official,
            "Is_Contest_Official": user.Is_Contest_Official,
            "Is_System_Admin": user.Is_System_Admin,
        }
    }
    )

@CheckRequire
@CheckMethod(permissions=["POST"])
@session_authenticated_required
def add_star(request: HttpRequest):
    user = request.auth_user
    allowed_params = {"session", "athlete_name"}
    params = request.POST
    if not set(params.keys()).issubset(allowed_params):
        return request_failed(-1, f"Invalid parameter: {set(params.keys()) - allowed_params}")
    
    athlete_name = params.get('athlete_name')

    if athlete_name is None:
        return request_failed(-2, "请填写所有必填项", 400)
    athlete = Athlete.objects.filter(real_name=athlete_name)

    if athlete.count() == 0:
        return request_failed(2, "运动员不存在", 404)
    athlete = athlete[0]
    athlete_exist = Star.objects.filter(User=user, Athlete=athlete).exists()    
    if athlete_exist:
        return request_failed(3, "已经关注过了", 400)
    Star.objects.create(User=user, Athlete=athlete)

    
    return request_success({
        "data": {
            "username": user.username,
            "star_list": [star.Athlete.real_name for star in Star.objects.filter(User=user)]
        }
    })

@CheckRequire
@CheckMethod(permissions=["POST"])
@session_authenticated_required
def delete_star(request: HttpRequest):
    user = request.auth_user
    allowed_params = {"session", "athlete_name"}
    params = request.POST
    if not set(params.keys()).issubset(allowed_params):
        return request_failed(-1, f"Invalid parameter: {set(params.keys()) - allowed_params}")
    
    athlete_name = params.get('athlete_name')

    if athlete_name is None:
        return request_failed(-2, "请填写所有必填项", 400)
    athlete = Athlete.objects.filter(real_name=athlete_name)

    if athlete.count() == 0:
        return request_failed(2, "运动员不存在", 404)
    athlete = athlete[0]
    athlete_exist = Star.objects.filter(User=user, Athlete=athlete).exists()    
    if not athlete_exist:
        return request_failed(4, "不能取消未关注的运动员", 400)
    Star.objects.filter(User=user, Athlete=athlete).delete()

    
    return request_success({
        "data": {
            "username": user.username,
            "star_list": [star.Athlete.real_name for star in Star.objects.filter(User=user)]
        }
    })


    