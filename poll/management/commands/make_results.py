#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import poll
from poll.models import Journal, UserProfile

from django.db import transaction

from optparse import make_option

import sys
import os
import csv
import random
import string

class Command(BaseCommand):
    help = """Produces poll results."""
    option_list = BaseCommand.option_list + (
        make_option('-c',
                    '--count',
                    action='store_true',
                    dest='count',
                    help='count results',
                ),
        make_option('-t',
                    '--took_part',
                    action='store_true',
                    dest='participants',
                    help='list participants',
                ),                
    )
    pth = os.path.abspath(poll.__path__[0])
        
    def count_results(self):
        results = Journal.count_results()
        r_writer = csv.writer(sys.stdout)
        r_writer.writerow([
            'issn',
            'title',
            'url',
            'downloads',
            'subject area',
            'publisher',
            'num selected',
            'num selected by institute',
            'points',
        ])
        results_per_journal = results['journal']
        results_per_journal_institute = results['journal_institute']
        results_range = results['range']
        for result in results['range'].most_common():
            journal = result[0]
            r_writer.writerow([
                journal.issn,
                journal.title.encode('utf-8'),
                journal.url,
                journal.downloads,
                journal.subject_area.name.encode('utf-8'),
                journal.publisher.name.encode('utf-8'),
                results_per_journal[journal],
                results_per_journal_institute[journal],
                result[1],
            ])

    def list_participants(self):
        results = UserProfile.list_participants()
        r_writer = csv.writer(sys.stdout)
        r_writer.writerow([
            'acronym',
            'name',
            'institute',
            'first name'
            'last_name',
            'email',
            'subject_area',
            'num_preferences',
            'took_part',
        ])
        for result in results:
            row = [
                result.project.acronym,
                result.project.name,
                result.project.institute.name,
                result.user.first_name,
                result.user.last_name,
                result.user.email,
                result.subject_area.name,
                str(result.num_preferences),
                str(not result.first_time),
            ]
            r_writer.writerow([ s.encode("utf-8") for s in row])
                     
    def handle(self, *args, **options):
        if options['count']:
            self.count_results()
        elif options['participants']:
            self.list_participants()

        
        
