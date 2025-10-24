from odoo import fields, models

class RealEstate(models.Model):
    _name = "real_estate"
    _description = "Real Estate"

    name = fields.Char()
    phone = fields.Char()
    email = fields.Char()
    description = fields.Text()

    manager = fields.Many2one("sales_person", domain=[('activate', '=', True)], 
                              context={'default_activate': True}, ondelete='cascade', delegate=True)
    
    buyers = fields.Many2many("buyers")

    offers = fields.One2many("offers", "property")