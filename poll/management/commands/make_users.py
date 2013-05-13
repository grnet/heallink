#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import poll
from poll.models import UserProfile, Cart, SubjectArea, Instrument, Project
from poll.models import Institute

from django.contrib.auth.models import User

from django.db import transaction

from optparse import make_option

import sys
import os
import csv
import random
import string

class Command(BaseCommand):
    help = """Initialises user data.
If no input file is given, reads users.csv from fixtures"""
    option_list = BaseCommand.option_list + (
        make_option('-i',
                    '--input',
                    action='store',
                    type='string',
                    dest='input_file',
                    help='set users file',
                ),
    )
    pth = os.path.abspath(poll.__path__[0])
        
    @transaction.commit_on_success
    def create_users(self, users_file_path=None):
        random.seed()
        if users_file_path is None:
            users_file_path = os.path.join(Command.pth,
                                           'fixtures',
                                           'users.csv')
        default_subject_area = SubjectArea.objects.filter(ordering=1)[0]
        with open(users_file_path, 'rb') as users_file:
            u_reader = csv.reader(users_file)
            u_writer = csv.writer(sys.stdout)
            for i, row in enumerate(u_reader):
                if i == 0:
                    continue
                row = [item.strip() for item in row]
                email = row[-2].lower()
                name = row[6]
                instrument_name = row[1]
                (instrument, created) = Instrument.objects.get_or_create(
                    name=instrument_name)
                institute_name = row[5]
                (institute, created) = Institute.objects.get_or_create(
                    name=institute_name)                
                project_name = row[3]
                project_acronym = row[4]
                (project, created) = Project.objects.get_or_create(
                    name=project_name,
                    acronym=project_acronym,
                    instrument=instrument,
                    institute=institute)                
                (first_name, last_name) = name.split(None, 1)
                base_username = email.split('@')[0].lower()
                username = base_username
                i = 2
                while User.objects.filter(username=username).exists():
                    username = "{}_{}".format(base_username, i)
                    i += 1
                u = User.objects.create_user(username=username,
                                             email=email)
                passwd = ''.join(random.choice(string.ascii_lowercase +
                                               string.digits)
                                 for x in range(10))
                u_writer.writerow([first_name, last_name, email,
                                   username, passwd])
                u.first_name = first_name
                u.last_name = last_name
                u.set_password(passwd)
                up = UserProfile()
                up.subject_area = default_subject_area
                up.project = project
                cart = Cart()
                up.user = u
                cart.save()
                up.cart = cart
                u.save()
                up.save()
                        
    def handle(self, *args, **options):
        self.create_users(options['input_file'])

        
        
