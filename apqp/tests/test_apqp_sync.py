# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase


class TestAPQPSync(TransactionCase):
    
    def setUp(self):
        super(TestAPQPSync, self).setUp()
        
        # Create test phases
        self.phase1 = self.env['apqp.phase'].create({
            'name': 'Phase 1',
            'sequence': 1
        })
        self.phase2 = self.env['apqp.phase'].create({
            'name': 'Phase 2',
            'sequence': 2
        })
        
        # Create test timeline chart
        self.timeline_chart = self.env['apqp.timeline.chart'].create({
            'project_name': 'Test Project',
            'document_package_id': 1,  # Assuming exists
            'start_date': '2024-01-01',
            'target_date': '2024-12-31'
        })
    
    def test_attachment_sync_to_timeline_format(self):
        """Test that attachments sync to timeline formats correctly."""
        
        # Create attachment
        attachment = self.env['apqp.timeline.attachment'].create({
            'timeline_chart_id': self.timeline_chart.id,
            'phase_id': self.phase1.id,
            'format_name': 'Test Format 1',
            'planned_start_date': '2024-01-15',
            'planned_end_date': '2024-02-15',
            'reference': 'REF001'
        })
        
        # Check timeline format created
        timeline_format = self.env['apqp.timeline.format'].search([
            ('timeline_chart_id', '=', self.timeline_chart.id),
            ('phase_id', '=', self.phase1.id),
            ('name', '=', 'Test Format 1'),
            ('display_type', '=', False)
        ])
        
        self.assertTrue(timeline_format, "Timeline format should be created")
        self.assertEqual(timeline_format.reference, 'REF001')
        self.assertEqual(timeline_format.source_attachment_id.id, attachment.id)
    
    def test_format_name_not_overwritten(self):
        """Test that format_name is not overwritten when changing phase."""
        
        # Create attachment with custom format name
        attachment = self.env['apqp.timeline.attachment'].create({
            'timeline_chart_id': self.timeline_chart.id,
            'phase_id': self.phase1.id,
            'format_name': 'My Custom Format',
            'reference': 'REF002'
        })
        
        # Change phase
        attachment.write({'phase_id': self.phase2.id})
        
        # Check format name is preserved
        self.assertEqual(attachment.format_name, 'My Custom Format')
        
        # Check new timeline format in phase 2
        timeline_format = self.env['apqp.timeline.format'].search([
            ('timeline_chart_id', '=', self.timeline_chart.id),
            ('phase_id', '=', self.phase2.id),
            ('name', '=', 'My Custom Format')
        ])
        
        self.assertTrue(timeline_format, "Timeline format should exist in new phase")
    
    def test_phase_change_in_timeline_format(self):
        """Test that changing phase in timeline format updates attachment."""
        
        # Create attachment
        attachment = self.env['apqp.timeline.attachment'].create({
            'timeline_chart_id': self.timeline_chart.id,
            'phase_id': self.phase1.id,
            'format_name': 'Test Format 3',
        })
        
        # Find the created timeline format
        timeline_format = self.env['apqp.timeline.format'].search([
            ('source_attachment_id', '=', attachment.id)
        ])
        
        # Change phase in timeline format
        timeline_format.write({'phase_id': self.phase2.id})
        
        # Check attachment phase updated
        self.assertEqual(attachment.phase_id.id, self.phase2.id)
