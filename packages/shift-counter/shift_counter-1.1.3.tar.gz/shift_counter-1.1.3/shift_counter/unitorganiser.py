from typing import Optional, Dict, Any
import pandas as pd
from .unitfilter import UnitFilter


class UnitOrganiser:
    """
    Class for organizing and filtering Tria HR organizational units.
    Manages relationships between stores and departments.
    """

    def __init__(self, stores_list: Optional[pd.DataFrame] = None):
        """
        Initialize UnitOrganiser with optional stores DataFrame.

        Args:
            stores_list: DataFrame containing store information with columns:
                        'tria_id' and 'but_num_business_unit'
        """
        self.stores_list = stores_list
        self.extraction_date = pd.Timestamp.now(tz='UTC').tz_localize(None).floor('s')
        self.df = pd.DataFrame(columns=[
            'department_id',
            'department_name',
            'extraction_date',
            'store_department_id',
            'store_id',
            'deactivated'
        ])

        # Set proper types for columns
        self.df['department_id'] = self.df['department_id'].astype(int)
        self.df['department_name'] = self.df['department_name'].astype(str)
        self.df['extraction_date'] = pd.to_datetime(self.df['extraction_date'])
        self.df['store_department_id'] = self.df['store_department_id'].astype('Int64')  # nullable integer
        self.df['store_id'] = self.df['store_id'].astype('Int64')  # nullable integer
        self.df['deactivated'] = self.df['deactivated'].astype(bool)

    @staticmethod
    def filter_organization_units(organization_units: Dict[str, Any], unit_filter: UnitFilter) -> Dict[str, Any]:
        """
        Filter organization units based on provided filter chain.

        Args:
            organization_units: Dictionary containing organization units data
            unit_filter: Chain of filtering constraints

        Returns:
            Dictionary with filtered organization units
        """
        if not organization_units.get('data'):
            return organization_units

        filtered_data = [
            unit for unit in organization_units['data']
            if unit_filter.apply(unit)
        ]

        return {
            'data': filtered_data,
            'status': organization_units.get('status', 'ok')
        }

    def add_department(self, organization_units: Dict[str, Any]):
        if not self.stores_list is not None:
            raise ValueError("stores_list DataFrame is required for add_department")

        for unit in organization_units.get('data', []):
            unit_id = int(unit['id'])
            parent_id = unit.get('parent_unit_id')
            is_store = parent_id is None or parent_id == 0

            if is_store:
                matching_store = self.stores_list[
                    self.stores_list['tria_id'] == unit_id
                    ]

                if not matching_store.empty:
                    new_row = {
                        'department_id': unit_id,
                        'department_name': unit['full_name'],
                        'extraction_date': self.extraction_date,
                        'store_department_id': unit_id,
                        'store_id': matching_store.iloc[0]['but_num_business_unit'],
                        'deactivated': unit.get('deactivated', False)  # default to False if not present
                    }
                    self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
            else:
                parent_id = int(parent_id)
                matching_store = self.stores_list[
                    self.stores_list['tria_id'] == parent_id
                    ]

                if not matching_store.empty:
                    new_row = {
                        'department_id': unit_id,
                        'department_name': unit['full_name'],
                        'extraction_date': self.extraction_date,
                        'store_department_id': parent_id,
                        'store_id': matching_store.iloc[0]['but_num_business_unit'],
                        'deactivated': unit.get('deactivated', False)  # default to False if not present
                    }
                    self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)

    def get_dataframe(self) -> pd.DataFrame:
        """
        Return the current state of the departments DataFrame.

        Returns:
            pd.DataFrame: Copy of the internal DataFrame with all departments
        """
        return self.df.copy()