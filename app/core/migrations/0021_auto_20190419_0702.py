# Generated by Django 2.1.8 on 2019-04-19 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='categories',
            field=models.ManyToManyField(blank=True, to='core.PageCategory'),
        ),
    ]