# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import random


class EcommerceOrderImportWizard(models.TransientModel):
    _name = 'ecommerce.order.import.wizard'
    _description = 'E-commerce Order Import Wizard'

    shop_id = fields.Many2one('ecommerce.shop', string='Gian hàng', required=True)
    platform_id = fields.Many2one('ecommerce.platform', related='shop_id.platform_id',
                                  string='Sàn TMĐT', readonly=True)
    
    # Date Range Filter
    date_from = fields.Date(string='Từ ngày', required=True,
                           default=lambda self: fields.Date.today() - timedelta(days=30))
    date_to = fields.Date(string='Đến ngày', required=True,
                         default=fields.Date.today)
    
    # Status Filter
    status_filter = fields.Many2many('ecommerce.order.status', string='Trạng thái đơn hàng',
                                    help='Chọn trạng thái đơn hàng cần import')
    
    # Options
    auto_sync_to_odoo = fields.Boolean(string='Tự động đồng bộ vào Odoo',
                                       help='Tự động tạo Sale Order trong Odoo sau khi import')
    update_existing = fields.Boolean(string='Cập nhật đơn hàng đã tồn tại', 
                                     default=True,
                                     help='Cập nhật thông tin nếu đơn hàng đã tồn tại')
    
    # Results
    imported_count = fields.Integer(string='Số đơn đã import', readonly=True)
    updated_count = fields.Integer(string='Số đơn đã cập nhật', readonly=True)

    def action_import_orders(self):
        """Import orders from e-commerce platform"""
        self.ensure_one()
        
        if not self.shop_id:
            raise UserError('Vui lòng chọn gian hàng!')
        
        if self.date_from > self.date_to:
            raise UserError('Từ ngày phải nhỏ hơn Đến ngày!')
        
        # Fetch orders from platform API (demo implementation)
        orders_data = self._fetch_orders_from_platform()
        
        imported = 0
        updated = 0
        created_order_ids = []
        
        for order_data in orders_data:
            # Check if order already exists
            existing_order = self.env['ecommerce.order'].search([
                ('order_id', '=', order_data['order_id']),
                ('shop_id', '=', self.shop_id.id)
            ], limit=1)
            
            if existing_order:
                if self.update_existing:
                    existing_order.write(order_data)
                    updated += 1
            else:
                new_order = self.env['ecommerce.order'].create(order_data)
                created_order_ids.append(new_order.id)
                imported += 1
                
                # Auto sync to Odoo if enabled
                if self.auto_sync_to_odoo:
                    try:
                        new_order.action_sync_to_odoo()
                    except Exception as e:
                        # Log error but continue importing
                        new_order.message_post(
                            body=f'Lỗi đồng bộ tự động: {str(e)}'
                        )
        
        self.write({
            'imported_count': imported,
            'updated_count': updated,
        })
        
        # Show result
        return self.action_view_imported_orders(created_order_ids)

    def _fetch_orders_from_platform(self):
        """
        Fetch orders from platform API
        This is a demo implementation - replace with actual API calls
        """
        self.ensure_one()
        
        # Demo: Generate random orders
        orders_data = []
        statuses = ['pending', 'confirmed', 'processing', 'shipping', 'delivered', 'completed']
        payment_statuses = ['unpaid', 'partial', 'paid']
        
        # Filter by selected statuses
        if self.status_filter:
            filter_statuses = [s.code for s in self.status_filter]
        else:
            filter_statuses = statuses
        
        # Generate 3-8 random orders
        num_orders = random.randint(3, 8)
        
        for i in range(num_orders):
            order_date = datetime.combine(
                self.date_from + timedelta(days=random.randint(0, (self.date_to - self.date_from).days)),
                datetime.min.time()
            )
            
            status = random.choice(filter_statuses)
            
            # Generate order lines
            num_lines = random.randint(1, 4)
            order_lines = []
            
            for j in range(num_lines):
                order_lines.append((0, 0, {
                    'product_name': f'Sản phẩm {random.choice(["A", "B", "C", "D", "E"])} - Size {random.choice(["S", "M", "L", "XL"])}',
                    'product_sku': f'SKU-{random.randint(1000, 9999)}',
                    'quantity': random.randint(1, 5),
                    'unit_price': random.uniform(100000, 2000000),
                    'variant_name': random.choice(['Đỏ', 'Xanh', 'Vàng', 'Trắng', 'Đen']),
                }))
            
            orders_data.append({
                'name': f'ORD-{self.platform_id.code}-{random.randint(100000, 999999)}',
                'order_id': f'{self.platform_id.code.upper()}{random.randint(10000000, 99999999)}',
                'shop_id': self.shop_id.id,
                'order_date': order_date,
                'customer_name': random.choice([
                    'Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 
                    'Phạm Thị D', 'Hoàng Văn E', 'Vũ Thị F'
                ]),
                'customer_phone': f'09{random.randint(10000000, 99999999)}',
                'customer_email': f'customer{random.randint(1, 999)}@example.com',
                'shipping_address': f'{random.randint(1, 999)} Đường ABC, Quận {random.randint(1, 12)}, TP.HCM',
                'status': status,
                'payment_status': random.choice(payment_statuses),
                'payment_method': random.choice(['COD', 'Chuyển khoản', 'Ví điện tử', 'Thẻ tín dụng']),
                'shipping_method': random.choice(['Giao hàng tiêu chuẩn', 'Giao hàng nhanh', 'Giao hàng siêu tốc']),
                'shipping_fee': random.uniform(15000, 50000),
                'discount_amount': random.uniform(0, 100000),
                'tracking_number': f'TRK{random.randint(1000000000, 9999999999)}',
                'order_line_ids': order_lines,
                'note': random.choice(['', 'Giao hàng giờ hành chính', 'Gọi trước khi giao', '']),
            })
        
        return orders_data

    def action_view_imported_orders(self, order_ids):
        """View imported orders"""
        self.ensure_one()
        
        return {
            'name': 'Đơn hàng đã import',
            'type': 'ir.actions.act_window',
            'res_model': 'ecommerce.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', order_ids)],
            'context': {'create': False},
        }


class EcommerceOrderStatus(models.Model):
    _name = 'ecommerce.order.status'
    _description = 'E-commerce Order Status'
    _order = 'sequence, name'

    name = fields.Char(string='Tên trạng thái', required=True, translate=True)
    code = fields.Selection([
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipping', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
        ('returned', 'Hoàn trả'),
    ], string='Mã', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    color = fields.Integer(string='Màu sắc', default=0)
