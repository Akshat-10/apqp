# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class APQPTimelineAttachment(models.Model):
    _name = 'apqp.timeline.attachment'
    _description = 'APQP Timeline Attachment'
    _order = 'sequence, id'

    # Core relational fields
    timeline_chart_id = fields.Many2one('apqp.timeline.chart', string='Timeline Chart', ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10, help='Defines the order of this attachment in the timeline.')
    
    # Attachment-specific information
    name = fields.Char(string='Description', help='A brief description of the attachment.')
    phase_id = fields.Many2one('apqp.phase', string='Phase', required=True, help='The phase this attachment belongs to.')
    format_name = fields.Char(string='Format Name', required=True, help='Name of the format this attachment represents.')
    
    # Date fields for planning and tracking
    planned_start_date = fields.Date(string='Planned Start Date')
    planned_end_date = fields.Date(string='Planned End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    
    # Attachment management
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', help='Files attached to this timeline entry.')
    attachment_count = fields.Integer(string='Attachment Count', compute='_compute_attachment_count', help='Number of attached files.')
    
    # Additional metadata
    reference = fields.Char(string='Reference', help='A reference code or identifier.')
    notes = fields.Text(string='Notes', help='Additional notes or comments.')
    state = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed')
    ], string='Status', default='not_started', compute='_compute_state', store=True, help='Current status of the attachment.')
    
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        """Calculate the number of attachments linked to this record."""
        for record in self:
            record.attachment_count = len(record.attachment_ids)
    
    @api.depends('actual_start_date', 'actual_end_date', 'planned_end_date')
    def _compute_state(self):
        """Compute the status based on date fields."""
        today = fields.Date.today()
        for record in self:
            if record.actual_end_date:
                record.state = 'completed'
            elif record.actual_start_date:
                if record.planned_end_date and today > record.planned_end_date:
                    record.state = 'delayed'
                else:
                    record.state = 'in_progress'
            else:
                record.state = 'not_started'
    
    @api.model
    def create(self, vals):
        """Create an attachment and sync it to the timeline format."""
        attachment = super(APQPTimelineAttachment, self).create(vals)
        attachment._sync_to_timeline_format()
        return attachment
    
    def _sync_to_timeline_format(self):
        """Synchronize attachment data to a timeline format record with proper sequencing."""
        for attachment in self:
            if not (attachment.timeline_chart_id and attachment.phase_id and attachment.format_name):
                continue  # Skip if required fields are missing

            # First ensure all phase sections exist with proper sequence
            all_phases = self.env['apqp.phase'].search([], order='sequence')
            for phase in all_phases:
                existing_section = self.env['apqp.timeline.format'].search([
                    ('timeline_chart_id', '=', attachment.timeline_chart_id.id),
                    ('phase_id', '=', phase.id),
                    ('display_type', '=', 'line_section')
                ], limit=1)
                
                if not existing_section:
                    # Create phase section with sequence based on phase sequence
                    self.env['apqp.timeline.format'].with_context(from_attachment_sync=True).create({
                        'timeline_chart_id': attachment.timeline_chart_id.id,
                        'phase_id': phase.id,
                        'display_type': 'line_section',
                        'name': phase.name,
                        'sequence': phase.sequence * 1000,  # Multiply by 1000 to leave room for format lines
                    })

            # Now find the phase section for this attachment
            phase_section = self.env['apqp.timeline.format'].search([
                ('timeline_chart_id', '=', attachment.timeline_chart_id.id),
                ('phase_id', '=', attachment.phase_id.id),
                ('display_type', '=', 'line_section')
            ], limit=1)
            
            # Update the section name if it doesn't match the phase name
            if phase_section and phase_section.name != attachment.phase_id.name:
                phase_section.with_context(from_attachment_sync=True).write({'name': attachment.phase_id.name})
            
            # Look for an existing timeline format linked to this attachment
            existing_format = self.env['apqp.timeline.format'].search([
                ('timeline_chart_id', '=', attachment.timeline_chart_id.id),
                ('phase_id', '=', attachment.phase_id.id),
                ('name', '=', attachment.format_name),
                ('display_type', '=', False),
                ('source_attachment_id', '=', attachment.id)
            ], limit=1)
            
            # Calculate sequence for format line within the phase
            phase_base_sequence = attachment.phase_id.sequence * 1000
            # Get the next available sequence within this phase
            max_format_sequence = self.env['apqp.timeline.format'].search([
                ('timeline_chart_id', '=', attachment.timeline_chart_id.id),
                ('phase_id', '=', attachment.phase_id.id),
                ('display_type', '=', False),
                ('sequence', '>', phase_base_sequence),
                ('sequence', '<', phase_base_sequence + 1000)
            ], order='sequence desc', limit=1).sequence or phase_base_sequence
            
            next_sequence = max_format_sequence + 10
            
            # Values to sync to the timeline format
            format_vals = {
                'timeline_chart_id': attachment.timeline_chart_id.id,
                'phase_id': attachment.phase_id.id,
                'name': attachment.format_name,
                'planned_start_date': attachment.planned_start_date,
                'planned_end_date': attachment.planned_end_date,
                'actual_start_date': attachment.actual_start_date,
                'actual_end_date': attachment.actual_end_date,
                'reference': attachment.reference,
                'source_attachment_id': attachment.id,
            }
            
            if not existing_format:
                # Create a new timeline format if none exists
                format_vals['sequence'] = attachment.sequence + (phase_section.sequence if phase_section else 0)
                self.env['apqp.timeline.format'].with_context(from_attachment_sync=True).create(format_vals)
            else:
                # Update the existing format, but preserve its sequence
                existing_format.with_context(from_attachment_sync=True).write(format_vals)
    
    def write(self, vals):
        """Update the attachment and sync changes to the timeline format."""
        if self.env.context.get('skip_sync'):
            return super(APQPTimelineAttachment, self).write(vals)
        
        old_values = {}
        if 'phase_id' in vals or 'format_name' in vals:
            for attachment in self:
                old_values[attachment.id] = {
                    'phase_id': attachment.phase_id.id,
                    'format_name': attachment.format_name,
                }
        
        res = super(APQPTimelineAttachment, self).write(vals)
        
        for attachment in self:
            if attachment.id in old_values:
                old_phase_id = old_values[attachment.id]['phase_id']
                old_format_name = old_values[attachment.id]['format_name']
                
                # Remove old format if phase or format name changed
                if (old_phase_id != attachment.phase_id.id or 
                    old_format_name != attachment.format_name):
                    old_format = self.env['apqp.timeline.format'].search([
                        ('timeline_chart_id', '=', attachment.timeline_chart_id.id),
                        ('phase_id', '=', old_phase_id),
                        ('name', '=', old_format_name),
                        ('display_type', '=', False),
                        ('source_attachment_id', '=', attachment.id)
                    ], limit=1)
                    if old_format:
                        old_format.unlink()
            
            # Sync updated data to timeline format
            attachment._sync_to_timeline_format()
        
        return res
    
    def action_view_attachments(self):
        """Open the attachments window."""
        self.ensure_one()
        action = {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.attachment_ids.ids)],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }
        return action
    
    def unlink(self):
        """Delete the attachment and its corresponding timeline format if applicable."""
        formats_to_delete = self.env['apqp.timeline.format']
        
        for attachment in self:
            if attachment.timeline_chart_id and attachment.phase_id and attachment.format_name:
                timeline_format = self.env['apqp.timeline.format'].search([
                    ('timeline_chart_id', '=', attachment.timeline_chart_id.id),
                    ('phase_id', '=', attachment.phase_id.id),
                    ('name', '=', attachment.format_name),
                    ('display_type', '=', False),
                    ('source_attachment_id', '=', attachment.id)
                ], limit=1)
                # Only delete if no other attachments share this format
                if timeline_format and not self.search([
                    ('timeline_chart_id', '=', attachment.timeline_chart_id.id),
                    ('phase_id', '=', attachment.phase_id.id),
                    ('format_name', '=', attachment.format_name),
                    ('id', '!=', attachment.id)
                ]):
                    formats_to_delete |= timeline_format
        
        res = super(APQPTimelineAttachment, self).unlink()
        if formats_to_delete:
            formats_to_delete.unlink()
        
        return res