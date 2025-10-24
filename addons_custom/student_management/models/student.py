from odoo import fields, models, api
from odoo.http import request
from odoo.exceptions import ValidationError

class Student(models.Model):
    _name = 'student.student'
    _description = 'Student Info'

    name = fields.Char(string='Name')
    student_id = fields.Char(string='Student ID', required=True)  # st001, st002
    image = fields.Binary(string='Image')
    dob = fields.Date(string='Date of birth')
    gender = fields.Selection([
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other')
    ], string='Gender')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    guardian_name = fields.Char(string='Guardian Name')
    guardian_phone = fields.Char(string='Guardian Phone')
    admission_date = fields.Date(string='Admission Date')
    address = fields.Char(string='Address')

    def print_something(self):
        print('The button got clicked')

    @api.model_create_multi
    def create(self, vals):
        existing_students = request.env['student.student'].search([])
        for student in existing_students:
            if student.student_id == vals.get('student_id'):
                raise ValidationError('A student with this student id already exists')
        return super().create(vals)


    def write(self, vals):
        existing_students = request.env['student.student'].search([])
        for student in existing_students:
            if student.student_id == vals.get('student_id'):
                raise ValidationError('A student with this student id already exists')
        return super().write(vals)