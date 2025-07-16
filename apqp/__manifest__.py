# -*- coding: utf-8 -*-
{
    'name': 'APQP Timeline Chart',
    'version': '16.0.1.0.2',
    'category': 'Project Management',
    'summary': 'Advanced Product Quality Planning Timeline Chart Management',
    'description': """
        APQP Timeline Chart Module
        
        This module creates APQP Timeline Charts for Document Package management.
        
        Features:
        - Automatic APQP Timeline Chart creation for each Document Package
        - Phase-wise format management
        - Timeline tracking with planned and actual dates
        - Document attachment management
        - Phase-wise timeline visualization
    """,
    'author': 'Your Company',
    'depends': ['base', 'xf_doc_approval', 'iatf', 'mail', 'hr', 'product', 'board'],
    'data': [
        'security/ir.model.access.csv',
        'data/apqp_phase_data.xml',
        'data/apqp_sequence_data.xml',
        'data/apqp_timeline_attachment_data.xml',
        'wizard/apqp_timeline_overview_wizard_views.xml',
        'views/apqp_timeline_chart_views.xml',
        'views/apqp_format_template_views.xml',
        'views/apqp_phase_views.xml',
        'views/apqp_timeline_attachment_views.xml',
        'views/apqp_mom_format_views.xml',
        'views/document_formate_inherit_views.xml',
        'views/document_approval_inherit_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
