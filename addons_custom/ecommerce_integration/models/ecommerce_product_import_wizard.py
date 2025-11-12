# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import random


class EcommerceProductImportWizard(models.TransientModel):
    _name = 'ecommerce.product.import.wizard'
    _description = 'Import Product from E-commerce Platform'

    shop_id = fields.Many2one('ecommerce.shop', string='Gian hàng', required=True)
    platform_id = fields.Many2one(related='shop_id.platform_id', string='Nền tảng', readonly=True)
    
    # Điều kiện import
    import_type = fields.Selection([
        ('all', 'Tất cả sản phẩm'),
        ('active', 'Chỉ sản phẩm đang bán'),
        ('new', 'Chỉ sản phẩm mới'),
    ], string='Loại import', default='all', required=True)
    
    category_filter = fields.Char(string='Lọc theo danh mục')
    min_price = fields.Float(string='Giá tối thiểu')
    max_price = fields.Float(string='Giá tối đa')
    
    # Tùy chọn đồng bộ
    auto_sync_to_odoo = fields.Boolean(string='Tự động đồng bộ vào Odoo', default=False)
    update_existing = fields.Boolean(string='Cập nhật sản phẩm đã có', default=True)
    
    # Kết quả
    result_message = fields.Text(string='Kết quả', readonly=True)
    
    def action_import_products(self):
        """Import sản phẩm từ sàn"""
        self.ensure_one()
        
        if not self.shop_id.access_token:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Lỗi',
                    'message': 'Gian hàng chưa được kết nối. Vui lòng kết nối trước.',
                    'type': 'danger',
                }
            }
        
        # TODO: Gọi API thực tế của từng sàn (Shopee, Lazada, TikTok...)
        # Đây là demo data
        products_data = self._fetch_products_from_platform()
        
        created_count = 0
        updated_count = 0
        EcommerceProduct = self.env['ecommerce.product']
        
        for product_data in products_data:
            # Kiểm tra sản phẩm đã tồn tại
            existing_product = EcommerceProduct.search([
                ('product_id', '=', product_data['product_id']),
                ('shop_id', '=', self.shop_id.id)
            ], limit=1)
            
            if existing_product:
                if self.update_existing:
                    existing_product.write(product_data)
                    updated_count += 1
            else:
                product_data['shop_id'] = self.shop_id.id
                product = EcommerceProduct.create(product_data)
                created_count += 1
                
                # Tự động đồng bộ vào Odoo nếu được chọn
                if self.auto_sync_to_odoo:
                    product.action_sync_to_odoo()
        
        result_msg = f"Đã import thành công!\n"
        result_msg += f"- Tạo mới: {created_count} sản phẩm\n"
        result_msg += f"- Cập nhật: {updated_count} sản phẩm"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': result_msg,
                'type': 'success',
                'sticky': True,
            }
        }
    
    def _fetch_products_from_platform(self):
        """
        Hàm này sẽ gọi API của từng sàn để lấy danh sách sản phẩm
        TODO: Implement API call cho từng platform
        """
        # Demo data - Trong thực tế sẽ gọi API
        platform_code = self.shop_id.platform_id.code
        
        # Giả lập dữ liệu sản phẩm
        demo_products = []
        for i in range(1, 6):  # Tạo 5 sản phẩm demo
            product = {
                'name': f'Sản phẩm {platform_code} {i}',
                'product_id': f'{platform_code.upper()}-{random.randint(100000, 999999)}',
                'sku': f'SKU-{random.randint(1000, 9999)}',
                'description': f'Mô tả sản phẩm {i} từ {self.shop_id.platform_id.name}',
                'price': random.randint(100, 1000) * 1000,
                'cost_price': random.randint(50, 500) * 1000,
                'stock_quantity': random.randint(10, 100),
                'status': 'active',
                'category_name': 'Electronics',
            }
            
            # Áp dụng filter
            if self.import_type == 'active' and product['status'] != 'active':
                continue
            
            if self.min_price and product['price'] < self.min_price:
                continue
                
            if self.max_price and product['price'] > self.max_price:
                continue
            
            demo_products.append(product)
        
        return demo_products
    
    def action_view_imported_products(self):
        """Xem danh sách sản phẩm đã import"""
        self.ensure_one()
        
        return {
            'name': 'Sản phẩm đã import',
            'type': 'ir.actions.act_window',
            'res_model': 'ecommerce.product',
            'view_mode': 'tree,form',
            'domain': [('shop_id', '=', self.shop_id.id)],
            'context': {'default_shop_id': self.shop_id.id},
        }
