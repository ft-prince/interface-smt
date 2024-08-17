from django.core.management.base import BaseCommand
from django.utils import timezone
from screen_app.models import ControlChartReading

class Command(BaseCommand):
    help = 'Adds test data for the control chart'

    def handle(self, *args, **options):
        test_data = [
            [360, 360, 360, 355, 360],
            [360, 365, 365, 365, 365],
            [360, 364, 364, 366, 364],
            [360, 367, 367, 362, 367],
            [360, 370, 370, 364, 370]
        ]

        for i, readings in enumerate(test_data):
            date = timezone.now().date() - timezone.timedelta(days=i)
            ControlChartReading.objects.create(
                date=date,
                reading1=readings[0],
                reading2=readings[1],
                reading3=readings[2],
                reading4=readings[3],
                reading5=readings[4]
            )

        self.stdout.write(self.style.SUCCESS('Successfully added test data'))