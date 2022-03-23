from cgitb import text
from pyexpat import model
from turtle import title
from django.db import models
from django.contrib.auth.models import User
from datetime import *
from datetime import datetime, timedelta
from django.db.models.aggregates import Sum
from django.db.models.query import QuerySet
from django.db.models.fields import DateField, TextField
from django.forms import CharField, Textarea
from django.utils import timezone, translation
import decimal
from django.apps import config
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
import math
import pendulum
import sys

class SoftDeletionQuerySet(QuerySet):
    def delete(self):
        sys.setrecursionlimit(10000)
        success = True

        rel_updated = list()
        found_related = False
        # child_deleter(self.model)

        if success:
            return super(SoftDeletionQuerySet,self).update(is_active=False,is_deleted=True,updated=pendulum.now())
        else:
            for rel in rel_updated:
                rel.update(is_active=True, is_deleted=False)
        if not found_related:
            return super(SoftDeletionQuerySet,
                         self).update(is_active=False,
                                      is_deleted=True,
                                      updated=pendulum.now())

    def restore(self):
        success = True
        rel_updated = list()
        found_related = False

        if success:
            return super(SoftDeletionQuerySet,
                         self).update(is_active=True,
                                      is_deleted=False,
                                      updated=pendulum.now())
        else:
            for rel in rel_updated:
                rel.update(is_active=False, is_deleted=True)

        if not found_related:
            return super(SoftDeletionQuerySet,
                         self).update(is_active=True,
                                      is_deleted=False,
                                      updated=pendulum.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.both = kwargs.pop('both', False)
        self.dead = kwargs.pop('dead', False)
        self.alive = kwargs.pop('alive', False)
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive:
            return SoftDeletionQuerySet(self.model).filter(is_deleted=False)

        if self.both:
            return SoftDeletionQuerySet(self.model)

        if self.dead:
            return SoftDeletionQuerySet(self.model).filter(is_deleted=True)

        return SoftDeletionQuerySet(self.model)

    def delete(self):
        return self.get_queryset().update(is_deleted=True,
                                          is_active=False,
                                          updated=pendulum.now())

    def hard_delete(self):
        return self.get_queryset().hard_delete()

class ModelIsDeletable(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    objects = SoftDeleteManager(alive=True)
    objects_dead = SoftDeleteManager(dead=True)
    objects_alive = SoftDeleteManager(alive=True)
    objects_both = SoftDeleteManager(both=True)


    def soft_delete(self):
        self.is_deleted = True
        self.is_active = False
        self.updated = pendulum.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.is_active = True
        self.updated = pendulum.now()
        self.save()

    def is_deletable(self):
        # get all the related object
        for rel in self._meta.get_fields():
            try:
                # check if there is a relationship with at least one related object
                related = rel.related_model.objects.filter(
                    **{rel.field.name: self})
                if related.exists():
                    # if there is return a Tuple of flag = False the related_model object
                    return False, related
            except AttributeError:  # an attribute error for field occurs when checking for AutoField
                pass  # just pass as we dont need to check for AutoField
        return True, None

    def whenpublished(self):
        now = timezone.now()
        diff = now - self.created
        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds
            if seconds == 1:
                return str(seconds) + "second ago"
            else:
                return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)
            if minutes == 1:
                return str(minutes) + " minute ago"
            else:
                return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)
            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days = diff.days
            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"

        if diff.days >= 30 and diff.days < 365:
            months = int(math.floor(diff.days / 30))
            if months == 1:
                return str(months) + " month ago"
            else:
                return str(months) + " months ago"

        if diff.days >= 365:
            years = int(math.floor(diff.days / 365))
            if years == 1:
                return str(years) + " year ago"
            else:
                return str(years) + " years ago"

    def whenupdated(self):
        now = timezone.now()
        diff = now - self.updated
        if diff.days == 0 and 0 <= diff.seconds < 60:
            seconds = diff.seconds
            if seconds == 1:
                return str(seconds) + "second ago"
            else:
                return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)
            if minutes == 1:
                return str(minutes) + " minute ago"
            else:
                return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)
            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"

        if diff.days >= 30 and diff.days < 365:
            months = int(math.floor(diff.days / 30))
            if months == 1:
                return str(months) + " month ago"
            else:
                return str(months) + " months ago"

        if diff.days >= 365:
            years = int(math.floor(diff.days / 365))
            if years == 1:
                return str(years) + " year ago"
            else:
                return str(years) + " years ago"

    class Meta:
        abstract = True


class Region(ModelIsDeletable):
    name = models.CharField(max_length=200, null=False, blank=False)

    class Meta:
        verbose_name = u'Region'
        verbose_name_plural = u'Regions'

    def __str__(self):
        return self.name

USER_TYPE_CHOICES = (
    (1, "STUDENT"),
    (2, "DEVELOPER")
)

class UserProfile(ModelIsDeletable):
    """Model definition for UserProfile."""
    user = models.ForeignKey(User,related_query_name="profile", on_delete=models.DO_NOTHING)
    middle_name = models.CharField(max_length=100,null=True,blank=True)
    phone_number = models.CharField(max_length=50,null=True,blank=True)
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES,null=True,blank=True)
    location = models.ForeignKey(Region, on_delete=models.DO_NOTHING,null=True,blank=True)

    class Meta:
        """Meta definition for UserProfile."""
        permissions = (
            ("can_change_password","Can change password"),
        )
        verbose_name = 'UserProfile'
        verbose_name_plural = 'UserProfiles'

    def __str__(self):
        """Unicode representation of UserProfile."""
        return self.get_full_name()
    
    def get_full_name(self):
        if self.user:
            first_name = self.user.first_name if self.user.first_name else ''
            last_name = self.user.last_name if self.user.last_name else ''
            middle_name = self.middle_name if self.middle_name else ''
            return first_name.capitalize() + " " + middle_name.capitalize() + " " + last_name.capitalize()
        else:
            return self.user.username
    
    def get_user_registered_tag(self):
        if self.user:
            tags = UserTag.objects.filter(user=self.user,is_active=True,is_deleted=False).values_list("tag__name")
            return [x[0] for x in tags]
        else:
            return [] 

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

class Tag(ModelIsDeletable):
    """Model definition for Tag."""
    name = models.CharField(max_length=100)
    description = models.TextField(null=True,blank=True)

    class Meta:
        """Meta definition for Tag."""

        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        """Unicode representation of Tag."""
        return self.name

class UserTag(ModelIsDeletable):
    """Model definition for UserTag."""
    user = models.ForeignKey(User,related_name="usertag", on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


    class Meta:
        """Meta definition for UserTag."""

        verbose_name = 'UserTag'
        verbose_name_plural = 'UserTags'

    def __str__(self):
        """Unicode representation of UserTag."""
        return f"{self.user.username} - {self.tag.name}"

class StudentPost(ModelIsDeletable):
    """Model definition for StudentPost."""
    owner = models.ForeignKey(User,related_name='user_post',on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    tags = models.CharField(max_length=200)

    class Meta:
        """Meta definition for StudentPost."""

        verbose_name = 'StudentPost'
        verbose_name_plural = 'StudentPosts'

    def __str__(self):
        """Unicode representation of StudentPost."""
        return self.title
    
    def get_post_user_related(self):
        users = User.objects.filter(profile__location=self.owner.profile.location).exclude(id=self.owner.id)
        return users

class PostComment(ModelIsDeletable):
    """Model definition for PostComment."""
    student_post = models.ForeignKey(StudentPost,related_name='post_comment',on_delete=models.CASCADE)
    owner = models.ForeignKey(User,related_name='post_comment',on_delete=models.CASCADE)
    description = models.TextField(null=True,blank=True)

    class Meta:
        """Meta definition for PostComment."""

        verbose_name = 'PostComment'
        verbose_name_plural = 'PostComments'

    def __str__(self):
        """Unicode representation of PostComment."""
        return f"{self.owner} - {self.description}"
