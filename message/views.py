import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tools.logging_check import logging_check
from topic.models import Topic


@logging_check('POST')
def messages(request, topic_id):
    if request.method == 'POST':
        # 发表留言或者是回复
        json_str = request.body# 那json数据-->'{...}'
        json_obj = json.loads(json_str)# {...}
        # print(json_obj)# {'content': '<p>厉害啊<br></p>'}
        content = json_obj.get('content')# 拿字典的值
        parent_id = json_obj.get('parent_id', 0) #给了默认值

        # 参数检查
        # 此判断行不通－＞if not content:
        #     return JsonResponse({'code':30019,'error':'请输入评价'})
        # 检查topic是否存在
        try:
            # 获取topic对象，同时判断是否存在这个topic
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            result = {'code': 40101, 'error': 'No topic'}
            return JsonResponse(result)
        Message.objects.create(content=content,
                               parent_message=parent_id,
                               publisher=request.user,
                               topic=topic)
        # 1,外键属性赋值 赋对象
        # 2,赋值给外键字段名
        return JsonResponse({'code': 200})

    if request.method == 'GET':
        all_m = Message.objects.filter(topic_id=int(topic_id))# 拿到的queryset对象
        all_list = []
        for m in all_m:
            d = {}
            d['id'] = m.id
            d['content'] = m.content
            d['parent_message'] = m.parent_message
            d['publisher'] = m.publisher.username
            d['title'] = m.topic_id
            all_list.append(d)
        return JsonResponse({'code': 200, 'data': all_list})
