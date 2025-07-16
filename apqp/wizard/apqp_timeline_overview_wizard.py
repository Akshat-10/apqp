# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class APQPTimelineOverviewWizard(models.TransientModel):
    _name = 'apqp.timeline.overview.wizard'
    _description = 'APQP Timeline Overview Wizard'
    
    timeline_chart_id = fields.Many2one('apqp.timeline.chart', string='Timeline Chart', required=True)
    timeline_html = fields.Html(string='Timeline Overview', compute='_compute_timeline_html', sanitize=False)
    
    @api.depends('timeline_chart_id')
    def _compute_timeline_html(self):
        for wizard in self:
            if wizard.timeline_chart_id:
                wizard.timeline_html = wizard.timeline_chart_id.timeline_html
            else:
                wizard.timeline_html = "<p>No timeline chart selected.</p>"
    
    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
