from django.db import models
from django.contrib.postgres.fields import ArrayField
from Query.models import Result

# from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    username = models.CharField(max_length=15, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=128, verbose_name='密码')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    email = models.EmailField(unique=True, null=True,
                              blank=True, verbose_name='邮箱')
    org = models.CharField(max_length=50, null=True,
                           blank=True, verbose_name='所属团体')
    Is_Department_Official = models.BooleanField(
        default=False, verbose_name='是否体干')
    Is_Contest_Official = ArrayField(
        models.IntegerField(), default=list, verbose_name='可管比赛列表', blank=True)
    Is_System_Admin = models.BooleanField(
        default=False, verbose_name='是否系统管理员')

    class Meta:
        ordering = ['create_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username

class Athlete(models.Model):
    User = models.OneToOneField(UserProfile,on_delete=models.SET_NULL,
                                 related_name='athlete_user', verbose_name='用户',unique=True,null=True,blank=True)
    real_name = models.CharField(max_length=55, verbose_name='真实姓名')



class Star(models.Model):
    User = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                             related_name='user', verbose_name='用户')
    Athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE,
                                 related_name='athlete', verbose_name='运动员')