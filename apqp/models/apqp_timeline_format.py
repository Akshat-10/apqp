# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class APQPTimelineFormat(models.Model):
    _name = 'apqp.timeline.format'
    _description = 'APQP Timeline Format'
    _order = 'sequence, id'

    timeline_chart_id = fields.Many2one('apqp.timeline.chart', string='Timeline Chart', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Format Information
    name = fields.Char(string='Format Name', required=True)
    format_id = fields.Many2one('document.formate', string='Document Format')
    document_approval_id = fields.Many2one('document.approval', string='Document Approval')
    
    # Phase Information
    phase_id = fields.Many2one('apqp.phase', string='Phase')
    
    # Date Fields
    planned_start_date = fields.Date(string='Planned Start Date')
    planned_end_date = fields.Date(string='Planned End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    
    # Status and Progress
    status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed')
    ], string='Status', default='not_started', compute='_compute_status', store=True)
    
    # Display Type for Sections and Notes
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note')
    ], string='Display Type', help='Technical field for UX purpose.')
    
    # Computed field to show phase name in section lines
    section_name = fields.Char(string='Section Name', compute='_compute_section_name', store=True)
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    attachment_count = fields.Integer(string='Attachment Count', compute='_compute_attachment_count')
    
    # Additional Fields
    reference = fields.Char(string='Reference')
    notes = fields.Text(string='Notes')
    responsible_user_id = fields.Many2one('res.users', string='Responsible User')
    source_attachment_id = fields.Many2one('apqp.timeline.attachment', string='Source Attachment', help='If this format was created from an attachment')
    
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)
    
    @api.depends('phase_id', 'display_type')
    def _compute_section_name(self):
        for record in self:
            if record.display_type == 'line_section' and record.phase_id:
                record.section_name = record.phase_id.name
            else:
                record.section_name = False
    
    @api.depends('actual_start_date', 'actual_end_date', 'planned_end_date')
    def _compute_status(self):
        today = fields.Date.today()
        for record in self:
            if record.display_type:
                record.status = False  # Sections and notes don't have status
            elif record.actual_end_date:
                record.status = 'completed'
            elif record.actual_start_date:
                if record.planned_end_date and today > record.planned_end_date:
                    record.status = 'delayed'
                else:
                    record.status = 'in_progress'
            else:
                record.status = 'not_started'
    
    @api.onchange('format_id')
    def _onchange_format_id(self):
        if self.format_id:
            self.name = self.format_id.name
    
    def action_view_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.attachment_ids.ids)],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }
    
    def action_add_attachment(self):
        self.ensure_one()
        return {
            'name': _('Add Attachment'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }
    
    @api.model
    def create(self, vals):
        """Override create to ensure phase_id is set for sections."""
        # If creating a section and phase_id is provided, ensure the name is set
        if vals.get('display_type') == 'line_section' and vals.get('phase_id'):
            phase = self.env['apqp.phase'].browse(vals['phase_id'])
            if phase and not vals.get('name'):
                vals['name'] = phase.name
        return super(APQPTimelineFormat, self).create(vals)
    
    def write(self, vals):
        """Override write to sync phase changes back to source attachment and handle sequencing."""
        # Handle sequence changes to automatically update phase_id
        if 'sequence' in vals and not 'phase_id' in vals:
            for record in self:
                if not record.display_type:  # Only for regular lines, not sections
                    # Find the nearest phase section above this sequence
                    phase_section = self.search([
                        ('timeline_chart_id', '=', record.timeline_chart_id.id),
                        ('display_type', '=', 'line_section'),
                        ('sequence', '<=', vals.get('sequence', record.sequence))
                    ], order='sequence desc', limit=1)
                    
                    if phase_section and phase_section.phase_id != record.phase_id:
                        vals['phase_id'] = phase_section.phase_id.id
        
        # Update section name if phase_id changes
        if 'phase_id' in vals and self.filtered(lambda r: r.display_type == 'line_section'):
            phase = self.env['apqp.phase'].browse(vals['phase_id'])
            if phase:
                vals['name'] = phase.name
        
        res = super(APQPTimelineFormat, self).write(vals)
        
        # If phase_id changed and this format has a source attachment, update it
        if 'phase_id' in vals:
            for record in self:
                if record.source_attachment_id and not record.display_type:
                    # Update the source attachment's phase
                    record.source_attachment_id.with_context(skip_sync=True).write({
                        'phase_id': record.phase_id.id
                    })
        
        # Sync sequence changes back to source attachment
        if 'sequence' in vals and not self.env.context.get('from_attachment_sync'):
            for record in self:
                if record.source_attachment_id and not record.display_type:
                    # Calculate relative sequence within the phase
                    phase_section = self.search([
                        ('timeline_chart_id', '=', record.timeline_chart_id.id),
                        ('phase_id', '=', record.phase_id.id),
                        ('display_type', '=', 'line_section')
                    ], limit=1)
                    relative_sequence = record.sequence - (phase_section.sequence if phase_section else 0)
                    record.source_attachment_id.with_context(skip_sync=True).write({
                        'sequence': relative_sequence
                    })
        
        # Sync changes from source attachment
        if any(field in vals for field in ['planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'reference']):
            for record in self:
                if record.source_attachment_id and not self.env.context.get('from_attachment_sync'):
                    sync_vals = {}
                    for field in ['planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'reference']:
                        if field in vals:
                            sync_vals[field] = vals[field]
                    if sync_vals:
                        record.source_attachment_id.with_context(skip_sync=True).write(sync_vals)
        
        return res
