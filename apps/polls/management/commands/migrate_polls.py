import csv
from bulk_update.helper import bulk_update

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from apps.polls.models import Poll, Choice
from apps.utils.converters import perl_to_python_dict
from apps.votes.models import Vote

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Migrate polls from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        choice_ct = ContentType.objects.get_for_model(Choice)

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        self.stdout.write('Parse file...')
        csv.field_size_limit(500 * 1024 * 1024)
        with open(path, 'r', encoding=settings.MIGRATE_FILE_ENCODING) as csvfile:
            reader = csv.reader(csvfile)

            poll_sum_votes = {}
            votes = []

            for row in reader:

                try:
                    data = perl_to_python_dict(row[9])
                except Exception as e:
                    self.stderr.write(e)
                    continue

                try:
                    results = perl_to_python_dict(data['results'], second=True)['1']
                except Exception as e:
                    self.stderr.write(e)
                    continue

                answers = data['votes']
                try:
                    answers = answers[answers.find("{") + 1: answers.rfind("}")]
                    answers = answers[answers.find("[") + 2: answers.rfind("]") - 1]
                    answers = answers.split('","')
                except Exception as e:
                    self.stderr.write(e)
                    continue

                poll = Poll.objects.create(question=row[7], is_active=bool(int(row[5])))
                poll_sum_votes[poll.id] = 0

                for i, answer in enumerate(answers, start=1):
                    vote_count = results[str(i)]
                    poll_sum_votes[poll.id] += vote_count

                    choice = Choice.objects.create(poll=poll, answer=answer, vote_count=vote_count)
                    votes.extend(
                        [Vote(object_id=choice.id, content_type_id=choice_ct.id, score=1)
                         for i in range(vote_count)]
                    )

            if votes:
                self.stdout.write('Bulk create choices votes...')
                Vote.objects.bulk_create(votes, batch_size=BATCH_SIZE)

            polls = Poll.objects.all()
            for poll in polls:
                poll.sum_votes = poll_sum_votes[poll.id]
            bulk_update(polls, update_fields=['sum_votes'])

        self.stdout.write('End...')
