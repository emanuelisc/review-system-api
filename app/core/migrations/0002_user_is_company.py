# Generated by Django 2.1.7 on 2019-03-14 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_company',
            field=models.BooleanField(default=False),
        ),
    ]