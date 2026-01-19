from django.core.management.base import BaseCommand
from automation.models import TriggerType, ActionType
from marketing.models import Feature
from webapp.models import Board, Workspace
from core.models import User

class Command(BaseCommand):
    help = 'Populates the database with essential initial data for Automation and Marketing'

    def handle(self, *args, **kwargs):
        self.stdout.write("Checking triggers...")
        if not TriggerType.objects.exists():
            TriggerType.objects.create(
                name="Status Changes",
                code="status_change",
                description="When an item moves stage",
                icon="check-circle",
                color="green",
                requires_value=True,
                order=1
            )
            TriggerType.objects.create(
                name="Item Created",
                code="item_created",
                description="When a new task is added",
                icon="plus",
                color="blue",
                requires_value=False,
                order=2
            )
            self.stdout.write(self.style.SUCCESS("Created default triggers."))
        
        self.stdout.write("Checking actions...")
        if not ActionType.objects.exists():
            ActionType.objects.create(
                name="Send Email",
                code="send_email",
                description="Notify the board owner",
                icon="mail",
                color="orange",
                requires_value=False, # For now hardcoded to owner
                order=1
            )
            ActionType.objects.create(
                name="Change Status",
                code="change_status",
                description="Update item status",
                icon="refresh",
                color="purple",
                requires_value=True,
                order=2
            )
            ActionType.objects.create(
                name="Archive Item",
                code="archive_item",
                description="Remove from board",
                icon="archive",
                color="gray",
                requires_value=False,
                order=3
            )
            self.stdout.write(self.style.SUCCESS("Created default actions."))

        self.stdout.write("Checking Features...")
        if not Feature.objects.exists():
            Feature.objects.create(title="Dynamic Boards", description="Create boards with any columns you need.", icon_name="boards", order=1)
            Feature.objects.create(title="Powerful Automation", description="Set up 'If this, then that' rules.", icon_name="automation", order=2)
            Feature.objects.create(title="Team Management", description="Divide work among the team.", icon_name="team", order=3)
            self.stdout.write(self.style.SUCCESS("Created default features."))
