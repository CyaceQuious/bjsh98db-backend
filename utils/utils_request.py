from django.http import JsonResponse


def request_failed(code, info, status_code=400):
    return JsonResponse({
        "code": code,
        "info": info
    }, status=status_code)


def request_success(data={}):
    response_data = {
        "code": 0,
        "info": "Succeed",
        **data
    }
    return JsonResponse(
        response_data,
        json_dumps_params={"ensure_ascii": False},  # 关键参数
        charset="utf-8"  # 显式指定字符集（可选，默认已包含）
    )
    


BAD_METHOD = request_failed(-3, "Bad method", 405)
