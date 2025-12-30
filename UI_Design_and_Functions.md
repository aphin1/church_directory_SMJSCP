# Church Directory Desktop Application – UI & Functional Design

## Overview

This document describes the **user interface** and **functional behavior** of the stand‑alone Windows church directory application. The app is built in Python with a desktop UI framework (e.g., PyQt) and uses SQLite as its local database. The primary goals are:

- Maintain a structured directory of families, members, and departed members.
- Provide granular, role‑based access for viewing, adding, editing, and exporting data (Super Admin > Admin > Add‑Member > View‑Member).
- Support PDF/Excel exports, notifications, soft‑delete with audit tracking, and basic health/usage reporting.

---

## Main Window Layout

The main window is divided into three regions:

- Left: Navigation sidebar (families A–Z and prayer groups).
- Center: Family card view (details, members, and departed members).
- Right: Notifications panel (birthdays and anniversaries).

|----------------------------------------------------------------------------------|
| Menu Bar / Top Bar (App title, current role, login/logout, global actions) |
|-------------------------+--------------------------------------+-----------------|
| | | |
| LEFT SIDEBAR | FAMILY CARD VIEW | RIGHT SIDEBAR |
| | | NOTIFICATIONS |
|-------------------------+--------------------------------------+-----------------|
| Status Bar (messages, progress, health info snippets) |
|----------------------------------------------------------------------------------|


---

## Navigation Sidebar

### Visual Layout

+-----------------------------------------+
| Search |
| [ Text box .................... ] |
+-----------------------------------------+
| Families A–Z |
| A |
| - Abraham |
| - Alexander |
| B |
| - Benjamin |
| - Binu |
| ... |
+-----------------------------------------+
| Prayer Groups ▾ |
| St. Mary's (bg: light blue) |
| - Benjamin |
| St. Joseph's (bg: light green) |
| - Alexander |
| ... |
+-----------------------------------------+


### Behavior & Functions

- **Search box**
  - Accepts partial text.
  - Filters families by:
    - Family name
    - Member name
    - Email
    - Phone
    - Parish
  - Results update the family list in the sidebar and the card view.

- **Family list (A–Z)**
  - Groups families alphabetically by family name.
  - Clicking a family name loads its card in the center area.
  - Soft‑deleted families are hidden for non‑admin and non‑super‑admin users.
  - Admin/Super Admin can choose to show deleted families with a toggle.

- **Prayer group section**
  - Expandable/collapsible groups.
  - Each group shows its families in alphabetical order.
  - Each prayer group has its own **page background color**, set at creation time and unique among groups (no two groups share the same color).
  - When a prayer group is selected, its color is applied to the family card background and to any empty space around the fixed image box.
  - Clicking a family from this section behaves the same as from the A–Z list.

---

## Family Card View

The center panel displays the full detail of a selected family in a compact card style.

### Visual Layout

|--------------------------------------------------------------------------|
| [ 160 x 120 PHOTO BOX ] | FAMILY NAME: [Family Name] |
| (fixed size container) | |
| | Current Address: [current address] |
| | Home Address: [home address] |
| | Parish: [parish] Prayer Group: [group] |
|--------------------------------------------------------------------------|

________________________________________________________________________________
| Members                                                      (Active)        |
| ---------------------------------------------------------------------------- |
|                                                                              |
|                                                                              |
|                                                                              |
|                                                                              |
|                                                                              |
| -----------------------------------------------------------------------      |
| [Export Card PDF]  [Edit Members]*  [Soft Delete Family]*                    |
| * Admin and Super Admin only                                                 |
| +--------------------------------------------------------------------------+ |
| Departed Family Members (Visible section)                                    |
| -----------------------------------------------------------------------      |
|                                                                              |
|                                                                              |
|                                                                              |
|                                                                              |
| -----------------------------------------------------------------------      |
| +--------------------------------------------------------------------------+ |


### Image Handling (160×120 Box)

- The family photo is displayed in a **fixed 160×120 pixel container**.
- Rules:
  - Imported images are scaled to fit while preserving aspect ratio.
  - If using “fit inside”, any empty space (letterboxing/pillarboxing) is filled with the **page background color** of the current prayer group.
  - Images are never distorted.
- **Small image warning**
  - If the original image is smaller than 160×120:
    - A popup warns: “The selected image is smaller than the minimum recommended size (160×120). Do you want to upload a different image or continue with this one?”
    - Buttons:
      - “Choose Another Image”
      - “Continue with This Image”
    - If user continues, the image is upscaled to fit, accepting potential quality loss.

- **Validation**
  - All images are validated to ensure they are real image files (e.g., JPEG/PNG) before saving.
  - Non‑image data is rejected with an error message, and the user is asked to pick another file.

### Data Elements

- Family metadata as before: names, addresses, parish, prayer group, etc.
- Members table and departed members section as previously described.

### Actions (Role‑Based)

- **Export Card PDF (View‑Member, Add‑Member, Admin, Super Admin)**
  - Generates a PDF representation of the current family card.
  - Includes family photo, active members, and departed members.
  - PDF is generated on demand; not stored in DB.

- **Edit Members (Admin & Super Admin only)**
  - Opens an edit dialog or inline editing interface for:
    - Updating member details.
    - Updating family metadata.
    - Updating assigned prayer group (which also updates background color).
  - Non‑admin roles cannot edit after submission.

- **Soft Delete Family (Admin & Super Admin)**
  - Marks the family and associated members as deleted (soft delete).
  - Entry disappears from standard views, remains in DB.
  - Admin/Super Admin can view and restore via admin tools.

---

## Prayer Group Management & Colors

### Creation & Editing (Admin & Super Admin)

- Admin and Super Admin can:
  - Create new prayer groups.
  - Assign:
    - Group name (unique).
    - Background color (UI color picker).
- Constraints:
  - No two prayer groups may share the exact same background color.
  - Background color is used for:
    - Page/card background when a family from that group is displayed.
    - Fill color for any empty space around the 160×120 photo box.

### UI

- Prayer group management screen:
  - List of existing groups with name and color sample.
  - Buttons to Add, Edit, and (optionally) Disable/Archive a group.
  - Color picker for selecting unique colors.

---

## Add / Edit Multi‑Step Dialog

New families and members are added using a guided wizard. Only **Add‑Member** role can create new entries; **Admin** and **Super Admin** can later edit.

(Existing steps remain; only image logic updated.)

### Step 4 – Photo Upload (Updated)

- File chooser for family photo.
- When the user selects an image:
  - Validate file is an image.
  - Check image dimensions.
  - If dimensions < 160×120 (either width or height):
    - Show the small‑image popup described above.
- Preview:
  - Show the image as it will appear in the 160×120 box, with group background color filling empty space.

---

## Notifications Panel

Same as defined earlier, showing weekly birthdays and anniversaries with week/day navigation. Background follows the current prayer group page color theme.

---

## Roles & Permissions (Updated with Super Admin)

### Role Overview

1. **Super Admin (new)**
   - Top‑level administrative role.
   - Main capabilities:
     - Manage admins and other users.
     - Export high‑level reports and complete data (Excel/PDF).
     - View and export audit logs and system health/usage.
     - No normal data browsing of families (as per “No data view” requirement).
2. **Admin (Vicar)**
   - Edit existing families and members.
   - Soft delete and restore entries.
   - Manage prayer groups.
   - Access admin dashboard exports (directory, events, departed).
3. **Add‑Member**
   - Add new families and members via the wizard.
   - No edit after submission.
   - No delete.
4. **View‑Member**
   - View directory and family cards.
   - Export individual family card PDF.
   - Cannot see deleted entries.

---

## Super Admin Console

The Super Admin uses a separate console or restricted mode focused on **administration and reporting**, not data browsing.

### Layout

+---------------------------------------------------------------+
| Super Admin Console |
+---------------------------------------------------------------+
| [Export Family List (table view) to Excel/PDF] |
| Includes: Family, Prayer Group Name, etc. |
| |
| [Export Complete Data to Excel] |
| Full DB export for backup/import in other software. |
| |
| [View & Export Audit Logs (last 365 days)] |
| - Filter by date, user, action, table. |
| - Export to PDF/Excel. |
| |
| [System Health & Usage] |
| - Memory usage (photos, text, logs). |
| - Storage usage per data type. |
| - CPU utilization samples. |
| - Crash reports. |
| |
| [Close Console] |
+---------------------------------------------------------------+


### Super Admin Features

1. **Export Family List with Prayer Group (Table View)**
   - Output:
     - Columns: Family ID, Family Name, Prayer Group Name, Parish, address fields.
   - Formats:
     - Excel (XLSX or CSV – easy to generate and open). [web:52][web:63]
     - PDF with tabular layout.
   - This export is list‑style, not card‑style.

2. **No Data View**
   - Super Admin does **not** see standard family cards or detailed member records inside the main UI.
   - Access is only through:
     - Aggregated table exports.
     - High‑level metrics.
     - Audit logs.
   - Prevents confusion between operational and oversight roles.

3. **Export Complete Data to Excel**
   - Full database export:
     - Families
     - Members
     - Departed members
     - Prayer groups
     - Users (excluding sensitive fields like password hashes, or with masking)
   - Format:
     - Preferably multiple sheets in a single Excel workbook or multiple CSVs.
   - Purpose:
     - Backup.
     - Import to other software (e.g., spreadsheet tools or external DBs).

4. **Audit Logs: View & Export (Last 365 Days)**
   - Retention:
     - Only the last 365 days of logs are kept.
     - When log storage is full or older than 365 days, **oldest entries are overwritten by new ones** (circular log behavior). [web:50][web:62]
   - UI:
     - Paginated list:
       - Timestamp
       - User
       - Role
       - Action (add, edit, delete, restore, login, export)
       - Target (family/member/prayer group)
       - Optional details (before/after values summary)
     - Filters:
       - Date range
       - User
       - Action type
       - Table/entity
   - Exports:
     - PDF (paged, readable report).
     - Excel (for further analysis).

5. **System Health & Usage**
   - High‑level indicators (read‑only, no tuning from UI):
     - Approximate memory and storage usage by:
       - Photos (storage in DB).
       - Textual data (family/member/departed records).
       - Logs (audit log table size).
     - CPU utilization snapshots (e.g., average of last N seconds when viewing).
     - Number of crash reports stored.
   - Crash handling:
     - On application crash or unhandled exception:
       - A crash report is generated (e.g., timestamp, stack trace, action).
       - Stored in a crash log table or file.
     - Super Admin can:
       - View a list of recent crash reports.
       - Export crash log as text or PDF for debugging.

---

## Admin Dashboard (Revised)

The Admin (Vicar) dashboard remains similar, focused on operational data, not full‑system reporting.

### Actions

- Export Directory PDF (card‑style, with or without deleted).
- Export birthdays/anniversaries and departed members PDF (weekly/monthly).
- Show/restore deleted entries.
- See per‑task progress (e.g., PDF generation progress bar).

Super Admin has **additional** export/report tasks but no normal data browsing.

---

## Status Bar & Progress Indicators

- Status bar:
  - Operation messages.
  - Hints about current role and mode (Admin vs Super Admin).
- Progress indicators:
  - For PDF/Excel exports (directory, complete data, logs).
  - For image validation and small image warnings.

---

## Summary of Key User Flows (Updated)

### Super Admin – Export Family List

1. Open Super Admin Console.
2. Click “Export Family List (table view)”.
3. Choose format (Excel or PDF).
4. Select save location.
5. Progress bar shows export status.
6. File is created with families and prayer group names.

### Super Admin – Export Complete Data

1. Open Super Admin Console.
2. Click “Export Complete Data to Excel”.
3. Choose workbook/file location.
4. Progress bar updates; status shown on completion.

### Super Admin – Audit Logs for Last 365 Days

1. Open Super Admin Console.
2. Open “View & Export Audit Logs”.
3. Filter by date/user/action as needed.
4. Export to PDF or Excel for the last 365 days.
5. Oldest entries automatically removed/overwritten as new logs arrive beyond capacity.

---
