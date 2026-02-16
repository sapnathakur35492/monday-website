from django.test import TestCase
from webapp.models import Board, Group, Item, Workspace, Column
from core.models import Organization, User
from automation.models import AutomationRule, AutomationLog
from automation.service import AutomationEngine

class ComprehensiveAutomationTest(TestCase):
    def setUp(self):
        # Setup basic data
        self.user = User.objects.create(username='auto_tester', email='auto@test.com')
        self.org = Organization.objects.create(name='Auto Org', owner=self.user)
        self.workspace = Workspace.objects.create(name='Auto WS', organization=self.org)
        self.board = Board.objects.create(name='Auto Board', workspace=self.workspace, created_by=self.user)
        self.group1 = Group.objects.create(board=self.board, title='Group 1')
        self.group2 = Group.objects.create(board=self.board, title='Group 2')
        self.item = Item.objects.create(group=self.group1, name='Test Item', created_by=self.user)
        
        # Columns
        self.status_col = Column.objects.create(board=self.board, title='Status', type='status', settings={'choices': ['ToDo', 'Done']})
        self.person_col = Column.objects.create(board=self.board, title='Assignee', type='person')

    def test_item_created_trigger(self):
        """Test 'item_created' trigger -> 'create_update' action"""
        # 1. Create Rule
        rule = AutomationRule.objects.create(
            board=self.board,
            name='Welcome New Item',
            trigger_type='item_created',
            action_type='create_update',
            action_config={'message': 'Welcome {item.name}!'}
        )
        
        # 2. Simulate Creation
        new_item = Item.objects.create(group=self.group1, name='New Baby Item', created_by=self.user)
        context = {'item': new_item}
        
        # 3. Run Engine
        AutomationEngine.run_automations(self.board, 'item_created', context)
        
        # 4. Verify
        self.assertTrue(new_item.updates.filter(body__contains='Welcome New Baby Item').exists())

    def test_status_change_moves_item(self):
        """Test 'status_change' (Done) -> 'move_item' (Group 2)"""
        rule = AutomationRule.objects.create(
            board=self.board,
            name='Move Done Items',
            trigger_type='status_change',
            trigger_config={'column_id': self.status_col.id, 'value': 'Done'},
            action_type='move_item',
            action_config={'group_id': self.group2.id}
        )
        
        context = {
            'item': self.item,
            'column_id': self.status_col.id,
            'new_value': 'Done'
        }
        
        AutomationEngine.run_automations(self.board, 'status_change', context)
        
        self.item.refresh_from_db()
        self.assertEqual(self.item.group.id, self.group2.id)

    def test_assign_person_action(self):
        """Test 'status_change' -> 'assign_person'"""
        rule = AutomationRule.objects.create(
            board=self.board,
            name='Assign Me',
            trigger_type='status_change',
            trigger_config={'column_id': self.status_col.id, 'value': 'ToDo'},
            action_type='assign_person',
            action_config={'user_id': self.user.id}
        )
        
        context = {
            'item': self.item,
            'column_id': self.status_col.id,
            'new_value': 'ToDo'
        }
        
        AutomationEngine.run_automations(self.board, 'status_change', context)
        
        self.item.refresh_from_db()
        # Check if person column value updated (JSON field)
        col_val = self.item.values.get(str(self.person_col.id))
        self.assertEqual(col_val, self.user.username)

    def test_chained_automations_logic(self):
        """
        Verify that we can essentially chain logic by having multiple rules on same trigger.
        1. Status -> Done => Update 'Good job'
        2. Status -> Done => Move to Group 2
        """
        rule1 = AutomationRule.objects.create(
            board=self.board, 
            name='Rule 1', 
            trigger_type='status_change', trigger_config={'column_id': self.status_col.id, 'value': 'Done'},
            action_type='create_update', action_config={'message': 'Good job'}
        )
        rule2 = AutomationRule.objects.create(
            board=self.board, 
            name='Rule 2', 
            trigger_type='status_change', trigger_config={'column_id': self.status_col.id, 'value': 'Done'},
            action_type='move_item', action_config={'group_id': self.group2.id}
        )
        
        context = {'item': self.item, 'column_id': self.status_col.id, 'new_value': 'Done'}
        AutomationEngine.run_automations(self.board, 'status_change', context)
        
        self.item.refresh_from_db()
        self.assertEqual(self.item.group.id, self.group2.id)
        self.assertTrue(self.item.updates.filter(body__contains='Good job').exists())

    def test_column_change_trigger(self):
        """Test 'column_changed' (generic) trigger"""
        # Create rule: When Any Column Changes -> Create Update
        rule = AutomationRule.objects.create(
            board=self.board,
            name='Track Changes',
            trigger_type='column_changed',
            action_type='create_update',
            action_config={'message': 'Column changed!'}
        )
        
        context = {
            'item': self.item,
            'column_id': self.status_col.id,
            'new_value': 'Done'
        }
        
        AutomationEngine.run_automations(self.board, 'column_changed', context)
        
        self.assertTrue(self.item.updates.filter(body__contains='Column changed!').exists())

    def test_change_status_action(self):
        """Test 'change_status' action"""
        # Create rule: When Item Created -> Change Status to 'Done'
        rule = AutomationRule.objects.create(
            board=self.board,
            name='Auto Done',
            trigger_type='item_created',
            action_type='change_status',
            action_config={'column_id': self.status_col.id, 'new_value': 'Done'}
        )
        
        new_item = Item.objects.create(group=self.group1, name='Auto Done Item', created_by=self.user)
        context = {'item': new_item}
        
        AutomationEngine.run_automations(self.board, 'item_created', context)
        
        new_item.refresh_from_db()
        val = new_item.values.get(str(self.status_col.id))
        self.assertEqual(val, 'Done')

    def test_e2e_status_change_via_signal(self):
        """
        End-to-end: Update item status via .save() (signal fires) -> automation runs -> update created.
        No manual run_automations; pure signal flow.
        """
        rule = AutomationRule.objects.create(
            board=self.board,
            name='Done creates update',
            is_active=True,
            trigger_type='status_change',
            trigger_config={'column_id': self.status_col.id, 'value': 'Done'},
            action_type='create_update',
            action_config={'message': 'Task marked done!'}
        )
        self.assertFalse(self.item.updates.exists())
        # Change status via model save (as the UI would)
        self.item.values[str(self.status_col.id)] = 'Done'
        self.item.save()
        self.item.refresh_from_db()
        self.assertTrue(
            self.item.updates.filter(body__icontains='Task marked done').exists(),
            'Update should be created by automation when status changed to Done'
        )
        self.assertTrue(
            AutomationLog.objects.filter(rule=rule, status='success').exists(),
            'AutomationLog success should be created'
        )
