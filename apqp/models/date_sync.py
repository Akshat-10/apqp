from odoo import api, models

class DocumentApprovalSync(models.Model):
    _inherit = 'document.approval'

    def write(self, vals):
        # Skip synchronization if triggered by another model
        if self.env.context.get('from_timeline_format') or self.env.context.get('from_format_record'):
            return super(DocumentApprovalSync, self).write(vals)
        
        # Perform the write operation
        res = super(DocumentApprovalSync, self).write(vals)
        
        # Check if date fields are being updated
        date_fields = ['plan_start_date', 'plan_end_date', 'actual_start_date', 'actual_end_date']
        if any(field in vals for field in date_fields):
            for rec in self:
                # Update the format record (e.g., iatf.sign.off.members)
                if rec.formate_id and rec.formate.table:
                    try:
                        format_record = self.env[rec.formate.table].browse(int(rec.formate_id))
                        if format_record.exists():
                            format_record.with_context(from_document_approval=True).write({
                                'plan_start_date': rec.plan_start_date,
                                'plan_end_date': rec.plan_end_date,
                                'actual_start_date': rec.actual_start_date,
                                'actual_end_date': rec.actual_end_date,
                            })
                    except ValueError:
                        # Handle case where formate_id is not a valid integer
                        pass

                # Update related apqp.timeline.format records
                timeline_formats = self.env['apqp.timeline.format'].search([('document_approval_id', '=', rec.id)])
                for timeline_format in timeline_formats:
                    timeline_format.with_context(from_document_approval=True).write({
                        'planned_start_date': rec.plan_start_date,
                        'planned_end_date': rec.plan_end_date,
                        'actual_start_date': rec.actual_start_date,
                        'actual_end_date': rec.actual_end_date,
                    })
        return res

class APQPTimelineFormatSync(models.Model):
    _inherit = 'apqp.timeline.format'

    @api.model
    def create(self, vals):
        # If document_approval_id is provided, fetch dates from it
        if 'document_approval_id' in vals and vals.get('document_approval_id'):
            approval = self.env['document.approval'].browse(vals['document_approval_id'])
            if approval.exists():
                # Set dates from document.approval if not already provided in vals
                vals.setdefault('planned_start_date', approval.plan_start_date)
                vals.setdefault('planned_end_date', approval.plan_end_date)
                vals.setdefault('actual_start_date', approval.actual_start_date)
                vals.setdefault('actual_end_date', approval.actual_end_date)
        
        # Call the parent create method
        record = super(APQPTimelineFormatSync, self).create(vals)
        return record

    def write(self, vals):
        # Skip synchronization if triggered by another model
        if self.env.context.get('from_document_approval') or self.env.context.get('from_format_record'):
            return super(APQPTimelineFormatSync, self).write(vals)
        
        # Perform the write operation
        res = super(APQPTimelineFormatSync, self).write(vals)
        
        # Check if date fields are being updated
        date_fields = ['planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date']
        if any(field in vals for field in date_fields):
            for rec in self:
                # Update the related document.approval
                if rec.document_approval_id:
                    rec.document_approval_id.with_context(from_timeline_format=True).write({
                        'plan_start_date': rec.planned_start_date,
                        'plan_end_date': rec.planned_end_date,
                        'actual_start_date': rec.actual_start_date,
                        'actual_end_date': rec.actual_end_date,
                    })
                    
                    # Update the format record via document.approval
                    if rec.document_approval_id.formate_id and rec.document_approval_id.formate.table:
                        try:
                            format_record = self.env[rec.document_approval_id.formate.table].browse(
                                int(rec.document_approval_id.formate_id)
                            )
                            if format_record.exists():
                                format_record.with_context(from_timeline_format=True).write({
                                    'plan_start_date': rec.planned_start_date,
                                    'plan_end_date': rec.planned_end_date,
                                    'actual_start_date': rec.actual_start_date,
                                    'actual_end_date': rec.actual_end_date,
                                })
                        except ValueError:
                            # Handle case where formate_id is not a valid integer
                            pass
        return res

class IATFSignOffMembers(models.AbstractModel):
    _inherit = 'iatf.sign.off.members'

    def write(self, vals):
        # Skip synchronization if triggered by another model
        if self.env.context.get('from_document_approval') or self.env.context.get('from_timeline_format'):
            return super(IATFSignOffMembers, self).write(vals)
        
        # Perform the write operation
        res = super(IATFSignOffMembers, self).write(vals)
        
        # Check if date fields are being updated
        date_fields = ['plan_start_date', 'plan_end_date', 'actual_start_date', 'actual_end_date']
        if any(field in vals for field in date_fields):
            for rec in self:
                # Find related document.approval records
                approvals = self.env['document.approval'].search([
                    ('formate_id', '=', str(rec.id)),
                    ('formate.table', '=', rec._name)
                ])
                for approval in approvals:
                    # Update document.approval
                    approval.with_context(from_format_record=True).write({
                        'plan_start_date': rec.plan_start_date,
                        'plan_end_date': rec.plan_end_date,
                        'actual_start_date': rec.actual_start_date,
                        'actual_end_date': rec.actual_end_date,
                    })
                    
                    # Update related apqp.timeline.format records
                    timeline_formats = self.env['apqp.timeline.format'].search([('document_approval_id', '=', approval.id)])
                    for timeline_format in timeline_formats:
                        timeline_format.with_context(from_format_record=True).write({
                            'planned_start_date': rec.plan_start_date,
                            'planned_end_date': rec.plan_end_date,
                            'actual_start_date': rec.actual_start_date,
                            'actual_end_date': rec.actual_end_date,
                        })
        return res