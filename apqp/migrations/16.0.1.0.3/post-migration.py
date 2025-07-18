# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """
    Post-migration script to add new fields to apqp.timeline.chart model.
    The fields attendee_ids and conducted_by_id are added for automatic MOM data transfer.
    """
    if not version:
        return
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Log migration start
    env['ir.logging'].create({
        'name': 'apqp.migration',
        'type': 'server',
        'level': 'info',
        'message': 'Starting migration: Adding attendee_ids and conducted_by_id fields to apqp.timeline.chart',
        'path': __file__,
        'line': 1,
        'func': 'migrate',
    })
    
    # The fields will be automatically created by Odoo ORM based on the model definition
    # No manual field creation needed
    
    # Log migration end
    env['ir.logging'].create({
        'name': 'apqp.migration',
        'type': 'server',
        'level': 'info',
        'message': 'Migration completed: Fields added successfully',
        'path': __file__,
        'line': 1,
        'func': 'migrate',
    })
