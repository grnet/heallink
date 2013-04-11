from django.db import models
from django.contrib.auth import models as authmodels

class SubjectArea(models.Model):
    name = models.CharField(max_length=200)
    ordering = models.IntegerField(null=False, db_index=True, unique=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["ordering"]
        
class Publisher(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name
    
class Journal(models.Model):
    issn = models.CharField(max_length=9)
    title = models.CharField(max_length=300)
    url = models.CharField(max_length=200)
    downloads = models.IntegerField(null=True)
    subject_area = models.ForeignKey(SubjectArea)
    publisher = models.ForeignKey(Publisher)

    def __unicode__(self):
        return u"{} {} {} {} {} {}".format(self.issn,
                                           self.title,
                                           self.url,
                                           self.downloads,
                                           self.subject_area,
                                           self.publisher)
    
class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)    
    modified_at = models.DateTimeField(auto_now=True)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_item__set')
    journal = models.ForeignKey(Journal)
    preference = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{} {} {}".format(self.cart.__unicode__(),
                                 self.journal.__unicode__(),
                                 self.preference.__unicode__())
    
class UserProfile(models.Model):
    user = models.OneToOneField(authmodels.User, related_name="user_profile",
                                unique=False)
    subject_area = models.ForeignKey(SubjectArea)
    cart = models.ForeignKey(Cart)
    
    def __unicode__(self):
        return u"{} {}".format(self.user, self.subject_area)
