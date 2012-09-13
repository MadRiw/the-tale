# coding: utf-8
import datetime
import postmarkup
import markdown

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from forum.conf import forum_settings

class Category(models.Model):

    caption = models.CharField(max_length=256, blank=False, null=False)

    slug = models.CharField(max_length=32, blank=False, null=False, db_index=True)

    order = models.IntegerField(default=0, null=False, blank=True)

    def __unicode__(self): return self.slug


class SubCategory(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    category = models.ForeignKey(Category, null=False)

    slug = models.CharField(max_length=32, blank=False, null=False, db_index=True)

    caption = models.CharField(max_length=256, blank=False, null=False)

    order = models.IntegerField(default=0, null=False, blank=True)

    updated_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    threads_count = models.IntegerField(default=0, null=False)

    last_poster = models.ForeignKey(User, null=True, blank=True, related_name='+')

    posts_count = models.BigIntegerField(default=0, null=False)

    closed = models.BooleanField(default=False) # if True, only staff can create themes in this subcategory

    def __unicode__(self): return self.slug


class Thread(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    subcategory = models.ForeignKey(SubCategory, null=False)

    caption = models.CharField(max_length=256, blank=False, null=False)

    author =  models.ForeignKey(User, null=True, related_name='+')

    last_poster = models.ForeignKey(User, null=True, related_name='+')

    posts_count = models.BigIntegerField(default=0, null=False)

    updated_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    class Meta:
        permissions = (("moderate_thread", "Может редактировать темы на форуме"), )

    def get_absolute_url(self):
        return reverse('forum:threads:show', args=[self.id])

    @property
    def pages_count(self):
        pages_count = (self.posts_count + 1) / forum_settings.POSTS_ON_PAGE
        if (self.posts_count + 1) % forum_settings.POSTS_ON_PAGE:
            pages_count += 1
        return pages_count

class MARKUP_METHOD:
    POSTMARKUP = 0
    MARKDOWN = 1

MARKUP_METHOD_CHOICES = ( (MARKUP_METHOD.POSTMARKUP, 'bb-code'),
                          (MARKUP_METHOD.MARKDOWN, 'markdown') )


class Post(models.Model):

    thread = models.ForeignKey(Thread, null=False)

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    updated_at = models.DateTimeField(auto_now=True, null=False, default=datetime.datetime(2000, 1, 1))

    author = models.ForeignKey(User, null=True)

    text = models.TextField(null=False, blank=True, default='')

    markup_method = models.IntegerField(default=MARKUP_METHOD.POSTMARKUP, choices=MARKUP_METHOD_CHOICES, null=False)

    class Meta:
        permissions = (("moderate_post", "Может редактировать сообщения пользователей"), )

    @property
    def html(self):
        if self.markup_method == MARKUP_METHOD.POSTMARKUP:
            return postmarkup.render_bbcode(self.text)
        elif self.markup_method == MARKUP_METHOD.MARKDOWN:
            return markdown.markdown(self.text)
