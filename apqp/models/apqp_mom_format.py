# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class APQPMomFormat(models.Model):
    _name = 'apqp.mom.format'
    _description = 'APQP MOM Format'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    # Sequence and basic fields
    sequence = fields.Integer(string='Sequence', default=10)
    serial_no = fields.Integer(string='Serial No.', copy=False, compute='_compute_serial_no', store=True)
    timeline_chart_id = fields.Many2one('apqp.timeline.chart', string='Timeline Chart', required=True, ondelete='cascade')
    
    # Main fields
    open_point_id = fields.Many2one('apqp.open.point', string='Open Point', required=True)
    responsibility_id = fields.Many2one('res.partner', string='Responsibility (Supplier)')
    target_date = fields.Date(string='Target Date', required=True)
    actual_completion_date = fields.Date(string='Actual Completion Date')
    
    # Status field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Additional fields
    remarks = fields.Text(string='Remarks')
    create_date = fields.Datetime(string='Created on Date', readonly=True)
    
    # Attendees and Champion
    attendee_ids = fields.Many2many('hr.employee', 'apqp_mom_attendee_rel', 'mom_id', 'employee_id', string='Attendees')
    conducted_by_id = fields.Many2one('hr.employee', string='Conducted By/Champion')
    
    # Approval fields
    approve_date = fields.Datetime(string='Approve Date', readonly=True)
    approved_by_id = fields.Many2one('res.users', string='Approved By', readonly=True)
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    
    # State History Tracking
    state_history = fields.Text(string='State History', readonly=True, copy=False)
    
    @api.depends('timeline_chart_id', 'sequence')
    def _compute_serial_no(self):
        """Compute serial number based on sequence order within the timeline chart."""
        for record in self:
            if record.timeline_chart_id:
                # Get all records for the same timeline chart, ordered by sequence and id
                all_records = self.search([('timeline_chart_id', '=', record.timeline_chart_id.id)], order='sequence, id')
                # Assign serial numbers based on the order
                for idx, rec in enumerate(all_records, 1):
                    if rec.serial_no != idx:
                        rec.serial_no = idx
    
    @api.model
    def create(self, vals):
        """Create MOM format, initialize state_history, and update serial numbers."""
        if 'serial_no' not in vals or not vals.get('serial_no'):
            if 'timeline_chart_id' in vals and vals['timeline_chart_id']:
                # Find the next sequence number
                existing_records = self.search([('timeline_chart_id', '=', vals['timeline_chart_id'])], order='sequence desc', limit=1)
                next_sequence = existing_records.sequence + 10 if existing_records else 10
                vals['sequence'] = next_sequence
                # Serial number will be computed later
            else:
                vals['sequence'] = 10
        
        # Initialize state_history
        if 'state_history' not in vals:
            vals['state_history'] = ''
        
        res = super(APQPMomFormat, self).create(vals)
        if res.timeline_chart_id:
            # Recompute serial numbers for all records in the timeline chart
            all_records = self.search([('timeline_chart_id', '=', res.timeline_chart_id.id)], order='sequence, id')
            all_records._compute_serial_no()
        # Update state history for the 'created' event
        res._update_state_history('created', res.state or 'draft')
        return res
    
    def unlink(self):
        """Delete MOM format and update remaining serial numbers."""
        timeline_chart_ids = self.mapped('timeline_chart_id.id')
        res = super(APQPMomFormat, self).unlink()
        for timeline_id in timeline_chart_ids:
            remaining_records = self.search([('timeline_chart_id', '=', timeline_id)], order='sequence, id')
            remaining_records._compute_serial_no()
        return res
    
    def write(self, vals):
        """Override write to handle sequence changes and update state history."""
        old_timeline_ids = {rec.id: rec.timeline_chart_id.id for rec in self if rec.timeline_chart_id}
        old_states = {rec.id: rec.state for rec in self}
        
        res = super(APQPMomFormat, self).write(vals)
        
        if 'state' in vals:
            for record in self:
                old_state = old_states.get(record.id)
                new_state = vals.get('state')
                if old_state != new_state:
                    record._update_state_history(old_state, new_state)
        
        # If timeline_chart_id or sequence is changed, update serial numbers
        if 'timeline_chart_id' in vals or 'sequence' in vals:
            timeline_ids = set()
            for record in self:
                if record.timeline_chart_id:
                    timeline_ids.add(record.timeline_chart_id.id)
            if 'timeline_chart_id' in vals:
                for old_timeline_id in set(old_timeline_ids.values()):
                    if old_timeline_id and old_timeline_id not in timeline_ids:
                        remaining_records = self.search([('timeline_chart_id', '=', old_timeline_id)], order='sequence, id')
                        remaining_records._compute_serial_no()
            for timeline_id in timeline_ids:
                all_records = self.search([('timeline_chart_id', '=', timeline_id)], order='sequence, id')
                all_records._compute_serial_no()
        
        return res
    
    def _update_state_history(self, old_state, new_state):
        """Update state history with plain text formatting and ensure each entry is on a new line."""
        for record in self:
            timestamp = fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user = self.env.user
            
            state_display = {
                'draft': 'Draft',
                'in_progress': 'In Progress',
                'completed': 'Completed',
                'approved': 'Approved',
                'cancelled': 'Cancelled',
                'created': 'Created'
            }
            
            old_state_name = state_display.get(old_state, old_state)
            new_state_name = state_display.get(new_state, new_state)
            
            if old_state == 'created':
                history_entry = f"{timestamp} - Record created in {new_state_name} state by {user.name}"
            else:
                history_entry = f"{timestamp} - State changed from {old_state_name} to {new_state_name} by {user.name}"
            
            # Append the new entry with a newline
            if record.state_history:
                record.state_history = record.state_history + "\n" + history_entry
            else:
                record.state_history = history_entry
    
    def action_approve(self):
        """Approve the MOM format record."""
        for record in self:
            if record.state != 'completed':
                raise UserError(_('You can only approve completed records.'))
            record.write({
                'state': 'approved',
                'approve_date': fields.Datetime.now(),
                'approved_by_id': self.env.user.id,
            })
        return True
    
    def action_complete(self):
        """Mark the MOM format as completed."""
        for record in self:
            if not record.actual_completion_date:
                raise UserError(_('Please set the actual completion date before marking as completed.'))
            record.state = 'completed'
        return True
    
    def action_cancel(self):
        """Cancel the MOM format record."""
        for record in self:
            if record.state == 'approved':
                raise UserError(_('You cannot cancel an approved record.'))
            record.state = 'cancelled'
        return True
    
    def action_reset_to_draft(self):
        """Reset the record to draft state."""
        for record in self:
            record.write({
                'state': 'draft',
                'approve_date': False,
                'approved_by_id': False,
            })
        return True
    
    def action_in_progress(self):
        """Mark the record as in progress."""
        for record in self:
            record.state = 'in_progress'
        return True


class APQPOpenPoint(models.Model):
    _name = 'apqp.open.point'
    _description = 'APQP Open Point'
    _order = 'name'
    
    name = fields.Char(string='Open Point', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The open point name must be unique!')
    ]