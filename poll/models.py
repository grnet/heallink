from django.db import models
from django.contrib.auth import models as authmodels

from collections import defaultdict, Counter

from utils import SchulzeCalculator

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

    @classmethod
    def count_selected(cls):
        journals = Journal.objects.select_related('subject_area',
                                                  'publisher')
        counted = journals.annotate(num_selected=models.Count('cart_item'))
        filtered = counted.filter(num_selected__gt=0)
        return filtered.order_by('-num_selected')

    @classmethod
    def count_schulze(cls):
        pairwise_matrix = defaultdict(Counter)        
        carts = Cart.objects.all()
        ballots = []
        for cart in carts:
            items = cart.cart_item_set.order_by('preference')
            items = items.select_related('journal', 'journal__subject_area',
                                         'journal__publisher')
            ballots.append([item.journal for item in items])
        print "Number of ballots:", len(ballots)
        sc = SchulzeCalculator(ballots)
        return sc.results

    @classmethod
    def count_range(cls):
        results = Counter()
        carts = Cart.objects
        counted = carts.annotate(num_items=models.Count('cart_item_set'))
        filtered = counted.filter(num_items__gt=0)
        biggest_cart = filtered.order_by('-num_items')[0]
        top_score = biggest_cart.num_items
        for cart in filtered:
            items = cart.cart_item_set.select_related('journal',
                                                      'journal__subject_area',
                                                      'journal__publisher')
            for item in items:
                journal = item.journal
                results[journal] += top_score - item.preference + 1
        return results.most_common()
        
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
    journal = models.ForeignKey(Journal, related_name='cart_item')
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
        return u"{} {} {}".format(self.cart,
                                  self.journal,
                                  self.preference)
class Instrument(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name
    

class Institute(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name
    
class Project(models.Model):
    acronym = models.CharField(max_length=20)
    name = models.CharField(max_length=400)
    institute = models.ForeignKey(Institute)
    instrument = models.ForeignKey(Instrument)

    def __unicode__(self):
        return u"{} {}".format(self.acronym, self.name)
    
class UserProfile(models.Model):
    user = models.OneToOneField(authmodels.User, related_name="user_profile")
    subject_area = models.ForeignKey(SubjectArea)
    first_time = models.BooleanField(default=True)
    cart = models.OneToOneField(Cart, related_name="user_profile")
    project = models.ForeignKey(Project)
    
    def mark_in_cart(self, journals):
        cart = self.cart
        cart_items = cart.cart_item_set.select_related('journal').all()
        journals_in_cart = set([item.journal.id for item in cart_items])
        for journal in journals:
            if journal.id in journals_in_cart:
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
