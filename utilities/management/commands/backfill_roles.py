from django.core.management.base import BaseCommand
from home.models import Hive, UserRole
class Command(BaseCommand):
    help = 'Assign Queen roles to the creators of all existing hives'
    def handle(self, *args, **kwargs):
        hives = Hive.objects.all()
        for hive in hives:
            user_role, created = UserRole.objects.get_or_create(
                user=hive.creator,
                hive=hive,
                defaults={'role': 'queen'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Assigned Queen role to {hive.creator.username} for {hive.buzz}."))
            else:
                self.stdout.write(self.style.WARNING(f"{hive.creator.username} is already assigned a role in {hive.buzz}."))
                