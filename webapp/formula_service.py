import re
from decimal import Decimal

class FormulaEngine:
    """
    A simple, safe formula engine for the Monday.com clone.
    Supports basic arithmetic (+, -, *, /) and column references via {Column Name}.
    """
    
    @staticmethod
    def evaluate(expression, item):
        """
        Evaluates a formula expression string in the context of an Item.
        Replaces {Column Name} with actual values.
        """
        if not expression or not isinstance(expression, str):
            return ""

        # 1. Identify Column References: {Column Name}
        # Regex to find text inside curly braces
        refs = re.findall(r'\{([^}]+)\}', expression)
        
        # 2. Resolve Column Values
        # We need to look up columns by Title on the board
        board_columns = {c.title: c for c in item.group.board.columns.all()}
        
        processed_expr = expression
        
        for ref_name in refs:
            col = board_columns.get(ref_name)
            val = 0 # Default to 0 if not found or empty
            
            if col:
                # Retrieve value from item.values JSON
                # col.id is the key in item.values dictionary
                raw_val = item.values.get(str(col.id), 0)
                
                # Try to convert to float/number
                try:
                    val = float(raw_val)
                except (ValueError, TypeError):
                    val = 0
            
            # Replace {Column Name} with the actual numeric value
            # We use distinct placeholder repalcement to avoid partial matches
            processed_expr = processed_expr.replace(f"{{{ref_name}}}", str(val))
            
        # 3. Safe Evaluation
        # ALLOWED_CHARS: digits, ., +, -, *, /, (, ), space
        if not re.match(r'^[\d\.\+\-\*\/\(\)\s]+$', processed_expr):
            return "Error: Invalid Characters"
            
        try:
            # simple eval - in production, use a parser like 'asteval' or 'pyparsing' for full safety
            # But with our regex check above, we strictly limit to math chars.
            result = eval(processed_expr)
            
            # Formatting: Round to 2 decimals if float
            if isinstance(result, float):
                return round(result, 2)
            return result
        except ZeroDivisionError:
            return "Error: Div by 0"
        except Exception as e:
            return f"Error: {str(e)}"
