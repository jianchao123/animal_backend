# coding:utf-8
import traceback
from functools import wraps
from rest_framework.response import Response

from AppError import ApiArgsError, AppErrorBase

import logging
logger = logging.getLogger(__name__)


def make_error_resp(error_code, error_msg):
    """
    构造错误返回值

    args:
        error_code: 错误码
        error_msg: 错误信息

    return:
        字典.
    """
    return make_resp({}, error_code, error_msg)


def make_correct_resp(data={}):
    """
    构造正确返回值

    args:
        data: 返回数据

    return:
        字典.
    """
    return make_resp(data, 0, '')


def make_resp(data, code, detail):
    """
    构造返回值

    args:
        data: 返回数据
        code: 错误码
        detail: 错误信息

    return:
        字典.
    """
    return {
        'data': data,
        'code': code,
        'detail': detail
    }


def get_check_args(request, args_name):
    '''
    校验GET请求中的参数. args_name长度为0时不解析参数, 返回None.

    args:
        request: flask.request实体
        args_name: 参数名称列表，例如['name', 'password']

    return:
        解析得到的参数字典. 可为None.

    exception:
        ApiArgsError.
    '''
    if not args_name:
        return None

    req_args = request.query_params
    non_exists_name = is_argument_exists(req_args, args_name)
    if non_exists_name:
        raise ApiArgsError(2, '缺少参数 {}'.format(non_exists_name))
    return req_args


def is_argument_exists(req_args, args_name):
    """
    判断参数是否存在.

    args:
        req_args: 请求参数字典
        args_name: 必需的参数名称列表

    return:
        None. 所有参数都存在
        string. 不存在的参数名
    """
    for arg_name in args_name:
        if arg_name not in req_args:
            return arg_name
    return None


def post_check_args(request, args_name):
    '''
    校验POST请求中的参数. args_name长度为0时不解析参数, 返回None.

    args:
        request: flask.request实体
        args_name: 参数名称列表，例如['name', 'password']

    return:
        解析得到的参数字典. 可为None.

    exception:
        ApiArgsError.
    '''
    if 0 == len(args_name):
        return None

    req_args = request.data

    non_exists_name = is_argument_exists(req_args, args_name)
    if non_exists_name:
        raise ApiArgsError(2, '缺少参数 {}'.format(non_exists_name))
    return req_args


# 可删除
def set_response_key(request):
    cookies = []
    cookie_dict = {
        "sessionid": "",
        "csrftoken": ""
    }

    if request.META["HTTP_COOKIE"]:
        cookies = request.META["HTTP_COOKIE"].replace(" ", "").split(";")

    for row in cookies:
        tmp = row.split("=")
        if len(tmp) > 1:
            cookie_dict[tmp[0]] = tmp[1]
    Origin =  "*"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "sessionid={}; csrftoken={}; tabstyle=raw-tab".format(
            cookie_dict["sessionid"], cookie_dict["csrftoken"]),
        "X-CSRFTOKEN": "{}".format(cookie_dict["csrftoken"]),
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Origin": Origin
    }

    return headers


def post_require_check(args_name):
    '''
    装饰器, 校验POST请求中的参数, 参数通过http body 传递
    '''

    def post_require_check_wrapper(fn):
        '''
        校验POST请求中的参数，通过则用调用fn
        '''

        @wraps(fn)
        def __wrapper(self, request, *args, **kwargs):
            try:
                logger.info(request.COOKIES)
                if args_name:
                    post_check_args(request, args_name)
                data = fn(self, request, *args, **kwargs)

                return Response(status=200, data=make_correct_resp(data))
            except AppErrorBase as ex:
                return Response(status=200,
                                data=make_error_resp(ex.error_code,
                                                     ex.error_msg))
            except:
                logger.error(traceback.format_exc())
                return Response(status=500,
                                data=make_error_resp(999, u'unknown error'))

        return __wrapper

    return post_require_check_wrapper


def get_require_check(args_name):
    '''
    装饰器, 校验GET请求中的参数, 参数在http url中
    '''

    def get_require_check_wrapper(fn):
        '''
        校验GET请求中的参数，通过则调用fn
        '''

        @wraps(fn)
        def __wrapper(self, request, *args, **kwargs):
            try:
                logger.info(request.COOKIES)
                if args_name:
                    get_check_args(request, args_name)
                data = fn(self, request, *args, **kwargs)
                return Response(status=200, data=make_correct_resp(data))
            except AppErrorBase as ex:
                return Response(status=200,
                                data=make_error_resp(ex.error_code,
                                                     ex.error_msg))
            except:
                logger.error(traceback.format_exc())
                return Response(status=500,
                                data=make_error_resp(999, u'unknown error'))

        return __wrapper

    return get_require_check_wrapper
