from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.tests import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, test_reports

@tagged('post_install', '-at_install')
class TestAttentiaInterface(TransactionCase):

    def setUp(self):
        print('test attentia setup')
        super().setUp()
        self.employee_ids = [29,94,31,47]
        self.employees = self.env['hr.employee'].browse(self.employee_ids)

        self.attentia_time_off_types = self.env['hr.leave.type'].search([('name', 'ilike', 'Attentia%')])

        self.attentia_holiday_pv_name = f'Attentia Holiday {fields.Date.today().year - 1}'

        self.balance_py = {
            29: {
                self._get_attentia_time_off_type(self.attentia_holiday_pv_name): 88, 
            },
            94: {
                self._get_attentia_time_off_type(self.attentia_holiday_pv_name): 40.4,
                
            },
            31: {
                # self._get_attentia_time_off_type(self.attentia_holiday_pv_name): 72.7,
                
            },
            47: {
                
            },
        }

    def _load_balance_py(self):
        
        for employee_id, balance in self.balance_py.items():
            for time_off_type, days in balance.items():
                self.env['hr.leave.allocation'].create({
                    'employee_id': employee_id,
                    'holiday_status_id': time_off_type.id,
                    'number_of_days': days,
                })

    def test_load_initial_balance(self):
        
        self._load_balance_py()

        allocations = self.env['hr.leave.allocation'].search([('employee_id', 'in', self.employee_ids),('holiday_status_id','=',self._get_attentia_time_off_type(self.attentia_holiday_pv_name).id)])

        allocations_by_employee_id = {allocation.employee_id.id: allocation.number_of_days for allocation in allocations}

        for employee_id in self.employee_ids:
            if employee_id not in allocations_by_employee_id:
                self.fail(f'Employee {employee_id} not found in allocations')
            print('******', allocations_by_employee_id[employee_id], self.balance_py[employee_id][self._get_attentia_time_off_type(self.attentia_holiday_pv_name)])
            if allocations_by_employee_id[employee_id] != self.balance_py[employee_id][self._get_attentia_time_off_type(self.attentia_holiday_pv_name)]:
                
                self.fail(f'Employee {employee_id} has wrong balance: {allocations_by_employee_id[employee_id]}')

    def test_attentia_time_off_types(self):
        current_year = fields.Date.today().year
        
        time_off_types_to_check = [
            f'Attentia Holiday {current_year}',
            f'Attentia ADV {current_year}',
            f'Attentia Career Leave {current_year}',
            'Attentia Home Work',
            'Attentia Illness',
            f'Attentia Seniority {current_year}',
            self.attentia_holiday_pv_name,
        ]

        for time_off_type_name in time_off_types_to_check:
            if not self.attentia_time_off_types.filtered(lambda time_off_type: time_off_type.name == time_off_type_name):
                self.fail(f'Time Off Type "{time_off_type_name}" not found')

    

    def _get_attentia_time_off_type(self, time_off_type_name):
        time_off_type = self.attentia_time_off_types.filtered(lambda time_off_type: time_off_type.name == time_off_type_name)
        if not time_off_type:
            raise UserError(f'Time Off Type "{time_off_type_name}" not found')
        return time_off_type
    
    





