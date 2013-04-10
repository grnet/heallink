from django.core.management.base import BaseCommand, CommandError
import poll
from poll.models import Journal, SubjectArea, Publisher

from optparse import make_option

import os
import csv

class Command(BaseCommand):
    args = '[-sjd]'
    help = 'Imports journal data to the database'
    pth = os.path.abspath(poll.__path__[0])
    
    option_list = BaseCommand.option_list + (
        make_option('-s',
                    '--subjectareas',
                    action='store_true',
                    dest='subject_areas',
                    default=False,
                    help='Import  subject areas in the database'),
        make_option('-j',
                    '--journals',
                    action='store_true',
                    dest='journals',
                    default=False,
                    help='Import journal data in the database'),
        make_option('-d',
                    '--downloads',
                    action='store_true',
                    dest='downloads',
                    default=False,
                    help='Update the journal download field'),
        )

    def import_subject_areas(self):
        subject_areas_file_path = os.path.join(Command.pth,
                                               'fixtures',
                                               'journal_subject_areas.csv')
        with open(subject_areas_file_path, 'rb') as subject_areas_file:
            sa_reader = csv.reader(subject_areas_file)
            for row in sa_reader:
                sa = SubjectArea(name=row[0], ordering=row[1])
                sa.save()

    def import_journals(self):
        journal_file_path = os.path.join(Command.pth,
                                         'fixtures',
                                         'journal_titles.csv')
        with open(journal_file_path, 'rb') as journal_titles_file:
            jt_reader = csv.reader(journal_titles_file)
            next(jt_reader)
            for row in jt_reader:
                title = row[6].strip()
                if title == "":
                    continue
                sa_name = row[-2].strip()
                p_name = row[8].strip()
                if Publisher.objects.filter(name=p_name).count() == 0:
                    publisher = Publisher(name=p_name)
                    publisher.save()
                else:
                    publisher = Publisher.objects.filter(name=p_name)[0]
                if SubjectArea.objects.filter(name=sa_name).count() == 0:
                    subject_area = SubjectArea(name=sa_name)
                    subject_area.save()
                else:
                    subject_area = SubjectArea.objects.filter(name=sa_name)[0]
                journal = Journal(issn=row[4].strip(),
                                  title=title,
                                  url=row[7].strip(),
                                  publisher=publisher,
                                  subject_area=subject_area)
                journal.save()
            

    def import_downloads(self):
        journal_downloads_file_path = os.path.join(Command.pth,
                                                   'fixtures',
                                                   'journal_downloads.csv')
        with open(journal_downloads_file_path, 'rb') as journal_downloads_file:
            jd_reader = csv.reader(journal_downloads_file)
            next(jd_reader)
            for row in jd_reader:
                downloads = row[0].strip()
                if downloads == "":
                    continue
                issn = row[1].strip()
                title = row[3].strip()
                journal = None
                if (issn != ""
                    and Journal.objects.filter(issn=issn).count() != 0):
                    journal = Journal.objects.filter(issn=issn)[0]
                elif (title != "" and
                      Journal.objects.filter(title=title).count() != 0):
                    journal = Journal.objects.filter(title=title)[0]
                if journal is not None:
                    journal.downloads = downloads
                    journal.save()
                
            
            
    def handle(self, *args, **options):
        if options['subject_areas']:
            self.import_subject_areas()
        if options['journals']:
            self.import_journals()
        if options['downloads']:
            self.import_downloads()

        
        
