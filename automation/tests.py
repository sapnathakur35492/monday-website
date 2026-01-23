from django.test import TestCase
from webapp.models import Board, Group, Item, Workspace, Column
from core.models import Organization, User
from automation.models import AutomationRule, AutomationLog
from automation.service import AutomationEngine

class AutomationLogicTest(TestCase):
    def setUp(self):
        # Setup basic data
        self.user = User.objects.create(username='testuser', email='test@example.com')
        self.org = Organization.objects.create(name='Test Org', owner=self.user)
        self.workspace = Workspace.objects.create(name='Test WS', organization=self.org)
        self.board = Board.objects.create(name='Test Board', workspace=self.workspace, created_by=self.user)
        self.group = Group.objects.create(board=self.board, title='Test Group')
        self.item = Item.objects.create(group=self.group, name='Test Item', created_by=self.user)
        
        # Create columns
        self.status_col = Column.objects.create(
            board=self.board, 
            title='Status', 
            type='status', 
            settings={'choices': ['Not Started', 'Done']}
        )

    def test_status_change_trigger(self):
        # 1. Create Rule: When Status changes to "Done", Create Update
        rule = AutomationRule.objects.create(
            board=self.board,
            name='Test Rule',
            is_active=True,
            trigger_type='status_change',
            trigger_config={'column_id': self.status_col.id, 'value_id': 'Done'},
            action_type='create_update',
            action_config={'message': 'Task completed!'}
        )
        
        # 2. Simulate Event
        context = {
            'item': self.item,
            'column_id': self.status_col.id,
            'new_value': 'Done'
        }
        
        # 3. Run Engine
        AutomationEngine.run_automations(self.board, 'status_change', context)
        
        # 4. Verify Action (Update created)
        self.assertTrue(self.item.updates.exists())
        self.assertIn('Task completed!', self.item.updates.first().body)
        
        # 5. Verify Log
        self.assertTrue(AutomationLog.objects.filter(rule=rule, status='success').exists())

    def test_condition_mismatch_ignored(self):
        # Rule expects "Done"
        rule = AutomationRule.objects.create(
            board=self.board,
            name='Test Rule Mismatch',
            trigger_type='status_change',
            trigger_config={'column_id': self.status_col.id, 'value_id': 'Done'},
            action_type='create_update',
            action_config={'message': 'Should not happen'}
        )
        
        # Context has "In Progress"
        context = {
            'item': self.item,
            'column_id': self.status_col.id,
            'new_value': 'In Progress'
        }
        
        AutomationEngine.run_automations(self.board, 'status_change', context)
        
        # Verify NO Update created
        self.assertFalse(self.item.updates.exists())
