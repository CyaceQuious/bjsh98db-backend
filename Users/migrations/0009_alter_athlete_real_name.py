# Generated by Django 5.1.3 on 2025-05-09 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0008_alter_athlete_real_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athlete',
            name='real_name',
            field=models.CharField(max_length=40, verbose_name='真实姓名'),
        ),
    ]
