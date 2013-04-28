#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import poll
from poll.models import UserProfile, Cart, SubjectArea, Instrument, Project
from django.contrib.auth.models import User

from django.db import transaction

from optparse import make_option

import os
import csv

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

    def fix_name(self, s):
        fixed = s.decode('utf-8').capitalize()
        if fixed[-1] ==  u"σ":
            s[-1] = u'ς'
        return fixed
        
    @transaction.commit_on_success
    def create_users(self, users_file_path=None):
        if users_file_path is None:
            users_file_path = os.path.join(Command.pth,
                                           'fixtures',
                                           'users.csv')
        default_subject_area = SubjectArea.objects.filter(ordering=1)[0]
        with open(users_file_path, 'rb') as users_file:
            u_reader = csv.reader(users_file)
            for i, row in enumerate(u_reader):
                if i == 0:
                    continue
                email = row[-2]
                name = row[6]
                instrument_name = row[2]
                (instrument, created) = Instrument.objects.get_or_create(
                    name=instrument_name)
                project_name = row[3]
                project_acronym = row[4]
                (project, created) = Project.objects.get_or_create(
                    name=project_name,
                    acronym=project_acronym,
                    instrument=instrument)                
                institute = row[5]
                (first_name, last_name) = [self.fix_name(s)
                                           for s in (name + ' ').split(' ', 1)]
                for s in (first_name, last_name):
                    if s[-1] == u"σ":
                        s[-1] = u'ς'
                base_username = email.split('@')[0]
                username = base_username
                i = 2
                while User.objects.filter(username=username).exists():
                    username = "{}_{}".format(base_username, i)
                    i += 1
                u = User.objects.create_user(username=username,
                                             email=email.lower(),
                                             password=username)
                print first_name, last_name, base_username, username
                u.first_name = first_name
                u.last_name = last_name
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

        
        
