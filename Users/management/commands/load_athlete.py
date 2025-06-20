from django.core.management.base import BaseCommand
from django.db import transaction
from Query.models import Result
from Users.models import Athlete

class Command(BaseCommand):
    help = '从 Result 表中提取所有不同的 name，并为每个 name 创建 Athlete 实例'

    def handle(self, *args, **options):
        with transaction.atomic():
            # 查询所有不重复的运动员姓名
            names = (
                Result.objects
                .values_list('name', flat=True)
                .distinct()
            )

            created_count = 0
            for real_name in names:
                # 如果该姓名的 Athlete 已存在，则跳过
                athlete, created = Athlete.objects.get_or_create(
                    real_name=real_name,
                    defaults={'User': None}
                )
                if created:
                    created_count += 1

            self.stdout.write(
                self.style.NOTICE(f'共创建 {created_count} 个新的 Athlete')
            )
