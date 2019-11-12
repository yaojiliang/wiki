import datetime
import hashlib
import json
from django.http import JsonResponse

# Create your views here.
from tools.logging_check import logging_check
from user.models import UserProfile
from wtoken.views import make_token

'''
    User模块　－ 如何做　同一时间只有一个用户登录
    
    方案：
        1,加个字段　－ loginStatus[0/1] -1已登录　0-未登录
        2,用户A 在浏览器a登录　loginStatus 0 - 1
        3,用户A 在浏览器b登录　怎么把loginStatus 1 - 0？？？？
        
        方案二：
        login_time Datetime:
        2,用户－登录t1 －＞login_time t1 ->token
        3,用户二次登录　t2 ->login_time t2 -token
        
        用户表添加　login_time DatetimeFiled
        用户执行登录时：
            1,用户表　更新　登录时间　为当前时间
            2,生成token时　在token中添加login_time
            [1,2步骤时间相等]
        
        校验token －　检查token中的login_time和用户表中的login_time
        是否相等；如果不等，则证明当前token生成后,又签发了新的token(有人登录过)
        此时，返回异常状态码告知用户"请重新登录"
        
        
'''


# 通过关键字判断那具体数据还是全部数据
@logging_check('PUT')
def users(request, username=None):
    if request.method == 'GET':
        # 格式:{‘code’:200, ‘data’:{‘nickname’:’abc’, ’sign’:’hell
        # ow’,  ‘info’: ‘hahahahah’}}
        # 拿数据
        if username:
            user = UserProfile.objects.filter(username=username).first()
            if user:
                # 拿具体用户数据
                # 有查询字符串[?nickname] or 没查询字符串
                # python的反射机制 判断对象里面有没有这个属性hasattr(user,'nickname')  判断对象有没有属性有没有值getattr()
                if request.GET.keys():
                    data = {}
                    for k in request.GET.keys():
                        if hasattr(user, k):
                            if k == 'password':
                                continue
                            v = getattr(user, k)
                            data[k] = v
                    res = {'code': 200, 'username': username, 'data': data}
                else:
                    #'avatar':str(user.avatar)}
                    res = {'code': 200, 'username': username,
                           'data': {'nickname': user.nickname, 'sign': user.sign, 'info': user.info,'avatar':str(user.avatar)}}
                return JsonResponse(res)
            else:
                return JsonResponse({'msg': '没有此用户'})
        else:
            users_data = []
            all_user = UserProfile.objects.all()
            for user in all_user:
                dic = {}
                dic['nickname'] = user.nickname
                dic['username'] = user.username
                dic['sign'] = user.sign
                dic['info'] = user.info
                users_data.append(dic)
            res = {'code': 200, 'data': users_data}
            return JsonResponse(res)

    elif request.method == 'POST':
        # 创建用户
        # 因为前端服务器是通过contentType:"application/json"请求的数据,
        # 而request.POST拿不到值,request.POST需要contentType是
        # Content-Type: (表单)application/x-www-form-urlencoded和数据格式要求： name=alex&age=18&gender=男
        # 所以拿值需要request.body--->不需要考虑contentType.
        json_str = request.body#'{...}'
        if not json_str:
            result = {'code': 10102, 'error': 'Please Give me data !'}
            return JsonResponse(result)

        json_obj = json.loads(json_str)#{...}
        username = json_obj.get('username')
        if not username:
            result = {'code': 10101, 'error': 'Please give me username~'}
            return JsonResponse(result)
        # 检查json中的dict中的key是否存在
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if password_1 != password_2:
            result = {'code': 10103, 'error': 'The password is error ! ! !'}
            return JsonResponse(result)
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 10104, 'error': 'The username is already exited ! '}
            return JsonResponse(result)
        # 生成散列的码
        pm = hashlib.md5()
        pm.update(password_1.encode())
        email = json_obj.get('email')
        # 创建用户
        # 并发
        try:
            UserProfile.objects.create(username=username, password=pm.hexdigest(), nickname=username, email=email)
        except Exception as e:
            print('---create error---')
            print(e)
            result = {'code': 10105, 'error': 'The username is already existed!!'}
            return JsonResponse(result)
        # 生成令牌
        login_time = datetime.datetime.now()
        token = make_token(username, 3600 * 24,login_time)
        # print('token',token)# b'...'
        # print('token ',token.decode())#'...'
        result = {'code': 200, 'data': {'token': token.decode()}, 'username': username}
        return JsonResponse(result)
    # 只有这个需要校验token
    elif request.method == 'PUT':
        # 更新:8000/v1/users/<username>
        if not username:
            res={'code':10108,'error':'Must be give me username !! '}
            return JsonResponse(res)
        json_str=request.body
        if json_str:
            # 反序列化成字典
            json_obj = json.loads(json_str)
            nickname=json_obj.get('nickname')
            sign=json_obj.get('sign')
            info=json_obj.get('info')

            # user=UserProfile.objects.filter(username=username).first()
            user = request.user

            to_update = False
            if user.nickname != nickname:
                to_update = True
            if user.info != info:
                to_update = True
            if user.sign != sign:
                to_update = True

            if to_update:
                # 更新
                user.sign =sign
                user.nickname=nickname
                user.info=info
                user.save()
            return JsonResponse({'code':200,'username':username})
        else:
            return JsonResponse({'msg':'请输入'})
    return JsonResponse({'code': 200})

@logging_check('POST')
def user_avater(request,username=None):
    if request.method != 'POST':
        result = {'code':10110,'error':"Plase use POST"}
        return JsonResponse(result)
    user =request.user
    if user.username != username:
        result={'code':10109,'error':'The username is error'}
        return JsonResponse(result)
    user.avatar=request.FILES['avatar']
    user.save()
    return JsonResponse({'code':200,'username':username})
