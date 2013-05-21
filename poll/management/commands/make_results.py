#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import poll
from poll.models import Journal

from django.db import transaction

from optparse import make_option

import sys
import os
import csv
import random
import string

class Command(BaseCommand):
    help = """Produces poll results.
Outputs journals, in decreasing order, in CSV format to standard output.
    """
    option_list = BaseCommand.option_list + (
        make_option('-s',
                    '--selected',
                    action='store_true',
                    dest='selected',
                    default=True,
                    help='simple selection count',
                ),
        make_option('-r',
                    '--range',
                    action='store_true',
                    dest='range',
                    help='preference counting (range voting)',
                ),        
    )
    pth = os.path.abspath(poll.__path__[0])
        
    def count_selected(self):
        results = Journal.count_selected()
        r_writer = csv.writer(sys.stdout)
        for result in results:
            r_writer.writerow([
                result.issn,
                result.title.encode('utf-8'),
                result.url,
                result.downloads,
                result.subject_area.name.encode('utf-8'),
                result.publisher.name.encode('utf-8'),
                result.num_selected
            ])

    def count_range(self):
        results = Journal.count_range()
        r_writer = csv.writer(sys.stdout)
        for result in results:
            r_writer.writerow([
                result[0].issn,
                result[0].title.encode('utf-8'),
                result[0].url,
                result[0].downloads,
                result[0].subject_area.name.encode('utf-8'),
                result[0].publisher.name.encode('utf-8'),
                result[1]
            ])
                        
    def handle(self, *args, **options):
        if options['range']:
            self.count_range()
        elif options['selected']:
            self.count_selected()

        
        
