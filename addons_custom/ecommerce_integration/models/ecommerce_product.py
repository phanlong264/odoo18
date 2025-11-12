# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EcommerceProduct(models.Model):
    _name = 'ecommerce.product'
    _description = 'E-commerce Product'
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Tên sản phẩm', required=True)
    product_id = fields.Char(string='ID sản phẩm sàn', required=True)
    shop_id = fields.Many2one('ecommerce.shop', string='Gian hàng', required=True, ondelete='cascade')
    platform_id = fields.Many2one(related='shop_id.platform_id', string='Nền tảng', store=True)
    
    # Thông tin sản phẩm
    sku = fields.Char(string='SKU')
    barcode = fields.Char(string='Mã vạch')
    description = fields.Text(string='Mô tả')
    category_name = fields.Char(string='Danh mục')
    
    # Giá và tồn kho
    price = fields.Float(string='Giá bán')
    cost_price = fields.Float(string='Giá vốn')
    stock_quantity = fields.Integer(string='Tồn kho', default=0)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', 
                                   default=lambda self: self.env.company.currency_id)
    
    # Trạng thái
    status = fields.Selection([
        ('active', 'Đang bán'),
        ('inactive', 'Ngừng bán'),
        ('out_of_stock', 'Hết hàng'),
    ], string='Trạng thái', default='active')
    
    # Liên kết với Odoo
    odoo_product_id = fields.Many2one('product.product', string='Sản phẩm Odoo')
    is_synced = fields.Boolean(string='Đã đồng bộ', default=False)
    last_sync_date = fields.Datetime(string='Lần đồng bộ cuối')
    
    # Hình ảnh
    image_url = fields.Char(string='URL hình ảnh')
    image = fields.Binary(string='Hình ảnh', attachment=True)
    
    # Thông tin bổ sung
    weight = fields.Float(string='Trọng lượng (kg)')
    length = fields.Float(string='Dài (cm)')
    width = fields.Float(string='Rộng (cm)')
    height = fields.Float(string='Cao (cm)')
    
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('product_shop_unique', 'unique(product_id, shop_id)', 
         'Sản phẩm này đã tồn tại trong gian hàng!')
    ]
    
    def action_sync_to_odoo(self):
        """Đồng bộ sản phẩm sang Odoo"""
        self.ensure_one()
        
        # Tìm hoặc tạo sản phẩm trong Odoo
        ProductProduct = self.env['product.product']
        
        if self.odoo_product_id:
            # Cập nhật sản phẩm đã có
            self.odoo_product_id.write({
                'name': self.name,
                'default_code': self.sku or self.product_id,
                'barcode': self.barcode,
                'list_price': self.price,
                'standard_price': self.cost_price,
                'description_sale': self.description,
                'weight': self.weight,
            })
        else:
            # Tạo sản phẩm mới
            product = ProductProduct.create({
                'name': self.name,
                'default_code': self.sku or self.product_id,
                'barcode': self.barcode,
                'list_price': self.price,
                'standard_price': self.cost_price,
                'description_sale': self.description,
                'weight': self.weight,
                'type': 'product',
                'categ_id': self.env.ref('product.product_category_all').id,
            })
            self.odoo_product_id = product.id
        
        self.is_synced = True
        self.last_sync_date = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': f'Đã đồng bộ sản phẩm: {self.name}',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_open_odoo_product(self):
        """Mở sản phẩm Odoo"""
        self.ensure_one()
        if not self.odoo_product_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Lỗi',
                    'message': 'Sản phẩm chưa được đồng bộ vào Odoo',
                    'type': 'warning',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'res_id': self.odoo_product_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
