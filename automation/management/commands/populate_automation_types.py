from django.core.management.base import BaseCommand
from automation.models import TriggerType, ActionType

class Command(BaseCommand):
    help = 'Populates default automation triggers and actions'

    def handle(self, *args, **options):
        # Triggers
        TriggerType.objects.get_or_create(
            code='status_change',
            defaults={
                'name': 'Status Changed',
                'description': 'When a status column changes to a specific value',
                'icon': 'lightning',
                'color': 'blue',
                'requires_value': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Ensured Trigger: Status Changed'))

        # Actions
        ActionType.objects.get_or_create(
            code='send_email',
            defaults={
                'name': 'Send Email',
                'description': 'Send an email to the board owner',
                'icon': 'mail',
                'color': 'orange',
                'requires_value': False
            }
        )
        self.stdout.write(self.style.SUCCESS('Ensured Action: Send Email'))
        
        ActionType.objects.get_or_create(
            code='change_status',
            defaults={
                'name': 'Change Status',
                'description': 'Change another status column',
                'icon': 'refresh',
                'color': 'purple',
                'requires_value': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Ensured Action: Change Status'))
