# Generated by Django 2.1.8 on 2019-04-08 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_validationtoken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='validationtoken',
            name='user',
        ),
        migrations.AddField(
            model_name='validationtoken',
            name='user_email',
            field=models.CharField(default='testas@testas.testas', max_length=255),
            preserve_default=False,
        ),
    ]
