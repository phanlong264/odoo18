from odoo import fields, models

class ImageOffers(models.Model):
    _name = "image_offers"
    _description = "Image Offers"

    name = fields.Char()

    offers = fields.Many2one("offers")
    image_offers = fields.Image(max_width=500, max_height=500, verify_resolution=True)