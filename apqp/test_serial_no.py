# Test script for serial number functionality
# Run this in Odoo shell: python odoo-bin shell -d your_database

# Get the models
MomFormat = env['apqp.mom.format']
TimelineChart = env['apqp.timeline.chart']

# Create or get a timeline chart
timeline_chart = TimelineChart.search([], limit=1)
if not timeline_chart:
    print("No timeline chart found. Please create one first.")
else:
    print(f"Using timeline chart: {timeline_chart.name}")
    
    # Get existing MOM formats for this timeline chart
    existing_moms = MomFormat.search([('timeline_chart_id', '=', timeline_chart.id)], order='id')
    print(f"Existing MOM formats: {[(m.id, m.serial_no) for m in existing_moms]}")
    
    # Create test MOM formats
    print("\nCreating new MOM formats...")
    open_point = env['apqp.open.point'].search([], limit=1)
    if not open_point:
        open_point = env['apqp.open.point'].create({'name': 'Test Open Point'})
    
    for i in range(3):
        mom = MomFormat.create({
            'timeline_chart_id': timeline_chart.id,
            'open_point_id': open_point.id,
            'target_date': fields.Date.today(),
        })
        print(f"Created MOM format ID: {mom.id}, Serial No: {mom.serial_no}")
    
    # Show all MOM formats
    all_moms = MomFormat.search([('timeline_chart_id', '=', timeline_chart.id)], order='id')
    print(f"\nAll MOM formats after creation: {[(m.id, m.serial_no) for m in all_moms]}")
    
    # Delete one in the middle
    if len(all_moms) >= 3:
        middle_mom = all_moms[len(all_moms)//2]
        print(f"\nDeleting MOM format ID: {middle_mom.id}, Serial No: {middle_mom.serial_no}")
        middle_mom.unlink()
        
        # Show remaining MOM formats
        remaining_moms = MomFormat.search([('timeline_chart_id', '=', timeline_chart.id)], order='id')
        print(f"Remaining MOM formats: {[(m.id, m.serial_no) for m in remaining_moms]}")
