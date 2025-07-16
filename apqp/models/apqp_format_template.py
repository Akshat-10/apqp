# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class APQPFormatTemplate(models.Model):
    _name = 'apqp.format.template'
    _description = 'APQP Format Template'
    _order = 'sequence, id'
    _rec_name = 'format_name'

    sequence = fields.Integer(string='Sequence', default=15)
    format_name = fields.Char(string='Format Name', required=True)
    phase_id = fields.Many2one('apqp.phase', string='Phase', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('format_phase_uniq', 'unique (format_name, phase_id)', 'The combination of format name and phase must be unique!')
    ]
