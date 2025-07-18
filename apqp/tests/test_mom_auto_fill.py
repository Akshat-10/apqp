# -*- coding: utf-8 -*-
from odoo.tests import common, TransactionCase
from odoo import fields


class TestMOMAutoFill(TransactionCase):
    """Test automatic data transfer from timeline chart to MOM format"""
    
    def setUp(self):
        super(TestMOMAutoFill, self).setUp()
        
        # Create test employees
        self.employee_1 = self.env['hr.employee'].create({
            'name': 'Test Employee 1',
        })
        self.employee_2 = self.env['hr.employee'].create({
            'name': 'Test Employee 2',
        })
        self.employee_3 = self.env['hr.employee'].create({
            'name': 'Test Employee 3',
        })
        
        # Create test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
        })
        
        # Create test document package
        self.doc_package = self.env['xf.doc.approval.document.package'].create({
            'name': 'Test Document Package',
            'partner_id': self.partner.id,
            'start_date': fields.Date.today(),
            'target_date': fields.Date.today(),
        })
        
        # Create test open point
        self.open_point = self.env['apqp.open.point'].create({
            'name': 'Test Open Point',
            'description': 'Test Description',
        })
    
    def test_mom_format_auto_fill(self):
        """Test that MOM format automatically gets attendee_ids and conducted_by_id from timeline chart"""
        
        # Create timeline chart with attendees and conducted by
        timeline_chart = self.env['apqp.timeline.chart'].create({
            'project_name': 'Test Project',
            'document_package_id': self.doc_package.id,
            'partner_id': self.partner.id,
            'attendee_ids': [(6, 0, [self.employee_1.id, self.employee_2.id])],
            'conducted_by_id': self.employee_3.id,
        })
        
        # Create MOM format linked to timeline chart
        mom_format = self.env['apqp.mom.format'].create({
            'timeline_chart_id': timeline_chart.id,
            'open_point_id': self.open_point.id,
            'target_date': fields.Date.today(),
        })
        
        # Check that attendees and conducted by were automatically filled
        self.assertEqual(len(mom_format.attendee_ids), 2, "MOM format should have 2 attendees")
        self.assertIn(self.employee_1, mom_format.attendee_ids, "Employee 1 should be in attendees")
        self.assertIn(self.employee_2, mom_format.attendee_ids, "Employee 2 should be in attendees")
        self.assertEqual(mom_format.conducted_by_id, self.employee_3, "Conducted by should be Employee 3")
    
    def test_mom_format_manual_override(self):
        """Test that manually provided values are not overridden"""
        
        # Create timeline chart with attendees and conducted by
        timeline_chart = self.env['apqp.timeline.chart'].create({
            'project_name': 'Test Project 2',
            'document_package_id': self.doc_package.id,
            'partner_id': self.partner.id,
            'attendee_ids': [(6, 0, [self.employee_1.id, self.employee_2.id])],
            'conducted_by_id': self.employee_3.id,
        })
        
        # Create MOM format with manual values
        mom_format = self.env['apqp.mom.format'].create({
            'timeline_chart_id': timeline_chart.id,
            'open_point_id': self.open_point.id,
            'target_date': fields.Date.today(),
            'attendee_ids': [(6, 0, [self.employee_1.id])],  # Only employee 1
            'conducted_by_id': self.employee_2.id,  # Different conductor
        })
        
        # Check that manual values were preserved
        self.assertEqual(len(mom_format.attendee_ids), 1, "MOM format should have only 1 attendee")
        self.assertIn(self.employee_1, mom_format.attendee_ids, "Employee 1 should be in attendees")
        self.assertNotIn(self.employee_2, mom_format.attendee_ids, "Employee 2 should NOT be in attendees")
        self.assertEqual(mom_format.conducted_by_id, self.employee_2, "Conducted by should be Employee 2")
    
    def test_mom_format_no_defaults(self):
        """Test MOM format creation when timeline chart has no default values"""
        
        # Create timeline chart without attendees and conducted by
        timeline_chart = self.env['apqp.timeline.chart'].create({
            'project_name': 'Test Project 3',
            'document_package_id': self.doc_package.id,
            'partner_id': self.partner.id,
        })
        
        # Create MOM format
        mom_format = self.env['apqp.mom.format'].create({
            'timeline_chart_id': timeline_chart.id,
            'open_point_id': self.open_point.id,
            'target_date': fields.Date.today(),
        })
        
        # Check that fields remain empty
        self.assertEqual(len(mom_format.attendee_ids), 0, "MOM format should have no attendees")
        self.assertFalse(mom_format.conducted_by_id, "Conducted by should be empty")
