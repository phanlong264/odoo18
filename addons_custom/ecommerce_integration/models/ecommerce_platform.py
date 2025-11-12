# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EcommercePlatform(models.Model):
    _name = 'ecommerce.platform'
    _description = 'E-commerce Platform'
    _order = 'sequence, name'

    name = fields.Char(string='Platform Name', required=True)
    code = fields.Selection([
        ('shopee', 'Shopee'),
        ('tiktok', 'TikTok Shop'),
        ('lazada', 'Lazada'),
        ('amazon', 'Amazon'),
    ], string='Platform Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    icon = fields.Char(string='Icon Class', help='Font Awesome icon class')
    color = fields.Char(string='Color', default='#000000')
    shop_ids = fields.One2many('ecommerce.shop', 'platform_id', string='Shops')
    shop_count = fields.Integer(string='Shop Count', compute='_compute_shop_count')
    oauth_url = fields.Char(string='OAuth URL')
    api_endpoint = fields.Char(string='API Endpoint')
    
    @api.depends('shop_ids')
    def _compute_shop_count(self):
        for platform in self:
            platform.shop_count = len(platform.shop_ids)
