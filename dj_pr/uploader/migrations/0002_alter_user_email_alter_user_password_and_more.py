# Generated by Django 4.1 on 2023-09-10 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.TextField(),
        ),
    ]