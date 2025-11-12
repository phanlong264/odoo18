# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EcommerceIntegration(models.Model):
    _name = 'ecommerce.integration'
    _description = 'E-commerce Integration'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    platform = fields.Selection([
        ('shopify', 'Shopify'),
        ('woocommerce', 'WooCommerce'),
        ('magento', 'Magento'),
        ('other', 'Other'),
    ], string='Platform', required=True)
    active = fields.Boolean(string='Active', default=True)
    api_key = fields.Char(string='API Key')
    api_secret = fields.Char(string='API Secret')
    store_url = fields.Char(string='Store URL')
    notes = fields.Text(string='Notes')
