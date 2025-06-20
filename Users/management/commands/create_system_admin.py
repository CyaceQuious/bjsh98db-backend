import secrets
import os
from django.core.management.base import BaseCommand, CommandError
from Users.models import UserProfile  # 替换your_app为你的应用名
from django.contrib.auth.hashers import make_password  # 导入密码加密函数

from django.conf import settings

class Command(BaseCommand):
    help = 'create system admin'
    def handle(self, *args, **options):
        username = 'admin_bjsh'
        password = "111111"
        # password = "L_1OhYGyQhoHS_6_"
        if UserProfile.objects.filter(username=username).exists():
            raise CommandError(f"Collision: user {username} already exists.")
        password_hash = make_password(password,salt="L_1OhYGyQhoHS_6_",hasher='default')
        UserProfile.objects.create(username=username, password=password_hash, Is_System_Admin=True)
        self.stdout.write(self.style.SUCCESS('create system admin success\n'))
        cred_file = os.environ.get(
            "SUPERUSER_CREDENTIAL_FILE",
            os.path.join(os.getcwd(), "superuser_credentials.txt")
        )

        # 临时把 umask 设为 0o177，保证文件权限为 rw------- (600)
        old_umask = os.umask(0o177)
        try:
            with open(cred_file, "w") as f:
                f.write(f"USERNAME: {username}\n")
                f.write(f"PASSWORD: {password}\n")
        finally:
            os.umask(old_umask)

        self.stdout.write(self.style.SUCCESS(
            f"Credentials saved to: {cred_file}"
        ))
