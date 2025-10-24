from odoo import fields, models

class SalesPerson(models.Model):
    _name = "sales_person"
    _description = "Sales Person"

    name = fields.Char()
    phone = fields.Char()
    email = fields.Char()

    activate = fields.Boolean(default=True)

    gender = fields.Selection(selection=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
