# APQP Timeline Chart Module

## Overview

The APQP (Advanced Product Quality Planning) Timeline Chart Module is a comprehensive Odoo 16 addon that manages quality planning timelines for document packages. It provides automatic synchronization between document attachments and timeline formats, enabling efficient project quality management.

**Module Details:**

- **Technical Name**: `apqp`
- **Version**: 16.0.1.0
- **Category**: Project Management
- **License**: LGPL-3 (implied)
- **Author**: Your Company

## Dependencies

This module requires the following Odoo modules:

- `base` - Odoo core module
- `xf_doc_approval` - Document approval management
- `iatf` - IATF standards compliance
- `mail` - Email and messaging functionality
- `hr` - Human resources
- `product` - Product management
- `board` - Dashboard functionality

## Features

### 1. Automatic APQP Timeline Chart Creation

- Automatically generates timeline charts for each document package
- Inherits data from document packages including:
  - Project name and dates
  - Customer information
  - Part details (name, number, drawing number)
  - Document type (Safe Launch, Prototype, PreLaunch, Production)

### 2. Phase-wise Format Management

- Supports APQP phases with customizable sequences
- Phase sections automatically created in timeline
- Drag-and-drop functionality for phase reorganization
- Color-coded phase indicators

### 3. Timeline Tracking with Dates

- **Planned Dates**: Start and end dates for planning
- **Actual Dates**: Real execution dates for tracking
- **Project Dates**: Overall project timeline boundaries
- **Status Tracking**: Automatic status calculation based on dates
  - Not Started (gray)
  - In Progress (yellow)
  - Completed (green)
  - Delayed (red)

### 4. Document Attachment Management

- Bi-directional synchronization between attachments and timeline formats
- Automatic format creation when attachments are added
- Attachment count tracking
- Support for multiple file attachments per timeline entry

### 5. Phase-wise Timeline Visualization

- HTML-based timeline overview with professional styling
- Responsive table layout showing:
  - Phase groupings
  - Format names and references
  - Planned vs actual dates
  - Color-coded status indicators
- Manual refresh capability with success notifications

### 6. Advanced Synchronization Features

- **Automatic Sync**: Changes in attachments reflect in timeline formats
- **Reverse Sync**: Timeline format updates sync back to source attachments
- **Smart Deletion**: Removes timeline formats when last attachment is deleted
- **Sequence Management**: Maintains proper ordering within phases

## Data Models

### 1. APQP Phase (`apqp.phase`)

**Purpose**: Defines the phases in the APQP process

| Field       | Type    | Description                 |
| ----------- | ------- | --------------------------- |
| name        | Char    | Phase name (required)       |
| sequence    | Integer | Display order (default: 10) |
| description | Text    | Phase description           |
| color       | Integer | Color index for UI          |
| active      | Boolean | Active/archived status      |

### 2. APQP Timeline Chart (`apqp.timeline.chart`)

**Purpose**: Main container for timeline data

| Field               | Type      | Description                      |
| ------------------- | --------- | -------------------------------- |
| project_name        | Char      | Project name (required, tracked) |
| document_package_id | Many2one  | Link to document package         |
| partner_id          | Many2one  | Customer reference               |
| start_date          | Date      | Project start date               |
| target_date         | Date      | Target completion date           |
| doc_type            | Selection | Document type category           |
| part_id             | Many2one  | Product/part reference           |
| state               | Selection | Overall status                   |
| progress            | Float     | Completion percentage (computed) |
| timeline_html       | Html      | Visual timeline (computed)       |

### 3. APQP Timeline Format (`apqp.timeline.format`)

**Purpose**: Individual timeline entries with phase grouping

| Field              | Type      | Description            |
| ------------------ | --------- | ---------------------- |
| timeline_chart_id  | Many2one  | Parent timeline chart  |
| phase_id           | Many2one  | Associated phase       |
| name               | Char      | Format name            |
| sequence           | Integer   | Display order          |
| planned_start_date | Date      | Planned start          |
| planned_end_date   | Date      | Planned completion     |
| actual_start_date  | Date      | Actual start           |
| actual_end_date    | Date      | Actual completion      |
| status             | Selection | Computed status        |
| display_type       | Selection | Section/note indicator |
| attachment_ids     | Many2many | File attachments       |

### 4. APQP Timeline Attachment (`apqp.timeline.attachment`)

**Purpose**: Manages document attachments with timeline sync

| Field             | Type      | Description           |
| ----------------- | --------- | --------------------- |
| timeline_chart_id | Many2one  | Parent timeline chart |
| phase_id          | Many2one  | Target phase          |
| format_name       | Char      | Format identifier     |
| sequence          | Integer   | Order within phase    |
| attachment_ids    | Many2many | Linked files          |
| state             | Selection | Current status        |

## Security Model

The module implements role-based access control:

| Model                    | User Group | Read | Write | Create | Delete |
| ------------------------ | ---------- | ---- | ----- | ------ | ------ |
| apqp.phase               | Users      | ✓   | ✗    | ✗     | ✗     |
| apqp.phase               | System     | ✓   | ✓    | ✓     | ✓     |
| apqp.timeline.chart      | Users      | ✓   | ✓    | ✓     | ✗     |
| apqp.timeline.chart      | System     | ✓   | ✓    | ✓     | ✓     |
| apqp.timeline.format     | Users      | ✓   | ✓    | ✓     | ✓     |
| apqp.timeline.attachment | Users      | ✓   | ✓    | ✓     | ✓     |

## Workflow

### Standard Operation Flow

1. **Document Package Creation**: User creates a document package in the system
2. **Timeline Chart Generation**: APQP timeline chart is automatically created
3. **Attachment Addition**: User adds attachments with phase and format information
4. **Automatic Sync**: System creates corresponding timeline format entries
5. **Progress Tracking**: User updates actual dates as work progresses
6. **Status Updates**: System automatically calculates and displays status
7. **Review**: Timeline overview provides comprehensive project view

### Phase Management Workflow

1. Phases are pre-defined with sequences
2. Timeline formats are grouped under phase sections
3. Drag-and-drop reordering updates phase associations
4. Changes sync bidirectionally with attachments

## Installation

1. **Prerequisites**:

   - Ensure all dependent modules are installed
   - Odoo 16.0 or compatible version
2. **Installation Steps**:

   ```bash
   # Copy module to custom addons directory
   cp -r apqp /path/to/odoo/custom-addons/

   # Update module list
   ./odoo-bin -u apqp -d your_database
   ```
3. **Initial Configuration**:

   - Configure APQP phases via Settings → Technical → APQP Phases
   - Set up user permissions as needed

## Usage Guide

### Creating Timeline Charts

1. Navigate to a Document Package
2. Timeline Chart is auto-created upon package creation
3. Access via smart button or menu

### Managing Attachments

1. Open Timeline Chart form
2. Add attachments in the Attachments tab
3. Specify:
   - Phase (dropdown selection)
   - Format Name (free text)
   - Planned dates
   - Reference information
4. Save to trigger automatic sync

### Tracking Progress

1. Update actual start/end dates in timeline formats
2. Status automatically updates based on dates
3. Overall progress percentage shown on timeline chart

### Viewing Timeline Overview

1. Click "Timeline Overview" button
2. Review HTML table with all phases and formats
3. Use "Refresh Timeline" for manual updates

## Technical Details

### Inheritance Structure

- `apqp.timeline.chart` inherits `mail.thread` and `mail.activity.mixin`
- Document models inherit from base document approval module

### Computed Fields

- **Progress**: Calculated as (completed formats / total formats) × 100
- **Status**: Determined by comparing actual vs planned dates
- **Timeline HTML**: Generated dynamically with embedded CSS

### Context Flags

- `skip_sync`: Prevents recursive synchronization
- `from_attachment_sync`: Identifies sync source
- `group_by_phase`: Default grouping in views

## Customization

### Adding New Phases

1. Navigate to Settings → Technical → APQP Phases
2. Create new phase with name and sequence
3. Existing timelines automatically include new phase

### Modifying Status Colors

Edit CSS in `_compute_timeline_html` method:

```css
.status-completed { background-color: #d4edda; }
.status-in_progress { background-color: #fff3cd; }
.status-delayed { background-color: #f8d7da; }
```

### Extending Fields

Inherit models to add custom fields:

```python
class APQPTimelineChartCustom(models.Model):
    _inherit = 'apqp.timeline.chart'
  
    custom_field = fields.Char('Custom Field')
```

## Troubleshooting

### Common Issues

1. **Attachments not syncing**

   - Check if `skip_sync` context is set
   - Verify phase_id and format_name are filled
   - Ensure user has proper permissions
2. **Timeline overview not updating**

   - Use manual refresh button
   - Check for JavaScript errors in browser console
   - Verify computed field dependencies
3. **Phase changes not reflecting**

   - Ensure drag-and-drop handle is visible
   - Check sequence field permissions
   - Verify bidirectional sync is enabled

### Debug Mode

Enable debug logging:

```python
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
```

## Best Practices

1. **Data Entry**

   - Always specify phase before format name
   - Use consistent format naming conventions
   - Set planned dates before actual dates
2. **Performance**

   - Limit attachments per timeline format
   - Use batch operations for multiple updates
   - Archive completed timelines
3. **Maintenance**

   - Regular cleanup of orphaned attachments
   - Periodic review of phase sequences
   - Monitor sync performance

## Version History

### Version 16.0.1.0

- Initial release for Odoo 16
- Core timeline management features
- Bidirectional synchronization
- HTML timeline overview
- Fixed Issues:
  - ✅ Format name preservation during phase selection
  - ✅ Proper attachment-to-format synchronization
  - ✅ Drag-and-drop phase management
  - ✅ Automatic and manual timeline refresh
  - ✅ Bidirectional sync implementation

## Support and Contribution

For issues, feature requests, or contributions:

1. Check existing documentation
2. Review module logs for errors
3. Contact system administrator or module maintainer

---

*This module is part of the Odoo custom addons for APQP management. Ensure proper testing in a development environment before production deployment.*
