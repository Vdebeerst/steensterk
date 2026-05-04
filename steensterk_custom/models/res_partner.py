# -*- coding: utf-8 -*-
"""
Short description if needed.

Changes:

"""

from typing import Optional
from dataclasses import dataclass
from odoo import fields, models, _
from odoo.exceptions import  UserError, ValidationError, AccessError
# from odoo.addons.ucamco_base.utils.constants import Constants as UcamcoConstants
import time
import requests
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption
import os
import json
import logging
from datetime import date, datetime, timedelta

# from odoo.addons.ucamco_base.utils.ucamco_utils import UcamcoUtils

# _logger = logging.getLogger(__name__)
# class PKCS12Manager():
#     """ Manages the conversion of a PKCS#12 file to PEM formatted key and certificate files. """

#     def __init__(self, p12file):
#         self.p12file = p12file
#         self.webservices_dir = ''
#         self.keyfile = ''
#         self.certfile = ''

#         # Get filename without extension
#         ext = os.path.splitext(p12file)
#         self.filebasename = os.path.basename(ext[0])

#         self.createPrivateCertStore()
#         self.p12topem()

#     def getKey(self):
#         return self.keyfile

#     def getCert(self):
#         return self.certfile

#     def createPrivateCertStore(self):
#         home = os.path.expanduser('~')
#         webservices_dir = os.path.join(home, '.webservices')
#         if not os.path.exists(webservices_dir):
#             os.mkdir(webservices_dir)
#         os.chmod(webservices_dir, 0o700)
#         self.webservices_dir = webservices_dir

#     # rewrote/replaced because of deprecation warning
#     # PKCS#12 support in pyOpenSSL is deprecated. You should use the APIs in cryptography
#     def p12topem(self):
#         with open(self.p12file, 'rb') as p12_file:
#             p12_data = p12_file.read()

#         # Load the PKCS#12 data
#         private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(p12_data, None)

#         if private_key is None or certificate is None:
#             raise AccessError("Failed to load private key or certificate from PKCS#12 file")

#         # PEM formatted private key
#         key = private_key.private_bytes(
#             encoding=Encoding.PEM,
#             format=PrivateFormat.TraditionalOpenSSL,
#             encryption_algorithm=NoEncryption()
#         )

#         self.keyfile = os.path.join(self.webservices_dir, self.filebasename + ".key.pem")
#         with open(self.keyfile, 'wb') as f:
#             f.write(key)
#         os.chmod(self.keyfile, 0o600)

#         # PEM formatted certificate
#         cert = certificate.public_bytes(Encoding.PEM)

#         self.certfile = os.path.join(self.webservices_dir, self.filebasename + ".crt.pem")
#         with open(self.certfile, 'wb') as f:
#             f.write(cert)
#         os.chmod(self.certfile, 0o644)

# @dataclass
# class AttentiaRecord:
#     """ Represents a single record from Attentia. """

#     _day: str
#     _code: int
#     _shift: int
#     _hours: float

#     _attentia_to_odoo_dict: Optional[dict] = None

#     def to_dict(self):
#         return {
#             'Day': self._day,
#             'Code': self._code,
#             'Shift': self._shift,
#             'Hours': self._hours
#         }

#     def code(self) -> int:
#         return int(self._code)

#     def hours(self) -> float:
#         return self._hours

#     def is_full_day(self) -> bool:
#         return self._hours == 0.0

#     def dayAsDate(self) -> date:
#         return datetime.strptime(self._day, "%Y%m%d").date()

#     def dayAsDateTime(self) -> datetime:
#         return datetime.strptime(self._day, "%Y%m%d")

#     @staticmethod
#     def _employee_resource_calendar(employee, target_date: Optional[date] = None):
#         """
#         Returns the correct resource calendar for the given employee based on the target date.
#         If no target date is provided, it uses the current date.

#         :param employee: The employee record (e.g., hr.employee)
#         :param target_date: The date for which to find the correct calendar (datetime.date or string in 'YYYY-MM-DD' format)
#         :return: The correct resource.calendar record or None if not found
#         """
#         if not target_date:
#             target_date = datetime.today().date()

#         # Filter the calendars that are active during the target date
#         for ucamco_resource_calendar in employee.ucamco_resource_calendar_ids:
#             date_start = ucamco_resource_calendar.date_start or datetime.min.date()
#             date_end = ucamco_resource_calendar.date_end or datetime.max.date()
#             if date_start <= target_date <= date_end:
#                 _logger.info(f"Using resource calendar {ucamco_resource_calendar.resource_calendar_id.name} for {employee.name} on {target_date}.")
#                 return ucamco_resource_calendar.resource_calendar_id
#         return employee.resource_calendar_id

#     def _employee_day_attendance(self, employee, day: date) -> list:
#         return AttentiaRecord._employee_resource_calendar(employee, day).attendance_ids.filtered(lambda x: int(x.dayofweek) == day.weekday())

#     def _employee_start_hour_on_day(self, employee, day: date) -> float:
#         work_hours_of_day = self._employee_day_attendance(employee, self.dayAsDate())
#         return sorted(work_hours_of_day, key=lambda x: x.hour_from)[0].hour_from

#     def _employee_end_hour_on_day(self, employee, day: date) -> float:
#         work_hours_of_day = self._employee_day_attendance(employee, self.dayAsDate())
#         return sorted(work_hours_of_day, key=lambda x: x.hour_to, reverse=True)[0].hour_to

#     def date_from(self, employee) -> datetime:
#         start_hour = self._employee_start_hour_on_day(employee, self.dayAsDate())
#         hours, minutes, seconds = UcamcoUtils.float_hours_to_hms(start_hour, True)
#         return UcamcoUtils.convert_to_gmt(datetime.combine(self.dayAsDate(), datetime.min.time()) + timedelta(hours=hours, minutes=minutes, seconds=seconds), 'Europe/Brussels')

#     def date_to(self, employee, date_from: datetime) -> datetime:
#         if not(self.is_full_day()):
#             hours, minutes, seconds = UcamcoUtils.float_hours_to_hms(self._hours, True)
#             end_date_time = date_from + timedelta(hours=hours, minutes=minutes, seconds=seconds)
#             return UcamcoUtils.convert_to_gmt(end_date_time, 'Europe/Brussels') 
#         end_hour = self._employee_end_hour_on_day(employee, self.dayAsDate())
#         hours, minutes, seconds = UcamcoUtils.float_hours_to_hms(end_hour, True)
#         return UcamcoUtils.convert_to_gmt(datetime.combine(self.dayAsDate(), datetime.min.time()) + timedelta(hours=hours, minutes=minutes, seconds=seconds), 'Europe/Brussels')

#     def _get_employee_work_hours_for_weekday(self, employee, resource_calendar = None) -> float:
#         """ Return the total number of work hours for the employee on the day of the week of the record. """
#         day_of_week = str(self.dayAsDate().weekday())
#         if not(resource_calendar):
#             attendances = self._employee_resource_calendar(employee, self.dayAsDate()).attendance_ids.filtered(lambda attendance: attendance.dayofweek == day_of_week) # self.resource_calendar_id.attendance_ids.filtered(lambda attendance: attendance.dayofweek == day_of_week)
#         else:
#             attendances = resource_calendar.attendance_ids.filtered(lambda attendance: attendance.dayofweek == day_of_week)
#         if not attendances:
#             # user doesn't work on that day?
#             # raise ValidationError(_(f'No working hours defined for this day of the week {day_of_week}.'))
#             # was raining an error here before, but apparently there is also data on days in the weekend?
#             # Dauw Giovanni - 2024-06-29 00:00:00 - 200 - Dauw Giovanni - Attentia Illness - 800
#             _logger.warning(f'No working hours defined for this day of the week {day_of_week}.')
#             return 0.0
#         total_hours = 0
#         for attendance in attendances:
#             total_hours += attendance.hour_to - attendance.hour_from
#         return total_hours

#     def _calculate_work_hours_in_days(self, employee) -> float:
#         """
#         Calculate the number of days from the hours.

#         Args:
#             day (date): The date.

#         Returns:
#             float: The total work hours between the specified dates.
#         """
        
#         work_hours_real = 0.0

#         day: date = self.dayAsDate()

#         resource_calendar = AttentiaRecord._employee_resource_calendar(employee, day) # employee.resource_calendar_id
#         if resource_calendar:
#             work_hours_real = self._get_employee_work_hours_for_weekday(employee)
#         else:
#             raise UserError(_(f'No working hours defined for this employee {employee.name} on {day}.'))

#         # potential working hours
#         work_hours_potential = self._get_employee_work_hours_for_weekday(employee, employee.resource_calendar_id)

#         if work_hours_potential == 0.0:
#             raise UserError(_(f'No working hours defined for this employee {employee.name} on {day}.'))

#         return work_hours_real / resource_calendar.hours_per_day if self._hours == 0.0 else self._hours / resource_calendar.hours_per_day

#     def dayAsString(self) -> str:
#         return self.dayAsDate().strftime("%Y-%m-%d")

#     def attentia_to_odoo_name(self) -> str:
#         if not self._attentia_to_odoo_dict.get(self._code):
#             return f"Unknown code {self._code}"
#         return self._attentia_to_odoo_dict[self._code]['odoo_name']

#     def attentia_to_odoo_id(self, env) -> int:
#         if not self._attentia_to_odoo_dict.get(self._code):
#             return -1
#         if self._code == 151:
#             return env['hr.leave.type'].search([('name', 'like', f'Attentia Holiday {self.dayAsDate().year - 1}')]).id
#         elif self._code == 204:
#             return env['hr.leave.type'].search([('name', 'like', f'Attentia Seniority {self.dayAsDate().year}')]).id
#         elif self._code == 200:
#             return env['hr.leave.type'].search([('name', 'like', f'Attentia Holiday {self.dayAsDate().year}')]).id
#         elif self._code == 120:
#             return env['hr.leave.type'].search([('name', 'like', f'Attentia ADV {self.dayAsDate().year}')]).id
#         elif self._code == 12:
#             return env['hr.leave.type'].search([('name', 'like', f'Attentia Career Leave {self.dayAsDate().year}')]).id
#         elif self._code == 8:
#             return env['hr.leave.type'].search([('name', 'like', f'Attentia Flex {self.dayAsDate().year}')]).id
#         return self._attentia_to_odoo_dict[self._code]['odoo_code']

#     def load_in_odoo(self) -> bool:
#         if not self._attentia_to_odoo_dict.get(self._code):
#             return False
#         return self._attentia_to_odoo_dict[self._code]['odoo_load']

#     def __repr__(self) -> str:
#         return f"AttentiaRecord({self.dayAsDate()}: {self.attentia_to_odoo_name()} [{self._hours} hours])"

#     @staticmethod
#     def from_json(json_str):
#         data = json.loads(json_str)
#         return AttentiaRecord(data['Day'], data['Code'], data['Shift'], data['Hours'])

class res_partner(models.Model):
    _inherit = "res.partner"

    ziggu_id = fields.Char('Ziggu Id')

    # def setup_attentia_to_odoo_dict(self, current_year: int, previous_year: int) -> dict:
    #     """ Maps attentia codes to Odoo leave types. 
    #     TODO: create the leave type? """
    #     attentia_types = self.env['hr.leave.type'].search([('name', 'like', 'Attentia%')])

    #     mapping = {
    #         200: {'odoo_code': 56, 'odoo_name': f'Attentia Holiday {current_year}', 'odoo_load': True, 'dynamic': True},
    #         204: {'odoo_code': 55, 'odoo_name': f'Attentia Seniority {current_year}', 'odoo_load': True, 'dynamic': True},
    #         151: {'odoo_code': 59, 'odoo_name': f'Attentia Holiday {previous_year}', 'odoo_load': True, 'dynamic': True},
    #         48: {'odoo_code': 61, 'odoo_name': 'Attentia Illness', 'odoo_load': True, 'dynamic': False},
    #         9: {'odoo_code': 60, 'odoo_name': 'Attentia Home Office', 'odoo_load': True, 'dynamic': False},
    #         800: {'odoo_code': 61, 'odoo_name': 'Attentia Illness', 'odoo_load': True, 'dynamic': False},
    #         339: {'odoo_code': 61, 'odoo_name': 'Attentia Illness', 'odoo_load': True, 'dynamic': False},
    #         120: {'odoo_code': 57, 'odoo_name': f'Attentia ADV {current_year}', 'odoo_load': True, 'dynamic': True},
    #         12: {'odoo_code': 58, 'odoo_name': f'Attentia Career Leave {current_year}', 'odoo_load': True, 'dynamic': True},
    #         4: {'odoo_code': -1, 'odoo_name': 'Attentia Zending', 'odoo_load': False, 'dynamic': False},
    #         100: {'odoo_code': -1, 'odoo_name': 'Attentia Public Holiday', 'odoo_load': False, 'dynamic': False}, # skip that one, is Public Holiday
    #         # vervanging feestdag, zoals public holiday maar dan voor vervanging, niet geladen in Odoo
    #         138: {'odoo_code': -1, 'odoo_name': 'Attentia Replacement Day Public Holiday', 'odoo_load': False, 'dynamic': False},
    #         111: {'odoo_code': 62, 'odoo_name': 'Attentia Paternity Leave 3', 'odoo_load': True, 'dynamic': False},
    #         356: {'odoo_code': 63, 'odoo_name': 'Attentia Paternity Leave', 'odoo_load': True, 'dynamic': False},
    #         8: {'odoo_code': 71, 'odoo_name': f'Attentia Flex {current_year}', 'odoo_load': True, 'dynamic': True},
    #     }

    #     """ Automatically remove the dynamic types so that they can be used in the mapping. """
    #     for key, value in mapping.items():
    #         if value['dynamic']:
    #             odoo_id = attentia_types.filtered(lambda type: type.name == value['odoo_name'])
    #             if not(odoo_id):
    #                 raise ValidationError(f"Time off type {value['odoo_name']} not found in Odoo.")
    #             mapping[key]['odoo_code'] = odoo_id.id

    #     return mapping

    # def attentia_import_new(self, how: str = 'Manual'):
    #     delayable = self.delayable(description=f"Attentia Import - {self.name} [{how}]")
    #     delayable.attentia_import_new_do()
    #     delayable.delay()

    # def import_attentia_employee_information(self, privatekey: tuple[str, str]):
    #     """ Imports the employee information from Attentia. """

    #     _logger.info(f'Loading attentia employee information for {self.name}...')

    #     api_url_worker = '%s/worker/%s' % (UcamcoConstants.ATTENTIA_API_BASE_URL, self.employee_nbr)
    #     r = requests.get(url=api_url_worker, cert=privatekey, headers=UcamcoConstants.ATTENTIA_API_UCAMCO_EMPLOYER_PARAMS)

    #     api_url_result = '%s/%s/%s' % (UcamcoConstants.ATTENTIA_API_BASE_URL, 'Result', r.json())
    #     statuscode = 0
    #     counter = 0
    #     while statuscode != '200' and counter < 50:
    #         time.sleep(0.5)
    #         r = requests.get(url=api_url_result, cert=privatekey)
    #         parsed_json = json.dumps(r.json(), indent=4)
    #         data_table = json.loads(parsed_json)
    #         statuscode = data_table['Statuscode']
    #         counter += 1

    #     if not(data_table['Response']):
    #         _logger.warning(f"Attentia import failed for {self.name} - no data received from api.")
    #         _logger.error(f"Attentia import failed received status code: {statuscode}")
    #         _logger.error(f"Attentia import failed received data: {data_table}")
    #         return

    #     response = json.loads(data_table['Response'])

    #     if response['Sex'] == 'M':
    #         gender = 'male'
    #     else:
    #         if response['Sex'] == 'F':
    #             gender = 'female'
    #         else:
    #             gender = 'other'
    #     if self.sex != gender or not(self.sex):
    #         self.sex = gender

    #     birthdate_s = response['Birthdate']
    #     birthday = datetime.strptime(birthdate_s, '%Y%m%d')
    #     if self.birthday != birthday or not(self.birthday):
    #         self.birthday = birthday

    #     place_of_birth = response['Birthplace']
    #     if self.place_of_birth != place_of_birth:
    #         self.place_of_birth = place_of_birth

    #     r.close()

    #     _logger.info(f'Loaded attentia employee information for {self.name}.')

    # def _load_private_key(self) -> tuple[str, str]:
    #     # Why? Not used?
    #     # import subprocess
    #     directory = os.path.abspath(__file__)
    #     pkcs12 = PKCS12Manager(directory.replace('models/hr_employee.py', 'static/description/Ucamco.pubpri.pfx'))
    #     return (pkcs12.getCert(), pkcs12.getKey())

    # def get_attentia_data(self, result_url: str, privatekey: tuple[str, str]) -> str | None:
    #     """ Retrieves leaves data from Attentia API given a result URL and private key. """

    #     statuscode = 0
    #     counter = 0
    #     while statuscode != '200' and counter < 50:
    #         time.sleep(0.5)
    #         request = requests.get(url=result_url, cert=privatekey)
    #         parsed_json = json.dumps(request.json(), indent=4)
    #         leave_table = json.loads(parsed_json)
    #         statuscode = leave_table['Statuscode']
    #         counter += 1

    #     if statuscode != '200':
    #         _logger.info('RUN ATTENTIA IMPORT FAILED: %s' % (statuscode))
    #         return None

    #     return leave_table['Response'] if leave_table else None

    # def get_attentia_leave_data(self, privatekey: tuple[str, str], load_from: date) -> str | None:
    #     """ Retrieves leaves data from Attentia API for this employee starting from the given date. """

    #     api_url_worker = '%s/worker/%s/%s/%s' % (UcamcoConstants.ATTENTIA_API_BASE_URL, self.employee_nbr, 'absences', load_from.strftime('%Y%m%d'))

    #     request = requests.get(url=api_url_worker, cert=privatekey, headers=UcamcoConstants.ATTENTIA_API_UCAMCO_EMPLOYER_PARAMS)

    #     api_url_result = '%s/%s/%s' % (UcamcoConstants.ATTENTIA_API_BASE_URL, 'Result', request.json())

    #     return self.get_attentia_data(api_url_result, privatekey)

    # def json_to_attentia_records(self, attentia_data: str, attentia_to_odoo_dict: dict):
    #     """ Converts JSON data from Attentia into a list of AttentiaRecord objects. """
    #     records = []
    #     record: AttentiaRecord
    #     for attentia_entry in json.loads(attentia_data):
    #         record = AttentiaRecord.from_json(json.dumps(attentia_entry))
    #         record._attentia_to_odoo_dict = attentia_to_odoo_dict
    #         records.append(record)
            
    #         _logger.debug('Attentia records: %s', records)

    #     return records

    # def _unsubscribe_followers(self, model) -> None:
    #     # Unsubscribe all followers
    #     # moved that to the automated action as it's too invasive here...
    #     # model.message_unsubscribe(partner_ids=model.message_partner_ids.ids)
    #     pass


    # def _strip_time_from_leave(self, leave):
    #     # stripping time from the leave
    #     leave.date_from = leave.date_from.date()
    #     leave.date_to = leave.date_to.date()
    #     leave.request_hour_from = 0.0
    #     leave.request_hour_to = 0.0
    #     return leave

    # def _override_calendar_event_name(self, leave) -> None:
    #     # overriding the name with the same as the time off
    #     calendar_event = self.env['calendar.event'].search([('res_model', '=', 'hr.leave'), ('res_id', '=', leave.id)], limit=1)
    #     if calendar_event:
    #         new_name = leave.display_name
    #         if leave.employee_id.user_id.partner_id.ref:
    #             new_name = new_name.replace(leave.employee_id.name, '[' + leave.employee_id.user_id.partner_id.ref + ']')
    #         calendar_event.name = new_name
    #     else:
    #         _logger.warning(f'No calendar event found for {leave}')

    # def _get_or_update_full_day_date_values(self, date_from, date_to, existing_values: dict | None = None):
    #     if not existing_values:
    #         existing_values = {}
    #     existing_values['date_from'] = date_from
    #     existing_values['date_to'] = date_to
    #     existing_values['request_date_from'] = date_from
    #     existing_values['request_date_to'] = date_to
    #     existing_values['request_hour_from'] = UcamcoUtils.time_to_float_hours(UcamcoUtils.convert_from_gmt_to_brussels(date_from).time())
    #     existing_values['request_hour_to'] = UcamcoUtils.time_to_float_hours(UcamcoUtils.convert_from_gmt_to_brussels(date_to).time())
    #     return existing_values

    # def _remove_calendar_event(self, leave):
    #     calendar_event = self.env['calendar.event'].search([('res_model', '=', 'hr.leave'), ('res_id', '=', leave.id)], limit=1)
    #     if calendar_event:
    #         calendar_event.unlink()
    #     else:
    #         _logger.warning(f'No calendar event found for {leave}')

    # def _confirm_leave(self, leave):
    #     leave.action_confirm()
    #     _logger.info(f'Confirmed leave {leave}.')

    # def _approve_leave(self, leave):
    #     leave.action_approve()
    #     _logger.info(f'Approved leave {leave}.')

    # def _draft_leave(self, leave):
    #     leave.action_draft()
    #     _logger.info(f'Drafted leave {leave}.')

    # def _refuse_leave(self, leave):
    #     leave.action_refuse()
    #     _logger.info(f'Refused leave {leave}.')

    # def _remove_leave(self, leave):
    #     self._remove_calendar_event(leave)
    #     self._refuse_leave(leave)
    #     self._draft_leave(leave)
    #     leave.unlink()
    #     _logger.info(f'Removed leave {leave}.')

    # def process_record(self, HrLeave, employee, existing_leaves, index: int, total_records: int, record: AttentiaRecord, previous_leave_created):
    #     creation_values = {}
    #     leave_created = None
    #     if record.load_in_odoo():
    #         _logger.info("Processing record %d/%d: %s %s" % (index, total_records, self.id, record))

    #         try:
    #             work_hours_in_days = record._calculate_work_hours_in_days(employee)
    #         except Exception as e:
    #             _logger.warning(f"Error calculating work hours for {employee} and {record}: {e}")
    #             return None

    #         # Find existing leaves matching the record
    #         matching_leaves = existing_leaves.filtered(
    #             lambda leave: (leave.holiday_status_id.id == record.attentia_to_odoo_id(self.env)) and
    #                         (leave.date_from.date() == record.dayAsDateTime().date()) and
    #                         (leave.attentia_code == record.code())
    #         )
            
    #         try:
    #             if matching_leaves:
    #                 # Handle updates
    #                 for leave in matching_leaves:
    #                     # little trick to be able to skip a leave that comes from the interface and that shouldn't be there
    #                     if leave.state == 'refuse':
    #                         # attention - if not processed without this, the leave will be deleted and processed again and again
    #                         leave.attentia_processed = True
    #                         _logger.info(f"Skipping leave {leave.id} as it's refused.")
    #                         return None
    #                     expected_days = work_hours_in_days #record._calculate_work_hours_in_days(employee)
    #                     # print('abs', abs(leave.number_of_days - expected_days), 'current', leave.number_of_days, 'expected', expected_days, 'within treshold', abs(leave.number_of_days - expected_days) > 0.02)
    #                     if leave.number_of_days != expected_days and abs(leave.number_of_days - expected_days) > 0.02:
    #                         _logger.info('Updating existing leave %s' % leave.id)
    #                         self._refuse_leave(leave)
    #                         self._draft_leave(leave)
    #                         if record.is_full_day():
    #                             date_from = record.date_from(self)
    #                             date_to = record.date_to(self, date_from)
    #                             leave.write(self._get_or_update_full_day_date_values(date_from, date_to))
    #                         else:
    #                             self._strip_time_from_leave(leave)
    #                         leave.number_of_days = expected_days
    #                         # self._confirm_leave(leave) # not necessary anymore Odoo 19
    #                         self._approve_leave(leave)
    #                         self._override_calendar_event_name(leave)
    #                     else:
    #                         _logger.info('Leave already up to date %s' % leave.id)
    #                     # mark the leave as processed
    #                     leave.attentia_processed = True
    #             else:
    #                 _logger.info(f"creating as not the same as {record}")
                    
    #                 creation_values: dict = {
    #                     'name': f'{employee.name} - {record.attentia_to_odoo_name()}',
    #                     'employee_id': employee.id,
    #                     'holiday_status_id': record.attentia_to_odoo_id(self.env),
    #                     'attentia_code': record.code(),
    #                     'state': 'confirm',
    #                 }
    #                 date_from = record.date_from(self)
    #                 date_to = record.date_to(self, date_from)
    #                 if record.is_full_day():
    #                     self._get_or_update_full_day_date_values(date_from, date_to, creation_values)
    #                 else:
    #                     creation_values['date_from'] = date_from.date()
    #                     creation_values['date_to'] = date_to.date()
                        
    #                 creation_values['number_of_days'] = work_hours_in_days #record._calculate_work_hours_in_days(employee)
                    
    #                 leave_created = HrLeave.with_context(mail_auto_subscribe_no_notify=True, mail_create_nosubscribe=True).create(creation_values)

    #                 self._unsubscribe_followers(leave_created)

    #                 # self._confirm_leave(leave_created) # not necessary anymore Odoo 19

    #                 self._unsubscribe_followers(leave_created)

    #                 self._approve_leave(leave_created)
                    
    #                 _logger.info(f'Created leave {leave_created} with values {creation_values}.')

    #                 self._override_calendar_event_name(leave_created)

    #                 # Mark the leave as processed
    #                 leave_created.attentia_processed = True
    #                 existing_leaves |= leave_created  # Add to existing_leaves for future reference
            
    #         except ValidationError as ve:
    #             # rounding problems will cause this error for the last entry?
    #             if ve.args and 'remaining time off is not sufficient for this time off type' in ve.args[0]:  
    #                 _logger.warning("Warning processing record: %s %s [%s]" % (employee.id, record, ve))
    #                 # deleting the leave that we created as it won't approve automatically cause there isn't enough allocation
    #                 try:
    #                     _logger.info(f'Should I unlink? {leave_created}?')
    #                     if leave_created:
    #                         lea = HrLeave.browse(leave_created.id)
    #                     else:
    #                         raise Exception('No leave was created!')

    #                     self._draft_leave(lea)

    #                     hours_left = self.env['hr.leave.type'].browse(record.attentia_to_odoo_id(self.env)).get_employees_days([self.id])[self.id][record.attentia_to_odoo_id(self.env)].get('remaining_leaves', 0.0)

    #                     # removing the time as it could interfere with the number of days 
    #                     # which is not exactly a full day...
    #                     lea = self._strip_time_from_leave(lea)
                        
    #                     lea.number_of_days = hours_left / record._get_employee_work_hours_for_weekday(employee) # record._calculate_work_hours_in_days(employee)
    #                     lea.number_of_hours_display = hours_left

    #                     self._unsubscribe_followers(lea)

    #                     self._confirm_leave(lea)

    #                     self._unsubscribe_followers(leave_created)

    #                     self._approve_leave(lea)

    #                     self._override_calendar_event_name(lea)
                        
    #                 except Exception as e2:
    #                     _logger.error("Failed processing/updating record: %s %s [%s]" % (employee.id, record, e2))

    #             elif ve.args and 'two time off that overlap on the same day' in ve.args[0]:
    #                 """ You can not set two time off that overlap on the same day for the same employee.
    #                 Not really a problem with the Attentia interface, but with the Odoo interface for example
    #                 with recup. """
    #                 _logger.warning("Warning processing record (overlap): %s %s [%s] | %s" % (employee.id, record, ve, creation_values))
    #                 # at this point actually the leave is created, but leave_created is None
    #                 if leave_created:
    #                     lea = HrLeave.browse(leave_created.id)
    #                     self._draft_leave(lea)
    #                     if record.is_full_day():
    #                         lea = self._strip_time_from_leave(lea)
    #                     self._unsubscribe_followers(lea)
    #                     self._confirm_leave(lea)
    #                     self._unsubscribe_followers(lea)
    #                     self._approve_leave(lea)
    #                     self._override_calendar_event_name(lea)
    #                 else:
    #                     if previous_leave_created:
    #                         lea = HrLeave.browse(previous_leave_created.id + 1)
    #                         lea.number_of_days = work_hours_in_days #record._calculate_work_hours_in_days(employee)
    #                         self._unsubscribe_followers(lea)
    #                         self._confirm_leave(lea)
    #                         self._unsubscribe_followers(lea)
    #                         self._approve_leave(lea)
    #                         self._override_calendar_event_name(lea)
    #             else:
    #                 _logger.error("Error processing record: %s %s [%s]" % (employee.id, record, ve))

    #         except Exception as e:
    #             _logger.error("Error processing record*: %s %s [%s]" % (employee.id, record, e))
                
    #     else:
    #         _logger.info("Skipping record: %s %s" % (employee.id, record))
    #         return None

    #     return leave_created
        
    # def attentia_import_new_do(self):
    #     _logger.info(f'Running attentia import for {self.name}...')

    #     employee = self
    #     employee_id = self.id
    #     employee_name = self.name
    #     user_id = self.user_id and self.user_id.id or False

    #     # setup AttentiatoOdoo mapping
    #     attentia_to_odoo_dict = self.setup_attentia_to_odoo_dict(datetime.now().year, datetime.now().year - 1)

    #     privatekey = self._load_private_key()
        
    #     if self.attentia_data_import:
    #         self.import_attentia_employee_information(privatekey)

    #     if self.attentia_leave_import: #and not self.user_id.field_engineer:
    #         _logger.info(f'Loading attentia leaves information for {employee_name}...')
    #         attentia_leave_load_from_initial = datetime(2024, 1, 1).date()
    #         param_value = self.env['ir.config_parameter'].sudo().get_param(UcamcoConstants.ATTENTIA_LEAVES_LOAD_FROM_SYSTEM_PARAMETER)
    #         if param_value:
    #             attentia_leave_load_from = date.fromisoformat(param_value)
    #             # the interface can't run on dates from previous year when year has changed
    #             if attentia_leave_load_from.year < datetime.now().year:
    #                 new_year = date(datetime.now().year, 1, 1)  
    #                 self.env['ir.config_parameter'].sudo().set_param(UcamcoConstants.ATTENTIA_LEAVES_LOAD_FROM_SYSTEM_PARAMETER, new_year)
    #                 attentia_leave_load_from = new_year
    #         else:
    #             self.env['ir.config_parameter'].sudo().set_param(UcamcoConstants.ATTENTIA_LEAVES_LOAD_FROM_SYSTEM_PARAMETER, attentia_leave_load_from_initial)
    #             attentia_leave_load_from = attentia_leave_load_from_initial

    #         attentia_data = self.get_attentia_leave_data(privatekey, attentia_leave_load_from)

    #         if not(attentia_data):
    #             raise UserError(f'No attentia leave data received for {employee_name}.')

    #         _logger.info(f'Attentia data received: {attentia_data}')

    #         """ Example response:
    #         [
    #             {'Day': '20240101', 'Code': 100, 'Shift': 1, 'Hours': 0.0},
    #             {'Day': '20240102', 'Code': 151, 'Shift': 1, 'Hours': 0.0},
    #             {'Day': '20240103', 'Code': 9, 'Shift': 1, 'Hours': 0.0},
    #             {'Day': '20240104', 'Code': 9, 'Shift': 1, 'Hours': 0.0},
    #             {'Day': '20240105', 'Code': 9, 'Shift': 1, 'Hours': 0.0},
    #             {'Day': '20240108', 'Code': 9, 'Shift': 1, 'Hours': 0.0},
    #             {'Day': '20240115', 'Code': 9, 'Shift': 1, 'Hours': 0.0},
    #             {'Day': '20240117', 'Code': 9, 'Shift': 1, 'Hours': 0.0}
    #         ]
    #         """

    #         records = self.json_to_attentia_records(attentia_data, attentia_to_odoo_dict)
            
    #         HrLeave = self.env['hr.leave']

    #         existing_leaves = HrLeave.search([('employee_id', '=', employee_id), ('holiday_status_id', 'ilike', 'Attentia%'),('date_from','>=',attentia_leave_load_from)])
    #         existing_leaves.write({'attentia_processed': False})

    #         previous_leave = None

    #         for index, record in enumerate(records):

    #             previous_leave = self.process_record(HrLeave, employee, existing_leaves, index, len(records), record, previous_leave)

    #         # After processing all records:
    #         unprocessed_leaves = existing_leaves.filtered(lambda existing_leave: not existing_leave.attentia_processed)
    #         for unprocessed_leave in unprocessed_leaves:
    #             _logger.info('Removing unprocessed leave %s %s %s %s' % (unprocessed_leave.id, unprocessed_leave.name, unprocessed_leave.date_from, unprocessed_leave.number_of_days))
                
    #             self._remove_leave(unprocessed_leave)

    #         _logger.info(f'Loaded attentia leaves information for {employee_name} from {attentia_leave_load_from}.')

    #     return True
