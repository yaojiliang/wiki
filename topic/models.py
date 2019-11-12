from django.db import models

# Create your models here.
from user.models import UserProfile


class Topic(models.Model):
    title=models.CharField('文章主题',max_length=50)
    # 技术类文章 or no-tec 非技术类文章
    category=models.CharField('博客的分类',max_length=20)
    # 公开博客 or or private 私有博客
    limit=models.CharField('文章权限',max_length=10)
    introduce=models.CharField('博客简介',max_length=90)
    content=models.TextField('博客内容')
    created_time=models.DateTimeField('博客创建时间',auto_now_add=True)
    updated_time=models.DateTimeField('博客修改时间',auto_now=True)
    author=models.ForeignKey(UserProfile)

    class Meta:
        db_table='topic'
