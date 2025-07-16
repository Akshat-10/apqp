# -*- coding: utf-8 -*-
import re
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """Clean up HTML tags from existing state_history records."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Get all MOM format records with state_history
    mom_records = env['apqp.mom.format'].search([('state_history', '!=', False)])
    
    for record in mom_records:
        if record.state_history:
            # Remove all HTML tags
            clean_text = re.sub(r'<[^>]+>', '', record.state_history)
            # Remove extra whitespace
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            # Replace multiple spaces with single space
            clean_text = ' '.join(clean_text.split())
            
            # Update the record
            record.with_context(skip_update=True).write({
                'state_history': clean_text
            })
