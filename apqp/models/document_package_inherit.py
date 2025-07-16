# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DocumentPackageInherit(models.Model):
    _inherit = 'xf.doc.approval.document.package'

    apqp_timeline_chart_id = fields.Many2one('apqp.timeline.chart', string='APQP Timeline Chart', readonly=True, copy=False)

    def create_apqp_timeline_chart(self):
        for record in self:
            if not record.apqp_timeline_chart_id:
                apqp_timeline_chart = self.env['apqp.timeline.chart'].create({
                    'document_package_id': record.id,
                    'partner_id': record.partner_id.id,
                    'used_in_project_type_id': record.used_in_project_type_id.id,
                })
                record.apqp_timeline_chart_id = apqp_timeline_chart.id
                # Populate attachments from templates
                apqp_timeline_chart.populate_attachments_from_templates()
                record._create_timeline_formats()
    
    def _create_timeline_formats(self):
        for record in self:
            if not (record.apqp_timeline_chart_id and record.document_approval_ids):
                continue
            timeline_chart = record.apqp_timeline_chart_id
            timeline_chart.timeline_format_ids.unlink()
            
            all_phases = self.env['apqp.phase'].search([], order='sequence')
            for phase in all_phases:
                self.env['apqp.timeline.format'].create({
                    'timeline_chart_id': timeline_chart.id,
                    'name': phase.name,
                    'display_type': 'line_section',
                    'phase_id': phase.id,
                    'sequence': phase.sequence * 1000,
                })
            
            phases_with_approvals = record.document_approval_ids.mapped('phase_id').sorted('sequence')
            no_phase_approvals = record.document_approval_ids.filtered(lambda x: not x.phase_id)
            
            for phase in phases_with_approvals:
                phase_base_sequence = phase.sequence * 1000
                sequence_within_phase = 10
                phase_approvals = record.document_approval_ids.filtered(lambda x: x.phase_id == phase)
                for approval in phase_approvals.sorted('sr_no'):
                    if approval.formate:
                        self.env['apqp.timeline.format'].create({
                            'timeline_chart_id': timeline_chart.id,
                            'name': approval.formate.name,
                            'format_id': approval.formate.id,
                            'document_approval_id': approval.id,
                            'phase_id': phase.id,
                            'sequence': phase_base_sequence + sequence_within_phase,
                            'planned_start_date': approval.plan_start_date,
                            'planned_end_date': approval.plan_end_date,
                            'actual_start_date': approval.actual_start_date,
                            'actual_end_date': approval.actual_end_date,
                        })
                        sequence_within_phase += 10

            if no_phase_approvals:
                max_phase = all_phases[-1] if all_phases else None
                no_phase_sequence = (max_phase.sequence + 1) * 1000 if max_phase else 999000
                self.env['apqp.timeline.format'].create({
                    'timeline_chart_id': timeline_chart.id,
                    'name': 'No Phase Assigned',
                    'display_type': 'line_section',
                    'sequence': no_phase_sequence,
                })
                sequence_within_no_phase = 10
                for approval in no_phase_approvals.sorted('sr_no'):
                    if approval.formate:
                        self.env['apqp.timeline.format'].create({
                            'timeline_chart_id': timeline_chart.id,
                            'name': approval.formate.name,
                            'format_id': approval.formate.id,
                            'document_approval_id': approval.id,
                            'sequence': no_phase_sequence + sequence_within_no_phase,
                            'planned_start_date': approval.plan_start_date,
                            'planned_end_date': approval.plan_end_date,
                            'actual_start_date': approval.actual_start_date,
                            'actual_end_date': approval.actual_end_date,
                        })
                        sequence_within_no_phase += 10

    def action_open_apqp_timeline_chart(self):
        """Open the form view of the linked APQP Timeline Chart."""
        self.ensure_one()
        if not self.apqp_timeline_chart_id:
            raise UserError(_("No APQP Timeline Chart is linked to this document package."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'apqp.timeline.chart',
            'view_mode': 'form',
            'res_id': self.apqp_timeline_chart_id.id,
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        record = super(DocumentPackageInherit, self).create(vals)
        record.create_apqp_timeline_chart()
        return record

    def select_all_formate(self):
        department_lst = []
        formate_ids = self.env['document.formate'].search([]).filtered(
            lambda f: self.used_in_project_type_id.id in f.used_in_project_type_ids.ids
        )
        for formate in formate_ids:
            for department in formate.department_ids:
                manager = department.filtered(lambda l: not l.manager_id or not l.manager_id.work_email)
                if manager and department.name not in department_lst:
                    department_lst.append(department.name)

        if department_lst:
            raise UserError(_('Please configure Department Manager and their Email IDs in following departments:\n\n  %s') % ', '.join(department_lst))
        self.is_select_all = True
        for rec in formate_ids:
            manager_ids = rec.department_ids.mapped('manager_id').ids
            vals = {
                'serial_no': rec.serial_no,
                'sr_no': rec.sr_no,
                'control_emp_ids': [(6, 0, rec.control_emp_ids.ids)],
                'used_in_project_type_ids': [(6, 0, rec.used_in_project_type_ids.ids)],
                'control_department_ids': [(6, 0, rec.control_department_ids.ids)],
                'formate': rec.id,
                'document_package_id': self.id,
                'department_ids': [(6, 0, rec.department_ids.ids)],
                'manager_ids': [(6, 0, manager_ids)],
                'phase_id': rec.phase_id.id if rec.phase_id else False,
            }
            self.env['document.approval'].create(vals)
        
        self.create_apqp_timeline_chart()
        # Populate attachments from templates when creating from select_all_formate
        if self.apqp_timeline_chart_id:
            self.apqp_timeline_chart_id.populate_attachments_from_templates()
        self._create_timeline_formats()
        return True
    
    def write(self, vals):
        res = super(DocumentPackageInherit, self).write(vals)
        if 'document_approval_ids' in vals:
            self._create_timeline_formats()
        return res