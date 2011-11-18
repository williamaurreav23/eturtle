from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.contrib.auth.models import User, Group

class ETurtleGroup(Group):
    GROUP_ADMIN = 'admin'
    GROUP_COURIER = 'courier'
    GROUP_CLIENT = 'client'

    @classmethod
    def get_group_or_raise(cls,group_name):
        try:
            return cls.objects.get(name=group_name)
        except cls.DoesNotExist:
            raise ImproperlyConfigured('You must create the base user groups:(%s,%s,%s)' % (cls.GROUP_ADMIN, cls.GROUP_COURIER, cls.GROUP_CLIENT))

    @classmethod
    def admin(cls):
        return cls.get_group_or_raise(cls.GROUP_ADMIN)

    @classmethod
    def courier(cls):
        return cls.get_group_or_raise(cls.GROUP_COURIER)

    @classmethod
    def client(cls):
        return cls.get_group_or_raise(cls.GROUP_CLIENT)

    class Meta:
        proxy = True

class ETModelBase(models.Model):
    date_created = models.DateTimeField(auto_now_add = True)
    date_modified = models.DateTimeField(auto_now = True)
    class Meta:
        abstract = True

class Courier(ETModelBase, User):
    STATE_ENUM = (
        (1, 'IDLE'),
        (2, 'STANDING_BY'),
        (3, 'PENDING'),
        (4, 'SHIPPING'),
    )
    state = models.IntegerField(choices = STATE_ENUM, default = 1)

    def __unicode__(self):
        return u'%s' % self.username

    class Meta:
        permissions = (
            ("api_access", "Can login via api and access api functions."),
            ("web_access", "Can login via browser and access the web application."),
        )

class Client(User):
    class Meta:
        proxy = True

class Package(ETModelBase):
    STATE_ENUM = [
        (1, 'NEW'),
        (2, 'PENDING'),
        (3, 'SHIPPING'),
        (4, 'SHIPPED'),
        (5, 'FAILED'),
    ]
    client = models.ForeignKey(User)

    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)

    state = models.IntegerField(choices = STATE_ENUM, default = 1)

    def __unicode__(self):
        return u'%s' % self.name

class Dispatch(ETModelBase):
    STATE_ENUM = [
        (1, 'PENDING'),
        (2, 'REJECTED'),
        (3, 'SHIPPING'),
        (4, 'SHIPPED'),
        (5, 'FAILED'),
    ]
    state = models.IntegerField(choices = STATE_ENUM, default = 1)
    courier = models.ForeignKey('Courier')
    package = models.ForeignKey('Package')

    class Meta:
        ordering = ('-date_created',)

    def __unicode__(self):
        return u'%s -> %s' % (self.package, self.courier)

