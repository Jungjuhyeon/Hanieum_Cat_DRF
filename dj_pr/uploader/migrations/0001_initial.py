# Generated by Django 4.1 on 2023-09-03 19:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('userIdx', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.TextField(blank=True)),
                ('users_id', models.TextField(max_length=30, unique=True)),
                ('password', models.TextField(blank=True)),
                ('email', models.TextField(blank=True, unique=True)),
                ('phone', models.TextField(blank=True, unique=True)),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.TextField(blank=True, default='A', max_length=1)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Auth',
            fields=[
                ('phone', models.CharField(blank=True, max_length=11, primary_key=True, serialize=False)),
                ('username', models.TextField(blank=True)),
                ('auth', models.IntegerField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'auth_sms',
            },
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('photo', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pet',
            fields=[
                ('petIdx', models.AutoField(primary_key=True, serialize=False)),
                ('petname', models.TextField()),
                ('petage', models.IntegerField()),
                ('petgender', models.TextField()),
                ('petcomment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.TextField(blank=True, default='A', max_length=1)),
                ('userIdx', models.ForeignKey(db_column='userIdx', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Diagnosis',
            fields=[
                ('diagnosisIdx', models.AutoField(primary_key=True, serialize=False)),
                ('petresult', models.TextField(blank=True)),
                ('petresultper', models.TextField(blank=True)),
                ('diagday', models.DateTimeField(auto_now_add=True)),
                ('photo', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.TextField(blank=True, default='A', max_length=1)),
                ('petIdx', models.ForeignKey(blank=True, db_column='petIdx', on_delete=django.db.models.deletion.CASCADE, to='uploader.pet')),
            ],
        ),
    ]
