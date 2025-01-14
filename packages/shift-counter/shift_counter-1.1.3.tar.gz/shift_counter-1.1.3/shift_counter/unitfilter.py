from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Constraint:
    """Single filter constraint"""
    name: str
    keep: bool
    value: Optional[List[Any]] = None

class UnitFilter:
    """Builder for creating chains of unit filtering constraints"""
    def __init__(self):
        self.constraints: List[Constraint] = []

    def constraint(self, name: str, keep: bool, value: Optional[List[Any]] = None) -> 'UnitFilter':
        """
        Add a constraint to the filter chain.

        Args:
            name: Type of constraint ('stores', 'departments', 'id', 'parent_unit_id', 'deactivated')
            keep: Whether to keep (True) or remove (False) matching units
            value: List of values to match against (required for id, parent_unit_id, and deactivated constraints)

        Returns:
            self for method chaining
        """
        if name not in ['stores', 'departments', 'id', 'parent_unit_id', 'deactivated']:
            raise ValueError(f"Invalid constraint name: {name}")

        if name in ['id', 'parent_unit_id', 'deactivated'] and not value:
            raise ValueError(f"Value list is required for constraint: {name}")

        self.constraints.append(Constraint(name=name, keep=keep, value=value))
        return self

    def apply(self, unit: Dict[str, Any]) -> bool:
        """
        Apply all constraints to a single unit.

        Returns:
            bool: True if unit should be kept, False if it should be filtered out
        """
        for constraint in self.constraints:
            if constraint.name in ['stores', 'departments']:
                # Skip if this type of constraint doesn't apply to this unit
                parent_id = unit.get('parent_unit_id')
                is_store = parent_id is None or parent_id == 0

                if (constraint.name == 'stores' and not is_store) or \
                        (constraint.name == 'departments' and is_store):
                    continue

                if not constraint.keep:
                    return False
            else:
                matches = False
                if constraint.name == 'id':
                    matches = unit.get('id') in constraint.value
                elif constraint.name == 'parent_unit_id':
                    parent_id = unit.get('parent_unit_id')
                    matches = parent_id in constraint.value
                elif constraint.name == 'deactivated':
                    matches = unit.get('deactivated', False) in constraint.value

                if matches != constraint.keep:
                    return False

        return True