# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class APQPPhase(models.Model):
    _name = 'apqp.phase'
    _description = 'APQP Phase'
    _order = 'sequence, id'

    name = fields.Char(string='Phase Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(string='Active', default=True)

    @api.depends('name')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            res.append((record.id, name))
        return res
