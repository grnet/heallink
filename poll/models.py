from django.db import models
from django.contrib.auth import models as authmodels

class SubjectArea(models.Model):
    name = models.CharField(max_length=200)
    ordering = models.IntegerField(null=False, db_index=True, unique=True)
    
    def __unicode__(self):
        return self.name

    @staticmethod
    def get_subject_areas():
        return [(sa.id, sa.name) for sa in SubjectArea.objects.all()]
        
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

    def empty(self):
        self.cart_item_set.all().delete()

    def __unicode__(self):
        return u"{} {}".format(self.created_at, self.modified_at)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_item_set')
    journal = models.ForeignKey(Journal)
    preference = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def delete_set(to_update, cart_item_set):
        cart_item_set.all().delete()
        for cart_item in to_update:
            cart_item.preference = cart_item.preference - 1
            cart_item.save()
    
    def __unicode__(self):
        return u"{} {} {}".format(self.cart.__unicode__(),
                                 self.journal.__unicode__(),
                                 self.preference.__unicode__())

class Instrument(models.Model):
    name = models.CharField(max_length=100)
    
class Project(models.Model):
    acronym = models.CharField(max_length=20)
    name = models.CharField(max_length=400)
    instrument = models.ForeignKey(Instrument)
    
class UserProfile(models.Model):
    user = models.OneToOneField(authmodels.User, related_name="user_profile",
                                unique=False)
    subject_area = models.ForeignKey(SubjectArea)
    first_time = models.BooleanField(default=True)
    cart = models.ForeignKey(Cart)
    project = models.ForeignKey(Project)
    
    def mark_in_cart(self, journals):
        cart = self.cart
        cart_items = cart.cart_item_set.select_related('journal').all()
        journals_in_cart = set([item.journal.issn for item in cart_items])
        for journal in journals:
            if journal.issn in journals_in_cart:
                journal.in_cart = True
            else:
                journal.in_cart = False
        return journals

    def initialize_cart(self, subject_area_id):
        if self.cart is not None:
            self.cart.cart_item_set.all().delete()
        if self.cart_id is None or self.cart_id == 0:
            cart = Cart()
            cart.save()
            self.cart = cart
            self.save()
        self.subject_area_id = subject_area_id
        journals = Journal.objects.filter(subject_area_id=subject_area_id)
        top_journals = journals.order_by('-downloads')[:100]
        for i, journal in enumerate(top_journals):
            cart_item = CartItem(cart=self.cart,
                                 journal=journal,
                                 preference=i+1)
            cart_item.save()
        self.first_time = False
        self.save()

        
    def __unicode__(self):
        return u"{} {}".format(self.user, self.subject_area)
