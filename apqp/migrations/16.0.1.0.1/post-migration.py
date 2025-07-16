# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """Remove NOT NULL constraint from serial_no field and fix state history formatting."""
    try:
        # Drop any NOT NULL constraint on serial_no
        cr.execute("""
            ALTER TABLE apqp_mom_format 
            ALTER COLUMN serial_no DROP NOT NULL
        """)
        
        # Update any NULL values to a default value
        cr.execute("""
            UPDATE apqp_mom_format 
            SET serial_no = 1 
            WHERE serial_no IS NULL
        """)
    except Exception as e:
        # If the constraint doesn't exist, just continue
        pass
    
    # Fix state history formatting
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['apqp.mom.format'].fix_state_history_formatting()
