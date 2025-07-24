# APQP Timeline Chart Module

## Overview
This module manages Advanced Product Quality Planning (APQP) Timeline Charts with automatic synchronization between attachments and timeline formats.

## FIXED ISSUES
1. ✅ Format name no longer gets overwritten when selecting phase_id in attachments
2. ✅ Attachments properly sync to timeline formats when saving the document
3. ✅ Phase changes can be done using drag-and-drop (sequence handle) in timeline formats
4. ✅ Timeline overview (HTML) updates automatically and can be refreshed manually
5. ✅ Bidirectional sync between attachments and timeline formats

## Key Features

### 1. Attachment Management
- When adding lines in `attachment_ids`:
  - User can freely enter any `format_name` without it being overwritten
  - When changing `phase_id`, the system shows available formats but doesn't auto-fill
  - Upon saving, the attachment automatically creates corresponding entries in `timeline_format_ids`

### 2. Timeline Format Synchronization
- **Automatic Creation**: When an attachment is saved, it creates:
  - A phase section (if not exists) with display_type='line_section'
  - A timeline format entry under the appropriate phase
- **Updates**: Changes to attachment fields (dates, reference) sync to timeline formats
- **Deletion**: When an attachment is deleted, its corresponding timeline format is also removed (if not used by other attachments)

### 3. Phase Management
- Users can change `phase_id` in timeline formats using drag-and-drop (sequence handle)
- Phase changes in timeline formats sync back to source attachments
- Timeline formats maintain proper grouping under phase sections

### 4. Timeline Overview
- HTML table displaying all phases and their formats
- Shows data from both `timeline_format_ids` and `attachment_ids` (without duplication)
- Displays: Phase Name, Format Name, Reference, Planned/Actual dates, and Status
- Color-coded status badges:
  - Green: Completed
  - Yellow: In Progress
  - Red: Delayed
  - Gray: Not Started

### 5. Manual Refresh
- "Refresh Timeline" button on Timeline Overview page
- Updates the HTML table with latest data
- Shows success notification after refresh

## Technical Implementation

### Models
1. **apqp.timeline.attachment**
   - Links to timeline chart
   - Stores format details and dates
   - Syncs with timeline formats on create/write/unlink

2. **apqp.timeline.format**
   - Main timeline format storage
   - Tracks source attachment via `source_attachment_id`
   - Supports sections (display_type='line_section') and regular lines

3. **apqp.timeline.chart**
   - Main container for timeline data
   - Computes HTML overview
   - Links to document package

### Workflow
1. User adds attachment with phase and format name
2. System creates timeline format entry automatically
3. User can reorder formats using drag-and-drop
4. Phase changes sync between formats and attachments
5. Timeline overview updates automatically or manually

## Usage Notes
- Format names are preserved when entered by users
- Phase changes can be done in either attachments or timeline formats
- Timeline overview provides a consolidated view of all data
- All changes are synchronized bidirectionally
