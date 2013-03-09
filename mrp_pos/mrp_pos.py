import time
from datetime import datetime

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools



class pos_order(osv.osv):
    """
    Extencion de orden de produccion en Pv
    """
    _name = 'pos.order'
    _inherit = 'pos.order'
    
    _description = 'Extencion de orden de produccion'
    
    def test(self, cr, uid, ids, context=None):
        pos_order = self.browse(cr, uid, ids, context=None)[0]                
        for line in pos_order.lines:
            
            bom_id = self.pool.get('mrp.bom')._bom_find(cr,uid,line.product_id.id,line.product_id.uom_id.id)
            if bom_id:   
                """mrp_obj=self.pool.get('mrp.production').create(cr, uid, {
                               'product_id':"3",                                                        
                               'bom_id':"1",
                               'product_uom':"1",
                               'product_qty':"1",
                               },context=None)"""                       
        return True
    
    def produces(self, cr, uid, order, context=None):    
        
        ids=order['id'] 
                 
        
        for line in order.lines:
            bom_id=self.pool.get('mrp.bom')._bom_find(cr,uid,line.product_id.id,line.product_id.uom_id.id)            
            if bom_id:
                if line.prod_qty < line.qty:                    
                    
                    mrp_obj=self.pool.get('mrp.production').create(cr, uid, {
                                   'product_id':line.product_id.id,                                                        
                                   'bom_id':bom_id,
                                   'product_uom':line.product_id.uom_id.id,
                                   'product_qty':(line.qty)-line.prod_qty
                                                                       },context=None)                   
                    #actuliza prod_qty y realiza picking
                    self.pool.get('pos.order.line').write(cr, uid, line.id, { 'prod_qty':line.qty}, context)                    
                    temp= self.pool.get('mrp.production').browse(cr,uid,mrp_obj)
                    print temp._id
                    self.pool.get('mrp.production').action_confirm(cr, uid, [temp.id], context)                    
                else:                    
                    if line.prod_qty > line.qty:
                        return false                                                                   
        return True    
    
    def update_lines(self, cr, uid, order_id, lines = None, context = None):        
        if lines !=None:
            #actulizacion            
            super(pos_order, self).update_lines(cr, uid, order_id[0], lines, context)
            orders=self.pool.get('pos.order').browse(cr, uid, order_id, context)[0]
            print 'Estado de producion',self.produces(cr, uid, orders, context=None)
        else:
            #creacion
            orders=self.pool.get('pos.order').browse(cr, uid, order_id, context)
            print 'Estado de producion',self.produces(cr, uid, orders, context=None)
        return True  
    
    def get_current_lines(self,order_lines):
    #calcula ordenes actuales        
        current_lines=[]
        for line1 in order_lines:
            d= {                            
                        'discount':line1.discount,
                        'price_unit':line1.price_unit,
                        'product_id':line1.product_id.id,
                        'qty':line1.qty,                        
                        'prod_qty':line1.qty,
                        'id':line1.id,                         
                    }
            current_lines.append(d)
        return current_lines
    
    

pos_order()
#********************************************************************cambio******************************************************** 
class pos_order_line(osv.osv):
    
    _name = 'pos.order.line'
    _inherit = 'pos.order.line'
    
    _columns = {
                'prod_qty': fields.integer('Bquantity', digits=(16, 2)),                
                }
    _defaults = {
                 'prod_qty': lambda *a: 0,                 
                 }                
pos_order_line()
