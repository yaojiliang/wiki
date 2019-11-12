import html

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tools.logging_check import logging_check, get_user_by_request
import json

from topic.models import Topic
from user.models import UserProfile


@logging_check('POST','DELETE')
def topics(request, author_id):
    if request.method == "POST":
        # 发表博客
        # request.user拿到的是一个对象
        author = request.user
        # print(author)# UserProfile object
        if author.username != author_id:
            result = {"code": 30101, 'error': 'The author is error!'}
            return JsonResponse(result)
        json_str = request.body
        json_obj = json.loads(json_str)
        title = json_obj.get('title')
        # 注意 xss 攻击(恶意提交js代码)-->解决转义
        title = html.escape(title)
        category = json_obj.get('category')
        # category = html.escape(category)
        if category not in ['tec', 'no-tec']:
            result = {'code': 30102, 'error': 'Thanks,your category is error !!'}
            return JsonResponse(result)
        limit = json_obj.get('limit')
        if limit not in ['private', 'public']:
            result = {'code': 30103, 'error': 'Thanks,your limit is error!!'}
            return JsonResponse(result)
        # 带样式的文章内容
        content = json_obj.get('content')
        # 　纯文本　文章内容　－用于做文章简介的切片
        content_text = json_obj.get('content_text')
        introduce = content_text[:30]
        # 创建topic
        Topic.objects.create(title=title, limit=limit, category=category, content=content, introduce=introduce,
                             author=author)
        result = {'code': 200, 'username': author.username}

        return JsonResponse(result)

    if request.method == "GET":
        # 获取 用户文章数据
        # /v1/topics/guoxiaonao - guoxiaonao的所有文章
        # /v1/topics/guoxiaonao?category=tec|no-tec 查看具体种类
        # /v1/topics/guoxiaonao?t_id=33 查看具体文章
        # 1, 访问当前博客的访问者  visitor
        # 2, 当前被访问的博客的博主 author
        authors = UserProfile.objects.filter(username=author_id)
        if not authors:
            result = {'code': 30104, 'error': 'The author is not existed !'}
            return JsonResponse(result)
        # 当前被访问的博客博主
        author = authors[0]

        # 访问者
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username

        t_id = request.GET.get('t_id')
        if t_id:
            t_id = int(t_id)
            # 获取指定文章的详情页
            # 生成标记为 True 为博主访问自己， False为陌生访客访问博主
            is_self = False
            if author_id == visitor_username:
                # 博主本人访问自己的博客
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    print('--get t_id error--')
                    print(e)
                    result = {'code': 30108, 'error': 'No topic'}
                    return JsonResponse(result)
            else:
                # 非博主访问当前博客
                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    result = {'code': 30109, 'error': 'No topic visitor !'}
                    return JsonResponse(result)
            # 生成具体返回值
            res = make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)

        else:
            # 列表页的需求
            category = request.GET.get('category')
            if category in ['tec', 'no-tec']:
                # 按种类筛选
                if author_id == visitor_username:
                    author_topics = Topic.objects.filter(author_id=author_id, category=category)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id, limit='public', category=category)

            else:
                # 全量【不分种类】筛选
                if author_id == visitor_username:
                    # 博主访问自己的博客, 作者文章全都返回
                    author_topics = Topic.objects.filter(author_id=author_id)
                else:
                    # 陌生访客访问他人博客, 只返回公开权限的
                    author_topics = Topic.objects.filter(author_id=author_id, limit='public')

            res = make_topics_res(author, author_topics)
            return JsonResponse(res)

    if request.method == 'DELETE':
        # 删除博客文章
        user = request.user
        if user.username != author_id:
            # 检查token中的用户名和前端访问url中的用户名是否一致
            result = {'code': 30105, 'error': 'Your author_id is error!!'}
            return JsonResponse(result)
        topic_id = request.GET.get('topic_id')
        if not topic_id:
            return JsonResponse({'code': 10009, 'error': '请给我文章id'})
        try:
            topic = Topic.objects.get(id=int(topic_id))
        except Exception as e:
            print('topic--delete--error--', e)
            return JsonResponse({'code': 30107, 'error': 'The topic is not exited!'})
        res = {'code': 200, 'msg': '删除成功!'}
        topic.delete()
        return JsonResponse(res)


def make_topics_res(author, author_topics):
    # 生成文章列表值
    res = {"code": 200, 'data': {}}
    res['data']['nickname'] = author.nickname
    res['data']['topics'] = []
    for topic in author_topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['introduce'] = topic.introduce
        d['category'] = topic.category
        d['created_time'] = topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
        d['author'] = author.nickname
        res['data']['topics'].append(d)
    return res



def make_topic_res(author, author_topic, is_self):
    #获取上一篇文章的id 和title
    if is_self:
        #博主访问自己的博客
        #next_topic 大于当前文章id的第一个
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author).first()
        #last_topic 小于当前文章id的最后一个
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author).last()
    else:
        #访客访问当前博客
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author, limit='public').first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author, limit='public').last()

    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None

    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title
    else:
        last_id = None
        last_title = None

    #获取下一篇文章的id 和title

    res = {'code': 200, 'data':{}}
    res['data']['title'] = author_topic.title
    res['data']['nickname'] = author.nickname
    res['data']['content'] = author_topic.content
    res['data']['introduce'] = author_topic.introduce
    res['data']['category'] = author_topic.category
    res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    res['data']['author'] = author.nickname
    res['data']['next_id'] = next_id
    res['data']['next_title'] = next_title
    res['data']['last_id'] = last_id
    res['data']['last_title'] = last_title
    #留言
    # 添加留言显示
    # 获取当前文章的所有留言
    all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')
    m_count = 0
    # 留言专属容器
    msg_list = []
    # 回复专属容器
    reply_home = {}
    for message in all_messages:
        m_count += 1
        if message.parent_message:
            # 回复
            reply_home.setdefault(message.parent_message, [])
            reply_home[message.parent_message].append(
                {'msg_id': message.id, 'content': message.content, 'publisher': message.publisher.nickname,
                 'publisher_avatar': str(message.publisher.avatar),
                 'created_time': message.created_time.strftime('%Y-%m-%d %H:%M:%S')})

        else:
            # 留言
            msg_list.append({'id': message.id, 'content': message.content, 'publisher': message.publisher.nickname,
                             'publisher_avatar': str(message.publisher.avatar),
                             'created_time': message.created_time.strftime('%Y-%m-%d %H:%M:%S'), 'reply': []})

    # 关联 留言及回复
    for m in msg_list:
        if m['id'] in reply_home:
            m['reply'] = reply_home[m['id']]

    res['data']['messages'] = msg_list
    res['data']['messages_count'] = m_count
    return res

def find_father(input_list):
    home = {}
    parent_list = []
    for data in input_list:
        if data['parent_id'] == 0:
            #爹
            parent_list.append({'id':data['id']})
        else:
            #孩子们
            p_id = data['parent_id']
            if p_id not in home:
                home[p_id] = []
                home[p_id].append({'id':data['id']})
            else:
                home[p_id].append({'id': data['id']})
            # 以下两句可以替代上面的if - else 判断
            # home.setdefault(p_id,[])# 设置默认值
            # home[p_id].append({'id':data['id']})

    for f in parent_list:
        if f['id'] in home:
            f['children'] = home[f['id']]

    return parent_list