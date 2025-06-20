# Generated by Django 5.1.3 on 2025-04-09 09:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Meet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('mid', models.PositiveIntegerField(db_index=True, unique=True)),
            ],
            options={
                'ordering': ['-mid'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Query.meet')),
            ],
            options={
                'unique_together': {('contest', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_type', models.CharField(choices=[('top8', '前八排名'), ('group', '组别成绩')], max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('result', models.CharField(max_length=50)),
                ('grade', models.CharField(blank=True, max_length=20)),
                ('groupname', models.CharField(max_length=50)),
                ('rank', models.IntegerField(blank=True, null=True)),
                ('score', models.FloatField(blank=True, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Query.project')),
            ],
            options={
                'indexes': [models.Index(fields=['result_type'], name='Query_resul_result__55a218_idx'), models.Index(fields=['groupname'], name='Query_resul_groupna_46dea8_idx'), models.Index(fields=['name'], name='Query_resul_name_114177_idx')],
                'constraints': [models.UniqueConstraint(fields=('project', 'name', 'groupname'), name='unique_result_per_project_group')],
            },
        ),
    ]
