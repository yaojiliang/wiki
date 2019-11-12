from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import UserProfile


class Message(models.Model):
    content=models.CharField('内容',max_length=50)
    created_time=models.DateTimeField('创建时间',auto_now_add=True)
    parent_message=models.IntegerField('关联的留言ID父留言',default=0)
    topic = models.ForeignKey(Topic)
    publisher = models.ForeignKey(UserProfile)

    class Meta:
        db_table='message'

