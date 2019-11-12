import random

from django.db import models

def choice_sign():
    s = ['开心!', '高兴!']
    return random.choice(s)


# Create your models here.
class UserProfile(models.Model):
    username=models.CharField('用户名',max_length=11,primary_key=True)
    nickname=models.CharField('昵称',max_length=30)
    email=models.EmailField('邮箱',max_length=50)
    password = models.CharField('密码',max_length=32)
    sign=models.CharField('个人签名',max_length=50,default=choice_sign)
    info=models.CharField('个人描述',max_length=150,default='')
    created_time=models.DateTimeField('创建时间',auto_now_add=True)
    updated_time=models.DateTimeField('更新时间',auto_now=True)
    login_time=models.DateTimeField('登录时间',null=True)
    #
    score = models.IntegerField('分类',null=True,default=0)
    # upload_to指定存储位置 MEDIA_ROOT+upload_to的值
    # wiki/media/avatar
    avatar =models.ImageField('头像',upload_to='avatar',default='')
    class Meta:
        db_table='user_profile'
