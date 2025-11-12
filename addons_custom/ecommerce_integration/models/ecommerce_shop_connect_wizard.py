# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class EcommerceShopConnectWizard(models.TransientModel):
    _name = 'ecommerce.shop.connect.wizard'
    _description = 'Connect E-commerce Shop Wizard'

    platform_id = fields.Many2one('ecommerce.platform', string='Sàn TMĐT', required=True)
    shop_name = fields.Char(string='Tên gian hàng', required=True)
    shop_id = fields.Char(string='ID gian hàng', required=True)
    api_key = fields.Char(string='API Key')
    api_secret = fields.Char(string='API Secret')
    access_token = fields.Char(string='Access Token')
    owner_name = fields.Char(string='Chủ gian hàng')
    phone = fields.Char(string='Số điện thoại')
    email = fields.Char(string='Email')
    shop_url = fields.Char(string='URL gian hàng')
    
    def action_connect(self):
        """Create new shop connection"""
        self.ensure_one()
        
        # Tạo shop mới
        shop_vals = {
            'name': self.shop_name,
            'shop_id': self.shop_id,
            'platform_id': self.platform_id.id,
            'access_token': self.access_token or self.api_key,
            'refresh_token': self.api_secret,
            'status': 'active',
            'token_expire_date': datetime.now() + timedelta(days=30),
            'shop_url': self.shop_url,
            'owner_name': self.owner_name,
            'phone': self.phone,
            'email': self.email,
        }
        
        shop = self.env['ecommerce.shop'].create(shop_vals)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã kết nối gian hàng {self.shop_name} thành công!',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_oauth_connect(self):
        """Open OAuth connection"""
        self.ensure_one()
        
        if not self.platform_id.oauth_url:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Lỗi',
                    'message': 'URL OAuth chưa được cấu hình cho sàn này.',
                    'type': 'warning',
                }
            }
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.platform_id.oauth_url,
            'target': 'new',
        }
