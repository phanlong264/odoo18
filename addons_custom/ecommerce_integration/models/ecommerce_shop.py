# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class EcommerceShop(models.Model):
    _name = 'ecommerce.shop'
    _description = 'E-commerce Shop'
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Tên gian hàng', required=True)
    shop_id = fields.Char(string='ID gian hàng', required=True)
    platform_id = fields.Many2one('ecommerce.platform', string='Sàn TMĐT', required=True, ondelete='cascade')
    platform_code = fields.Selection(related='platform_id.code', string='Platform Code', store=True)
    status = fields.Selection([
        ('active', 'Kích hoạt'),
        ('expired', 'Hết hạn'),
        ('pending', 'Chờ kết nối'),
    ], string='Trạng thái kết nối', default='pending', required=True)
    last_sync_date = fields.Datetime(string='Lần đồng bộ cuối')
    access_token = fields.Char(string='Access Token')
    refresh_token = fields.Char(string='Refresh Token')
    token_expire_date = fields.Datetime(string='Token hết hạn')
    shop_url = fields.Char(string='URL gian hàng')
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Ghi chú')
    
    # Thông tin bổ sung
    image = fields.Binary(string='Ảnh gian hàng', attachment=True)
    owner_name = fields.Char(string='Chủ gian hàng')
    phone = fields.Char(string='Số điện thoại')
    email = fields.Char(string='Email')
    region = fields.Char(string='Khu vực', default='Việt Nam')
    effective_date = fields.Date(string='Ngày hiệu lực')
    
    # Thông tin quản trị
    sales_team = fields.Char(string='Đội ngũ bán hàng')
    business_household = fields.Char(string='Hộ kinh doanh')
    company_name = fields.Char(string='Công ty')
    customer_source = fields.Char(string='Nguồn khách hàng')
    
    # Thông tin quản lý kết nối
    auto_import_product_days = fields.Integer(string='Auto import sản phẩm (days)', default=1)
    auto_export_product_days = fields.Integer(string='Auto export sản phẩm (days)', default=1)
    auto_import_order_days = fields.Integer(string='Auto import đơn hàng (days)', default=1)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set initial status for batch creation"""
        for vals in vals_list:
            if 'access_token' in vals and vals.get('access_token'):
                vals['status'] = 'active'
        return super(EcommerceShop, self).create(vals_list)
    
    def action_connect(self):
        """Open connection wizard"""
        self.ensure_one()
        return {
            'name': f'Kết nối với {self.platform_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'ecommerce.shop.connect.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_platform_id': self.platform_id.id,
            }
        }
    
    def action_refresh_token(self):
        """Refresh access token"""
        self.ensure_one()
        # Logic để refresh token sẽ được implement sau
        self.status = 'active'
        self.token_expire_date = datetime.now() + timedelta(days=30)
        return True
    
    def action_disconnect(self):
        """Disconnect shop"""
        self.ensure_one()
        self.write({
            'status': 'expired',
            'access_token': False,
            'refresh_token': False,
        })
        return True
    
    def action_import_products(self):
        """Open import products wizard"""
        self.ensure_one()
        return {
            'name': 'Import sản phẩm từ sàn',
            'type': 'ir.actions.act_window',
            'res_model': 'ecommerce.product.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_shop_id': self.id},
        }
    
    def action_import_orders(self):
        """Open import orders wizard"""
        self.ensure_one()
        return {
            'name': 'Import đơn hàng từ sàn',
            'type': 'ir.actions.act_window',
            'res_model': 'ecommerce.order.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_shop_id': self.id},
        }
    
    def action_update_stock(self):
        """Open stock update wizard"""
        self.ensure_one()
        
        # Create wizard
        wizard = self.env['ecommerce.stock.update.wizard'].create({
            'shop_id': self.id,
        })
        
        # Call update action
        return wizard.action_update_stock()
