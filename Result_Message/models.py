from django.db import models
from Users.models import UserProfile
from Query.models import Result, Meet,Project

# Create your models here.

class ResultRequest(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_users')
    STATUS_PENDING = 0
    STATUS_APPROVED = 1
    STATUS_REJECTED = 2

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]
    apply_reason = models.CharField(max_length=300)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.CharField(max_length=300, null=True, blank=True)  
