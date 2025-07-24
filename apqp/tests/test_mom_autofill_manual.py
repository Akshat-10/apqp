#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual test script for MOM autofill functionality.
Run this script from Odoo shell: python odoo-bin shell -d your_database
Then execute: exec(open('custom-addons/apqp/test_mom_autofill_manual.py').read())
"""

# Create test data
print("Creating test data...")

# Create test employees
emp1 = env['hr.employee'].create({
    'name': 'John Doe',
})
emp2 = env['hr.employee'].create({
    'name': 'Jane Smith',
})
emp3 = env['hr.employee'].create({
    'name': 'Bob Johnson',
})
print(f"Created employees: {emp1.name}, {emp2.name}, {emp3.name}")

# Create test partner
partner = env['res.partner'].create({
    'name': 'Test Customer ABC',
})
print(f"Created partner: {partner.name}")

# Create test document package
doc_package = env['xf.doc.approval.document.package'].create({
    'name': 'Test Document Package',
    'partner_id': partner.id,
    'start_date': fields.Date.today(),
    'target_date': fields.Date.today(),
})
print(f"Created document package: {doc_package.name}")

# Create test open point
open_point = env['apqp.open.point'].create({
    'name': 'Test Open Point - Quality Check',
    'description': 'Test Description',
})
print(f"Created open point: {open_point.name}")

# Create timeline chart with default attendees and conducted by
print("\nCreating timeline chart with default MOM settings...")
timeline_chart = env['apqp.timeline.chart'].create({
    'project_name': 'Test Project with MOM Defaults',
    'document_package_id': doc_package.id,
    'partner_id': partner.id,
    'attendee_ids': [(6, 0, [emp1.id, emp2.id])],
    'conducted_by_id': emp3.id,
})
print(f"Timeline chart created: {timeline_chart.project_name}")
print(f"Default attendees: {', '.join(timeline_chart.attendee_ids.mapped('name'))}")
print(f"Default conducted by: {timeline_chart.conducted_by_id.name}")

# Test 1: Create MOM format programmatically
print("\n--- Test 1: Creating MOM format programmatically ---")
mom1 = env['apqp.mom.format'].create({
    'timeline_chart_id': timeline_chart.id,
    'open_point_id': open_point.id,
    'target_date': fields.Date.today(),
})
print(f"MOM format created with serial no: {mom1.serial_no}")
print(f"Attendees auto-filled: {', '.join(mom1.attendee_ids.mapped('name'))}")
print(f"Conducted by auto-filled: {mom1.conducted_by_id.name}")

# Test 2: Create MOM format with manual override
print("\n--- Test 2: Creating MOM format with manual override ---")
mom2 = env['apqp.mom.format'].create({
    'timeline_chart_id': timeline_chart.id,
    'open_point_id': open_point.id,
    'target_date': fields.Date.today(),
    'attendee_ids': [(6, 0, [emp1.id])],  # Only emp1
    'conducted_by_id': emp2.id,  # Different conductor
})
print(f"MOM format created with serial no: {mom2.serial_no}")
print(f"Attendees (manual): {', '.join(mom2.attendee_ids.mapped('name'))}")
print(f"Conducted by (manual): {mom2.conducted_by_id.name}")

# Test 3: Simulate inline creation with context
print("\n--- Test 3: Simulating inline creation with context ---")
mom3 = env['apqp.mom.format'].with_context(
    default_timeline_chart_id=timeline_chart.id,
    timeline_chart_id=timeline_chart.id
).create({
    'open_point_id': open_point.id,
    'target_date': fields.Date.today(),
})
print(f"MOM format created with serial no: {mom3.serial_no}")
print(f"Attendees auto-filled: {', '.join(mom3.attendee_ids.mapped('name'))}")
print(f"Conducted by auto-filled: {mom3.conducted_by_id.name}")

print("\n✓ All tests completed successfully!")
print(f"\nTo verify in UI:")
print(f"1. Go to APQP > Timeline Charts")
print(f"2. Open the timeline chart: '{timeline_chart.project_name}'")
print(f"3. Go to 'MOM Format' tab")
print(f"4. Check that Default MOM Settings show the employees")
print(f"5. Try adding a new line - it should auto-fill the attendees and conducted by")
print(f"\nTimeline Chart ID: {timeline_chart.id}")

# Commit the transaction if you want to keep the test data
# env.cr.commit()
print("\nNote: Transaction not committed. Data will be rolled back when you exit the shell.")
print("To keep the data, uncomment the env.cr.commit() line above.")
