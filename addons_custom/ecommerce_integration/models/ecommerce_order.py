# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class EcommerceOrder(models.Model):
    _name = 'ecommerce.order'
    _description = 'E-commerce Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'order_date desc, id desc'

    # Basic Information
    name = fields.Char(string='Số đơn hàng', required=True, copy=False, index=True)
    order_id = fields.Char(string='Order ID (Platform)', required=True, index=True,
                           help='Mã đơn hàng trên sàn TMĐT')
    shop_id = fields.Many2one('ecommerce.shop', string='Gian hàng', required=True, 
                              ondelete='cascade', index=True)
    platform_id = fields.Many2one('ecommerce.platform', string='Sàn TMĐT', 
                                  related='shop_id.platform_id', store=True)
    
    # Order Details
    order_date = fields.Datetime(string='Ngày đặt hàng', required=True, 
                                 tracking=True, default=fields.Datetime.now)
    customer_name = fields.Char(string='Tên khách hàng', required=True)
    customer_phone = fields.Char(string='Số điện thoại')
    customer_email = fields.Char(string='Email')
    shipping_address = fields.Text(string='Địa chỉ giao hàng')
    
    # Order Status
    status = fields.Selection([
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipping', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
        ('returned', 'Hoàn trả'),
    ], string='Trạng thái', default='pending', required=True, tracking=True)
    
    payment_status = fields.Selection([
        ('unpaid', 'Chưa thanh toán'),
        ('partial', 'Thanh toán 1 phần'),
        ('paid', 'Đã thanh toán'),
        ('refunded', 'Đã hoàn tiền'),
    ], string='Trạng thái thanh toán', default='unpaid', tracking=True)
    
    payment_method = fields.Char(string='Phương thức thanh toán')
    shipping_method = fields.Char(string='Phương thức vận chuyển')
    
    # Order Lines
    order_line_ids = fields.One2many('ecommerce.order.line', 'order_id', 
                                     string='Chi tiết đơn hàng')
    
    # Financial Information
    currency_id = fields.Many2one('res.currency', string='Đơn vị tiền tệ',
                                  default=lambda self: self.env.company.currency_id)
    subtotal = fields.Monetary(string='Tổng tiền hàng', currency_field='currency_id',
                               compute='_compute_amounts', store=True)
    shipping_fee = fields.Monetary(string='Phí vận chuyển', currency_field='currency_id',
                                   default=0.0)
    discount_amount = fields.Monetary(string='Giảm giá', currency_field='currency_id',
                                      default=0.0)
    total_amount = fields.Monetary(string='Tổng thanh toán', currency_field='currency_id',
                                   compute='_compute_amounts', store=True, tracking=True)
    
    # Odoo Integration
    odoo_sale_order_id = fields.Many2one('sale.order', string='Đơn hàng Odoo',
                                         readonly=True, copy=False)
    is_synced = fields.Boolean(string='Đã đồng bộ Odoo', default=False, 
                               tracking=True, copy=False)
    sync_date = fields.Datetime(string='Ngày đồng bộ', readonly=True, copy=False)
    
    # Additional Information
    note = fields.Text(string='Ghi chú')
    tracking_number = fields.Char(string='Mã vận đơn')
    
    # Constraints
    _sql_constraints = [
        ('order_id_shop_unique', 'unique(order_id, shop_id)',
         'Mã đơn hàng đã tồn tại cho gian hàng này!')
    ]

    @api.depends('order_line_ids.subtotal', 'shipping_fee', 'discount_amount')
    def _compute_amounts(self):
        """Compute order amounts"""
        for order in self:
            order.subtotal = sum(line.subtotal for line in order.order_line_ids)
            order.total_amount = order.subtotal + order.shipping_fee - order.discount_amount

    def action_sync_to_odoo(self):
        """Sync order to Odoo Sale Order"""
        self.ensure_one()
        
        if self.is_synced and self.odoo_sale_order_id:
            raise UserError('Đơn hàng này đã được đồng bộ vào Odoo!')
        
        # Create partner if not exists
        partner = self._find_or_create_partner()
        
        # Create sale order
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'date_order': self.order_date,
            'origin': f'{self.platform_id.name} - {self.name}',
            'note': self.note or '',
            'order_line': [(0, 0, {
                'product_id': line.odoo_product_id.id if line.odoo_product_id else self._get_default_product().id,
                'name': line.product_name,
                'product_uom_qty': line.quantity,
                'price_unit': line.unit_price,
            }) for line in self.order_line_ids],
        })
        
        self.write({
            'odoo_sale_order_id': sale_order.id,
            'is_synced': True,
            'sync_date': fields.Datetime.now(),
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đơn hàng Odoo',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _find_or_create_partner(self):
        """Find or create customer partner"""
        self.ensure_one()
        
        # Search by phone or email
        partner = False
        if self.customer_phone:
            partner = self.env['res.partner'].search([
                ('phone', '=', self.customer_phone)
            ], limit=1)
        
        if not partner and self.customer_email:
            partner = self.env['res.partner'].search([
                ('email', '=', self.customer_email)
            ], limit=1)
        
        # Create new partner if not found
        if not partner:
            partner = self.env['res.partner'].create({
                'name': self.customer_name,
                'phone': self.customer_phone,
                'email': self.customer_email,
                'street': self.shipping_address,
            })
        
        return partner

    def _get_default_product(self):
        """Get default product for order lines without product mapping"""
        product = self.env['product.product'].search([
            ('default_code', '=', 'ECOM-DEFAULT')
        ], limit=1)
        
        if not product:
            # Create product template first
            template = self.env['product.template'].create({
                'name': 'Sản phẩm sàn TMĐT',
                'default_code': 'ECOM-DEFAULT',
                'type': 'consu',  # consumable type
                'list_price': 0.0,
                'purchase_ok': False,
                'sale_ok': True,
            })
            product = template.product_variant_ids[0]
        
        return product

    def action_open_odoo_order(self):
        """Open linked Odoo sale order"""
        self.ensure_one()
        
        if not self.odoo_sale_order_id:
            raise UserError('Đơn hàng chưa được đồng bộ vào Odoo!')
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đơn hàng Odoo',
            'res_model': 'sale.order',
            'res_id': self.odoo_sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class EcommerceOrderLine(models.Model):
    _name = 'ecommerce.order.line'
    _description = 'E-commerce Order Line'
    _order = 'order_id, sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    order_id = fields.Many2one('ecommerce.order', string='Đơn hàng', 
                               required=True, ondelete='cascade', index=True)
    
    # Product Information
    product_name = fields.Char(string='Tên sản phẩm', required=True)
    product_sku = fields.Char(string='SKU')
    ecommerce_product_id = fields.Many2one('ecommerce.product', string='Sản phẩm sàn')
    odoo_product_id = fields.Many2one('product.product', string='Sản phẩm Odoo')
    
    # Quantity & Price
    quantity = fields.Float(string='Số lượng', required=True, default=1.0)
    unit_price = fields.Monetary(string='Đơn giá', required=True, 
                                 currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', 
                                  string='Đơn vị tiền tệ')
    subtotal = fields.Monetary(string='Thành tiền', compute='_compute_subtotal', 
                               store=True, currency_field='currency_id')
    
    # Additional Info
    variant_name = fields.Char(string='Phân loại')
    note = fields.Char(string='Ghi chú')

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        """Compute line subtotal"""
        for line in self:
            line.subtotal = line.quantity * line.unit_price
