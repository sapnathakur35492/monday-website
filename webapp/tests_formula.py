from django.test import TestCase
from .formula_service import FormulaEngine
from .models import Item, Group, Board, Workspace, Column
from core.models import Organization, User

class MockItem:
    def __init__(self, values, board_columns):
        self.values = values
        self.group = type('obj', (object,), {'board': type('obj', (object,), {'columns': type('obj', (object,), {'all': lambda: board_columns})})})

class MockColumn:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class FormulaEngineTest(TestCase):
    def test_basic_math(self):
        item = MockItem({}, [])
        self.assertEqual(FormulaEngine.evaluate("2 + 2", item), 4)
        self.assertEqual(FormulaEngine.evaluate("10 / 2", item), 5.0)
        
    def test_column_reference(self):
        col1 = MockColumn(1, "Numbers")
        col2 = MockColumn(2, "Price")
        
        # Format item values as they are in DB (strings in JSON)
        values = {"1": "10", "2": "5.5"}
        item = MockItem(values, [col1, col2])
        
        # Test referencing columns
        self.assertEqual(FormulaEngine.evaluate("{Numbers} * 2", item), 20.0)
        self.assertEqual(FormulaEngine.evaluate("{Numbers} + {Price}", item), 15.5)
        
    def test_error_handling(self):
        item = MockItem({}, [])
        self.assertEqual(FormulaEngine.evaluate("10 / 0", item), "Error: Div by 0")
        self.assertEqual(FormulaEngine.evaluate("INVALID", item), "Error: Invalid Characters")
