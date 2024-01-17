from django.core.management.base import BaseCommand

from funds.models import Fund


class Command(BaseCommand):
    help = 'Usage: createfund --name=Name'

    def add_arguments(self, parser):
        parser.add_argument(
            "--name",
            action='store',
            dest='name',
            required=True
        )

        parser.add_argument(
            "--notes",
            action='store', 
            dest='notes',
            required=False
        )

    def handle(self, **options):
        notes = options.get('notes')
        name = options.get('name')

        if name:
            if not Fund.objects.filter(name=name).exists():
                Fund.objects.create(name=name, notes=notes)
            self.stdout.write("Fund created")
        else:
            self.stdout.write("Fund name is required")
