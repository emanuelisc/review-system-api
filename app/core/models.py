import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin

from django.conf import settings


def page_image_file_path(instance, filename):
    # Generate file path for new recipe image
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/pages/', filename)


def provider_service_image_file_path(instance, filename):
    # Generate file path for new service image
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/providers/services/', filename)


def provider_image_file_path(instance, filename):
    # Generate file path for new provider image
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/providers/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        # Creates and saves a new user
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        # Creates  and saves a new super user
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Custom user model that supports using email instead of username
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    provider_id = models.ForeignKey(
        'Provider',
        related_name='users',
        on_delete=models.CASCADE,
        null=True
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'


class PageCategory(models.Model):
    # Page category
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Page(models.Model):
    # Page object
    title = models.CharField(max_length=255)
    text = models.TextField()
    slug = models.CharField(max_length=255, blank=True)
    date = models.DateField(auto_now=True)
    categories = models.ManyToManyField('PageCategory')
    image = models.ImageField(null=True, upload_to=page_image_file_path)

    def __str__(self):
        return self.title


class ProviderService(models.Model):
    # Provicer services object
    title = models.CharField(max_length=255)
    description = models.TextField()
    provider = models.ForeignKey(
        'Provider',
        related_name='services',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        null=True, upload_to=provider_service_image_file_path)

    def __str__(self):
        return self.title


class Provider(models.Model):
    # Provider object
    title = models.CharField(max_length=255)
    description = models.TextField()
    admin_user = models.ForeignKey(
        'User', related_name='provider_admin', on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    is_confirmed = models.BooleanField(default=False)
    image = models.ImageField(null=True, upload_to=provider_image_file_path)

    def __str__(self):
        return self.title


class ProviderLog(models.Model):
    # Object for provider page logging
    date = models.DateField(auto_now=True)
    ip = models.CharField(max_length=255)
    country = country = models.CharField(max_length=255, blank=True)
    provider = models.ForeignKey('Provider', on_delete=models.CASCADE)


class ServiceLog(models.Model):
    # Object for provider page logging
    date = models.DateField(auto_now=True)
    ip = models.CharField(max_length=255)
    country = country = models.CharField(max_length=255, blank=True)
    service = models.ForeignKey('ProviderService', on_delete=models.CASCADE)


class ReviewLog(models.Model):
    # Object for provider page logging
    date = models.DateField(auto_now=True)
    ip = models.CharField(max_length=255)
    country = country = models.CharField(max_length=255, blank=True)
    review = models.ForeignKey('Review', on_delete=models.CASCADE)


class Ticket(models.Model):
    # Page object
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now=True)
    object_type = models.IntegerField(blank=True)
    object_id = models.IntegerField(blank=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


class Review(models.Model):
    # Provider object
    title = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.IntegerField(default=0)
    date = models.DateField(auto_now=True)
    categories = models.ManyToManyField('ReviewCategory')
    tags = models.ManyToManyField('HashTag')
    is_auto_confirmed = models.BooleanField(default=False)
    confirmation_text = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    image = models.ImageField(null=True, upload_to=provider_image_file_path)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


class RatingLog(models.Model):
    # Log to prevent user commenting multiple times
    review = models.ForeignKey('Review', on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.review


class ReviewCategory(models.Model):
    # Review category object
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class HashTag(models.Model):
    # Review tag object
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Comment(models.Model):
    # Review comment object
    content = models.TextField()
    parent = models.ForeignKey(
        'self', related_name='reply_set', null=True, on_delete=models.CASCADE)
    review = models.ForeignKey('Review', on_delete=models.CASCADE, default=1)
    date = models.DateField(auto_now=True)
    rating = models.IntegerField(default=0)
    is_auto_confirmed = models.BooleanField(default=False)
    confirmation_text = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    is_provider = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        content = str(self.content).rstrip(40)
        return content
