# Generated by Django 2.1.7 on 2019-03-21 21:11

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_page_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('slug', models.CharField(blank=True, max_length=255)),
                ('image', models.ImageField(null=True, upload_to=core.models.provider_image_file_path)),
            ],
        ),
        migrations.CreateModel(
            name='ProviderService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(null=True, upload_to=core.models.provider_service_image_file_path)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Provider')),
            ],
        ),
    ]