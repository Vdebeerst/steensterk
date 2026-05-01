# -*- coding: utf-8 -*-

import json
from os import name

from odoo import api, models, _
from odoo.tools import float_round
import logging
_logger = logging.getLogger(__name__)

class attentia_import_wizard(models.AbstractModel):
    _name = 'attentia.import.wizard'
    _description = 'Attentia Import'

    def employee_import_attentia(self, employee):
        employee.attentia_import()

    def employee_import_attentia_new(self, employee):
        employee.attentia_import_new()

    def run_attentia_import(self):
        
        employees = self.env['hr.employee'].search(
            ['|',
             ('attentia_leave_import', '=', True),
             ('attentia_data_import', '=', True)]
        )
        for employee in employees:
            employee.attentia_import()

    def run_attentia_import_new(self):
        """ New method to import attentia data using the new import method in hr.employee. Executed from cron job. """

        employees = self.env['hr.employee'].search(
            ['|',
             ('attentia_leave_import', '=', True),
             ('attentia_data_import', '=', True)]
        )

        for employee in employees:

            # no need to create quejob... 
            # ...is done in the employee.attentia_import_new method
            
            employee.attentia_import_new('Job')
