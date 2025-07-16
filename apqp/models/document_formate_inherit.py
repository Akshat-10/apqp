# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DocumentFormateInherit(models.Model):
    _inherit = 'document.formate'

    phase_id = fields.Many2one('apqp.phase', string='Phase')