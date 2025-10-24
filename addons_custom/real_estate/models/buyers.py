from odoo import fields, models

class Buyers(models.Model):
    _name = "buyers"
    _description = "Buyers"

    name = fields.Char()
    phone = fields.Char()
    email = fields.Char()
    address = fields.Char()
    description = fields.Text(string="Description")