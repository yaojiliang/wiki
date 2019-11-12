import redis
from django.http import JsonResponse

from user.models import UserProfile


def test(request):
    r = redis.Redis(host='127.0.0.1',port=6379,db=0,password='123456')
    try:
        with r.lock('guoxiaonao',blocking_timeout=3) as lock:
            # 对score字段进行　+1 操作
            u = UserProfile.objects.get(username='liang')
            u.score+=1
            u.save()
    except Exception as e:
        print('Lock failed')
    return JsonResponse({'code':200,'data':{}})