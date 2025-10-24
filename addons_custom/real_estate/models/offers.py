from odoo import fields, models

class Offers(models.Model):
    _name = "offers"
    _description = "Offers"

    name = fields.Char()

    property=fields.Many2one("real_estate")

    expected_price=fields.Monetary(currency_field="currency_id")
    currency_id=fields.Many2one("res.currency")

    image_offers=fields.One2many("image_offers" , "offers")