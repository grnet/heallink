from django.core.management.base import BaseCommand, CommandError
import poll
from poll.models import UserProfile, Cart, CartItem, Journal
from django.contrib.auth.models import User

from optparse import make_option

import os
import csv

class Command(BaseCommand):
    args = '[-c]'
    help = 'Initialises user data'
    pth = os.path.abspath(poll.__path__[0])
    
    option_list = BaseCommand.option_list + (
        make_option('-c',
                    '--carts',
                    action='store_true',
                    dest='carts',
                    default=False,
                    help='Create user carts'),
        )

    def create_carts(self):
        users_file_path = os.path.join(Command.pth,
                                       'fixtures',
                                       'users.csv')
        with open(users_file_path, 'rb') as users_file:
            u_reader = csv.reader(users_file)
            for row in u_reader:
                if User.objects.filter(username=row[0]).count() != 0:
                    u = User.objects.filter(username=row[0])[0]
                    up = u.user_profile
                    if up.cart_id is None or up.cart_id == 0:
                        cart = Cart()
                        cart.save()
                        up.cart = cart
                        up.save()
                        sa = up.subject_area
                        journals = Journal.objects.filter(subject_area=sa)
                        top_journals = journals.order_by('-downloads')[:100]
                        for i, journal in enumerate(top_journals):
                            cart_item = CartItem(cart=cart,
                                                 journal=journal,
                                                 preference=i+1)
                            cart_item.save()
                        
    def handle(self, *args, **options):
        if options['carts']:
            self.create_carts()

        
        
