# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import random


class EcommerceStockUpdateWizard(models.TransientModel):
    _name = 'ecommerce.stock.update.wizard'
    _description = 'E-commerce Stock Update Wizard'

    shop_id = fields.Many2one('ecommerce.shop', string='Gian hàng', required=True)
    platform_id = fields.Many2one('ecommerce.platform', related='shop_id.platform_id',
                                  string='Sàn TMĐT', readonly=True)
    
    # Update results
    update_line_ids = fields.One2many('ecommerce.stock.update.line', 'wizard_id',
                                      string='Chi tiết cập nhật')
    
    total_count = fields.Integer(string='Tổng số', compute='_compute_counts', store=True)
    success_count = fields.Integer(string='Thành công', compute='_compute_counts', store=True)
    failed_count = fields.Integer(string='Thất bại', compute='_compute_counts', store=True)
    
    state = fields.Selection([
        ('draft', 'Chưa cập nhật'),
        ('done', 'Đã cập nhật'),
    ], string='Trạng thái', default='draft')

    @api.depends('update_line_ids.status')
    def _compute_counts(self):
        """Compute statistics"""
        for wizard in self:
            wizard.total_count = len(wizard.update_line_ids)
            wizard.success_count = len(wizard.update_line_ids.filtered(lambda l: l.status == 'success'))
            wizard.failed_count = len(wizard.update_line_ids.filtered(lambda l: l.status == 'failed'))

    def action_update_stock(self):
        """Update stock to platform"""
        self.ensure_one()
        
        if not self.shop_id:
            raise UserError('Vui lòng chọn gian hàng!')
        
        # Get all products from this shop
        products = self.env['ecommerce.product'].search([
            ('shop_id', '=', self.shop_id.id),
            ('status', '=', 'active'),
        ])
        
        if not products:
            raise UserError('Không có sản phẩm nào để cập nhật tồn kho!')
        
        # Create update lines
        update_lines = []
        for product in products:
            # Simulate API call to update stock (demo implementation)
            success = random.choice([True, True, True, False])  # 75% success rate
            
            if success:
                status = 'success'
                message = 'Cập nhật thành công'
                new_stock = product.stock_quantity
            else:
                status = 'failed'
                message = random.choice([
                    'Lỗi kết nối API',
                    'Sản phẩm không tồn tại trên sàn',
                    'Không có quyền cập nhật',
                    'Timeout kết nối',
                ])
                new_stock = 0
            
            update_lines.append((0, 0, {
                'wizard_id': self.id,
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'old_stock': product.stock_quantity,
                'new_stock': new_stock,
                'status': status,
                'message': message,
            }))
        
        self.write({
            'update_line_ids': update_lines,
            'state': 'done',
        })
        
        # Return action to show results
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cập nhật tồn kho',
            'res_model': 'ecommerce.stock.update.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }


class EcommerceStockUpdateLine(models.TransientModel):
    _name = 'ecommerce.stock.update.line'
    _description = 'E-commerce Stock Update Line'
    _order = 'status desc, product_name'

    wizard_id = fields.Many2one('ecommerce.stock.update.wizard', string='Wizard',
                                required=True, ondelete='cascade')
    
    product_id = fields.Many2one('ecommerce.product', string='Sản phẩm sàn')
    product_name = fields.Char(string='Tên sản phẩm', required=True)
    sku = fields.Char(string='SKU/Mã sản phẩm')
    
    old_stock = fields.Integer(string='Kho hiện tại')
    new_stock = fields.Integer(string='Kho mới')
    
    status = fields.Selection([
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
    ], string='Trạng thái', default='success')
    
    message = fields.Text(string='Thông báo')
    
    # Display fields
    platform_product_id = fields.Char(string='Mã sản phẩm', related='product_id.product_id')
    price = fields.Float(string='Giá bán', related='product_id.price')
    currency_id = fields.Many2one('res.currency', related='product_id.currency_id')
