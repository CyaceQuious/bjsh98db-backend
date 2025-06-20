from django.db import models
from Users.models import UserProfile, Athlete, Star
from Query.models import Result, Meet, Project
# Create your models here.

class AuthRequest(models.Model):
    Athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_auths')
    invited_reviewer = models.ForeignKey(
        UserProfile, on_delete=models.PROTECT, related_name='to_review_auths'
    )

    STATUS_PENDING = 0
    STATUS_APPROVED = 1
    STATUS_REJECTED = 2

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return f'{self.Athlete} invited {self.invited_reviewer} to review their auth request'   