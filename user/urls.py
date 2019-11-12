from django.conf.urls import url

from user import views

urlpatterns=[
    # http://127.0.0.1:8000/v1/users
    # http://127.0.0.1:8000/v1/tokens
    url(r'^$',views.users),
    #　限制字符长度w{1,11} http://127.0.0.1:8000/v1/users/<username>
    # 关键字传参(?P<username>)
    url(r'^/(?P<username>\w{1,11})$',views.users),
    url(r'^/(?P<username>\w{1,11})/avatar$',views.user_avater),
]