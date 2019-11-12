from django.conf.urls import url

from message import views

urlpatterns=[
    # URL : http://127.0.0.1:8000/v1/messages/<topic_id>
    url(r'^/(?P<topic_id>\d+)$',views.messages)
]