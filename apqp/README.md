# APQP Timeline Chart Module

## What is APQP? (Definition)

**APQP (Advanced Product Quality Planning)** is a structured methodology for defining and executing the steps necessary to ensure that a product meets customer expectations. It is widely used in automotive and manufacturing industries to achieve robust planning, prevent quality problems, and ensure on-time launch.

## About the APQP Timeline Chart Module

The **APQP Timeline Chart Module** for Odoo 16 is a custom addon that centralizes and streamlines APQP phase tracking, document management, and project monitoring using visual, interactive timeline charts. This module enhances your Odoo with:
- End-to-end visibility for all APQP phases and formats.
- Easy management, monitoring, and reporting of progress for every document package.
- Automation and synchronization between phases, formats, attachments, and review steps.

---

**Module Details:**

- **Technical Name:** `apqp`
- **Version:** 16.0.1.0+
- **Category:** Project Management / Quality / Manufacturing
- **License:** LGPL-3 (implied)
- **Author:** Your Company

## Dependencies

This module requires the following Odoo modules:

- `base` - Odoo core module
- `xf_doc_approval` - Document approval management
- `iatf` - IATF standards compliance
- `mail` - Email and messaging functionality
- `hr` - Human resources
- `product` - Product management
- `board` - Dashboard functionality

## Key Features & Functionalities

### 1. APQP Timeline Chart Management
- Auto-creation of timeline charts per document package.
- Charts pull relevant dates, part/customer info, and document types (Safe Launch, Prototype, etc) right from the package.
- Visual Gantt-like chart and timeline HTML with phase grouping, color-coded status, and metrics (% progress, actual vs. target).

### 2. APQP Phases
- Fully customizable set of phases (add/modify via configuration menu).
- Each phase supports color, description, and ordering/sequence.
- Phases are referenced throughout timeline, attachments, and formats.

### 3. Timeline Formats & Templates
- Add format lines to timeline, grouping by phase.
- Drag-and-drop to reorder or regroup timeline entries by phase.
- **Format Template Management**: Reusable templates for rapid chart creation. Define typical formats/steps per phase and apply to new timelines automatically.

### 4. Document Attachment Management
- Attach files to timeline entries directly (with drag-and-drop multi-upload support).
- Attachments sync bi-directionally: update one side, timeline format reflects changes; remove an attachment, the entry is smartly cleaned.
- Tracks count/availability of all related attachments.

### 5. Minutes of Meeting (MOM) Integration
- Dedicated MOM Formats (see new menu!) to log open points, responsibilities, due/actual dates, attendees, and approval.
- State workflow (draft, in progress, completed, approved, cancelled) with complete state history.
- Grouping and reporting on MOM per timeline/project/phase.

### 6. Open Points (New Model & Menu)
- Centralize all outstanding action points relevant to APQP/MOM.
- Assign to responsible parties; track status; ensure nothing is missed in the quality plan.

### 7. Menu Structure (Navigation)
- **APQP** (root menu)
   - **Timeline Charts**: Your main projects and their timelines.
   - **MOM Formats**: Manage, review and approve minutes of meeting formats.
   - **Timeline Attachments**: Mass-manage all attachments across charts.
   - **Configuration:**
     - **Phases**, **Format Templates**, **Open Points**: Full admin power over reference/config data.

### 8. Reporting & Views
- Tree and form views for all major entities (charts, formats, MOMs, open points, attachments, templates).
- Rich search/group by (by phase, by project, status, date, and more).

### 9. Security & Role Based Access
- Granular control: limit certain actions to system users/admins, and basic tracking for business users.
- Full Chatter and Odoo mail integration for tracking, notes, and communication.

### 10. Customization & Automation
- All key models are extensible via standard Odoo inheritance.
- Context-aware syncs prevent recursion/loops.
- Computed fields for status, progress, colorization, etc.

## Data Models Overview & Usage

### 1. APQP Phase (`apqp.phase`)
Defines reference phases for the APQP process - maintained via a dedicated menu. Used for grouping, ordering, and color-coding timeline entries, formats, and attachments.

| Field         | Type     | Description                         |
|-------------- |--------- |-------------------------------------|
| name          | Char     | Phase name                          |
| sequence      | Integer  | Sequence/order for display           |
| description   | Text     | Details about the phase              |
| color         | Integer  | Visual color (selection)             |
| active        | Boolean  | Visibility status                    |

### 2. Format Template (`apqp.format.template`)
Reusable templates for typical APQP timeline formats, assignable to any phase. Use these to pre-populate new timeline charts for consistency.

| Field        | Type      | Description         |
|--------------|----------|---------------------|
| format_name  | Char     | Format name         |
| phase_id     | Many2one | Template phase      |
| sequence     | Integer  | Display order       |
| active       | Boolean  | In use?             |

### 3. Timeline Chart (`apqp.timeline.chart`)
Main entity representing an APQP plan for a document package/project. Manages phases, formats, attachments, and MOM entries.

| Field               | Type      | Description                           |
|---------------------|-----------|---------------------------------------|
| project_name        | Char      | Main project name                     |
| document_package_id | Many2one  | Related document package              |
| partner_id          | Many2one  | Customer                              |
| start_date          | Date      | Plan start                            |
| target_date         | Date      | Target finish                         |
| doc_type            | Selection | Project/document category             |
| timeline_format_ids | O2M       | All timeline formats                  |
| attachment_ids      | O2M       | All attachments                       |
| mom_format_ids      | O2M       | Minutes of Meeting entries            |
| state               | Selection | Chart/project workflow state          |
| progress            | Float     | Computed overall progress (%)         |
| timeline_html       | Html      | Timeline chart visualization          |

### 4. Timeline Format (`apqp.timeline.format`)
Details individual timeline steps/entries under a chart, grouped by phase. Attachments, dates, status, etc. are all tracked here. Supports line sections (for phase headers), notes, and regular lines.

| Field              | Type      | Description                  |
|--------------------|-----------|------------------------------|
| timeline_chart_id  | Many2one  | Link to chart                |
| phase_id           | Many2one  | APQP phase                   |
| name               | Char      | Format/task name             |
| planned_start_date | Date      | Planned start                |
| actual_start_date  | Date      | Actual start                 |
| planned_end_date   | Date      | Planned end                  |
| actual_end_date    | Date      | Actual end                   |
| status             | Selection | Status auto-calculated       |
| reference          | Char      | Reference info               |
| attachment_ids     | Many2many | Linked docs                  |
| sequence           | Integer   | Display order                |
| display_type       | Selection | Section, note, or line       |
| source_attachment_id | M2O    | If format is from attachment |

### 5. Timeline Attachment (`apqp.timeline.attachment`)
File/document handling at the timeline entry level: attached docs trigger timeline entry updates (and vice versa).

| Field             | Type      | Description                   |
|-------------------|-----------|-------------------------------|
| timeline_chart_id | Many2one  | Linked timeline chart         |
| phase_id          | Many2one  | Phase of attached doc         |
| format_name       | Char      | Document/format type          |
| planned_start_date| Date      | Planning                      |
| actual_start_date | Date      | Execution                     |
| state             | Selection | Auto status based on dates    |
| attachment_ids    | Many2many | Files attached                |
| sequence          | Integer   | Order for display             |

### 6. MOM Format (`apqp.mom.format`) - NEW
Captures Minutes of Meeting actions, approval, attendees, and traceable open points—including a full approval workflow and state history.

| Field                 | Type           | Description                             |
|-----------------------|----------------|-----------------------------------------|
| timeline_chart_id     | Many2one       | Parent timeline chart (project)         |
| open_point_id         | Many2one       | Linked open point from register         |
| responsibility_id     | Many2one       | Person/team responsible                 |
| sequence/serial_no    | Integer        | Line order and unique number            |
| target_date           | Date           | When it should be completed             |
| actual_completion_date| Date           | Closed date                             |
| remarks               | Text           | Comments                                |
| attendee_ids          | Many2many      | MOM attendees (employees)               |
| conducted_by_id       | Many2one       | Meeting lead                            |
| approve_date/by_id    | Datetime/M2O   | Approval info                           |
| state                 | Selection      | Workflow/approval state                 |
| state_history         | Text           | Full change history                     |

### 7. Open Point (`apqp.open.point`) - NEW
Reference register of all open issues or action points related to project quality and meetings.

| Field         | Type    | Description                       |
|---------------|---------|-----------------------------------|
| name          | Char    | Unique description                 |
| description   | Text    | Details, context                   |
| active        | Boolean |                                 |

---

All main models are extensible—the above fields may be referenced/linked by custom modules as your business grows.

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

## Workflow & Usage Guide

### Typical User Flow

1. **Create or open a Document Package** in Odoo.
2. **Timeline Chart is created** automatically (or can be manually added if needed).
3. **View all phases/formats/attachment slots** structured as per company APQP process.
4. **(Optionally) Apply Format Templates** to auto-populate common steps per phase.
5. **Attach documents** directly; fill out references and relevant dates.
6. **All attachment actions are synced** to the chart—modifying or reordering updates the backend as needed.
7. **MOM Formats** can be logged at any point in the project lifecycle, with full attendee, responsibility, and open point tracking.
8. **Open Points Linkage**—track what’s still outstanding directly from open point register.
9. **Progress, status, and timeline visualization** is available throughout; refresh button ensures latest view, even on large projects.
10. **Admin users can create/configure phases, format templates, or open points** as the business process changes.

### Menu Navigation Quick Reference

- **APQP / Timeline Charts**: Browse/edit all project timelines.
- **APQP / MOM Formats**: Review project meeting actions/approvals.
- **APQP / Timeline Attachments**: Find and manage all files fast.
- **APQP / Configuration**: Set up phases, format templates, open points to match your business’s process.

### Special Features
- Drag-and-drop phase/format reordering with live updates.
- Role-based workflow for MOM approval/closure.
- Status calculation and color, for instant visual reporting.

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
