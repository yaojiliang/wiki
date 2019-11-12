from django.conf.urls import url

from wtoken import views

urlpatterns=[
    url(r'^$',views.tokens)
]