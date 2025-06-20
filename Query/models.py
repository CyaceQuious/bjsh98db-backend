from django.db import models

# Create your models here.

class Meet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    mid = models.PositiveIntegerField(unique=True, db_index=True)
    class Meta:
        ordering = ['-mid']
    @classmethod
    def get_next_mid(cls):
        """获取下一个可用mid"""
        max_mid = cls.objects.aggregate(models.Max('mid')).get('mid__max', 0)
        return max_mid + 1 if max_mid > 10000 else 10001

    def save(self, *args, **kwargs):
        """自动生成mid（如果未指定）"""
        if not self.mid:
            self.mid = self.get_next_mid()
        super().save(*args, **kwargs)
    
class Project(models.Model):
    contest = models.ForeignKey(Meet, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    leixing = models.CharField(max_length=100)
    zubie = models.CharField(max_length=100)
    xingbie = models.CharField(max_length=100)
    class Meta:
        unique_together = ('contest', 'name','leixing','zubie','xingbie')
    @property
    def combined_info(self):
        return f"{self.xingbie}{self.zubie}{self.name}{self.leixing}"
    def __str__(self):
        return self.combined_info


class Result(models.Model):
    RESULT_TYPE_CHOICES = [
        ('top8', '前八排名'),
        ('group', '组别成绩'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    result_type = models.CharField(max_length=10, choices=RESULT_TYPE_CHOICES)  # 新增类型字段
    name = models.CharField(max_length=100)
    result = models.CharField(max_length=50)  # 保持字符串类型，如"17:24.95"
    grade = models.CharField(max_length=20, blank=True)
    groupname = models.CharField(max_length=50)
    rank = models.IntegerField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True) 
    class Meta:
        indexes = [
            models.Index(fields=['result_type']),
            models.Index(fields=['groupname']),
            models.Index(fields=['name']),
        ]

