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
        make_option('-p',
                    '--participants',
                    action='store_true',
                    dest='participants',
                    help='list participants results',
                ),                
    )
    pth = os.path.abspath(poll.__path__[0])
        
    def count_results(self):
        results = Journal.count_results()
        csv_file_path = os.path.join(self.pth, 'static', 'poll', 'csv',
                                     'results.csv')
        json_file_path = os.path.join(self.pth, 'static', 'poll', 'json',
                                      'results.json')        
        with open(csv_file_path, 'w') as csvfile:
            r_writer = csv.writer(csvfile)
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
        participant_preferences = UserProfile.list_participant_preferences()
        csv_file_path = os.path.join(self.pth, 'static', 'poll', 'csv',
                                     'participants.csv')
        json_file_path = os.path.join(self.pth, 'static', 'poll', 'json',
                                      'participants.json')                
        results = UserProfile.list_participant_detailed_preferences()
        participant_details = results['participant_details']
        subject_areas = results['subject_areas']
        with open(csv_file_path, 'w') as csvfile:
            r_writer = csv.writer(csvfile)
            header = [
                'acronym',
                'project_name',
                'institute',
                'email',
                'subject_area',
                'num_preferences',
            ]
            for subject_area in subject_areas:
                header.append(subject_area.name.encode('utf-8'))
            r_writer.writerow(header)
            for participant in participant_preferences:
                per_participant = participant_details[participant]
                row = [
                    participant.project.acronym,
                    participant.project.name,
                    participant.project.institute.name,
                    participant.user.email,
                    participant.subject_area.name,
                    str(participant.num_preferences),
                ]
                for subject_area in subject_areas:
                    row.append(str(per_participant[subject_area]))
                r_writer.writerow([ s.encode("utf-8") for s in row])
                     
    def handle(self, *args, **options):
        if options['count']:
            self.count_results()
        elif options['participants']:
            self.list_participants()

        
        
