# Church Directory Desktop Application – Refined Requirements

## 1. Technical Stack

### Core Technologies
- **Python Version**: 3.11+
- **GUI Framework**: PySide6
  - Rationale: Long-term Qt support, cross-platform compatibility, future-proof for Windows OS upgrades
- **Database**: SQLite 3
- **PDF Generation**: ReportLab
- **Excel Export**: openpyxl
- **Password Hashing**: Argon2 (argon2-cffi library)

### Development Environment
- Windows 10/11 primary target
- Support for future Windows versions through PySide6's Qt abstraction layer

---

## 2. Database & File Storage

### Database Location
- **Default**: `%APPDATA%/ChurchDirectory/church_directory.db`
- **Configurable**: Admin/Super Admin can change location via settings
- **Backup Location**: User-selectable, defaults to `%USERPROFILE%/Documents/ChurchDirectory/Backups`

### Image Storage
- **Location**: `%APPDATA%/ChurchDirectory/photos/` (or relative to DB location)
- **Format**: Original files (JPEG, PNG) stored with unique names
- **Database**: Stores relative file paths only
- **Super Admin**: Can reconfigure photo storage location in settings
- **Validation**: Image format verification before saving

### Backup Strategy
- **Built-in Backup** (Primary method):
  - Accessible to Admin and Super Admin
  - Creates timestamped ZIP containing:
    - SQLite database file
    - Photos folder
    - Configuration files
  - Scheduled backups (weekly, configurable)
  - Manual backup on-demand
- **Manual Backup** (Secondary):
  - Users can copy DB and photo folders manually
  - Not officially supported but not prevented

---

## 3. User Management

### Initial Setup Wizard
First launch triggers setup wizard:

1. **Welcome Screen**
   - Brief app introduction
   - Privacy notice

2. **Create Super Admin Account**
   - Username (3-50 characters)
   - Password (meets policy below)
   - Confirm password
   - Generate recovery code:
     - 20-character alphanumeric code
     - Displayed once, user must save it
     - Stored as hashed value in DB

3. **Basic Configuration**
   - Select DB location (optional)
   - Select photo storage location (optional)
   - Import header image for PDF exports (optional, can be done later)

4. **Initial Prayer Groups** (Optional)
   - Create 1-3 prayer groups with names and colors
   - Can be skipped and done later

5. **Completion**
   - Summary of setup
   - Launch application

### Password Policy
- **Minimum length**: 10 characters
- **Required elements**:
  - At least 1 uppercase letter (A-Z)
  - At least 1 lowercase letter (a-z)
  - At least 1 digit (0-9)
  - At least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
- **Blacklist**: Common passwords blocked (password, 123456, qwerty, etc.)
- **Storage**: Argon2 hashed with salt (never plain text)

### Password Reset

#### For Regular Users (View-Member, Add-Member, Admin)
- **Admin-mediated reset**:
  - Super Admin can reset any user's password
  - Admin can reset View-Member and Add-Member passwords
  - Process:
    1. User contacts admin in person
    2. Admin verifies identity
    3. Admin generates temporary password
    4. User must change password on next login
  - All resets logged in audit log

#### For Super Admin
- **Recovery code method**:
  - Super Admin enters recovery code from initial setup
  - If code matches, set new password
  - Recovery code can be regenerated (invalidates old code)
- **Security question** (optional alternative):
  - Set during initial setup
  - Answer stored as hashed value
  - Less secure, but acceptable for offline church context
- All Super Admin password resets logged in audit log

---

## 4. Prayer Group Management

### Color Selection
- **Default Mode**: Predefined palette of gentle, soothing colors
  - Light pastels: soft blues, greens, lavenders, peaches, creams
  - 20-30 predefined colors
  - Prevents poor color choices
- **Advanced Mode**: Free color selection
  - Enabled by Super Admin in settings
  - Opens full RGB color picker
  - When enabled, predefined palette is disabled
- **Uniqueness**: No two active prayer groups can have identical colors
- **Color Usage**:
  - Family card background
  - Empty space around 160×120 photo box
  - Sidebar group label background

### Prayer Group Fields
- Group name (unique, 50 characters max)
- Background color (hex code)
- Created date
- Active status (can be deactivated, not deleted)

---

## 5. Search Functionality

### Search Behavior
- **Simultaneous results**: All matching families shown in sidebar list
- **Search across**:
  - Family name
  - Member names
  - Email addresses
  - Phone numbers
  - Parish names
- **Real-time filtering**: Results update as user types
- **Deleted families**:
  - Hidden by default for all users
  - Visible to Admin/Super Admin when "Show deleted" toggle is enabled
  - Deleted families appear in search results only when toggle is on

### Search UI
- Prominent search box at top of sidebar
- Clear button (X) to reset search
- Result count displayed
- No results message when applicable

---

## 6. Export Specifications

### PDF Exports

#### Family Card PDF
- **Header**: Custom JPG/PNG image (imported by admin)
  - Position: Top of page
  - Max height: 1.5 inches
  - Centered
- **Content**:
  - Family photo (160×120 proportions maintained)
  - Family details (name, addresses, parish, prayer group)
  - Active members table
  - Departed members (optional, checkbox in export dialog)
- **Styling**:
  - Font: Helvetica/Arial family
  - Margins: 0.75 inches all sides
  - Footer: Page number, export date

#### Directory PDF (Admin only)
- Card-style layout, one family per page
- Same format as individual family card
- Optional: Include deleted families
- Progress bar during generation

#### Events PDF (Admin only)
- Birthdays/anniversaries by week or month
- Tabular format with names, dates, ages
- Grouped by prayer group (optional)

### Excel Exports

#### Family List (Super Admin)
- **Format**: .xlsx (single worksheet)
- **Columns**:
  - Family ID
  - Family Name
  - Prayer Group Name
  - Parish
  - Current Address
  - Home Address
  - Number of Active Members
  - Number of Departed Members
- **Sorting**: Alphabetical by family name
- **Filtering**: Include/exclude deleted families

#### Complete Data Export (Super Admin)
- **Format**: .xlsx (multiple worksheets)
- **Worksheets**:
  1. Families (all fields)
  2. Members (all fields)
  3. Departed Members (all fields)
  4. Prayer Groups (all fields)
  5. Users (username, role, created date only - no password hashes)
- **Purpose**: Full backup, import to other tools
- **Security**: Warn user about sensitive data

#### Audit Log Export (Super Admin)
- **Format**: .xlsx or .pdf
- **Columns**:
  - Timestamp
  - Username
  - Role
  - Action
  - Target Table
  - Target ID
  - Details Summary
- **Filtering**: Date range, user, action type
- **Date Range**: Last 365 days only

---

## 7. Member & Family Data Structure

### Family Fields
- **Family name** (required, 100 characters)
- **Current address** (500 characters)
- **Home address** (500 characters)
- **Parish** (100 characters)
- **Prayer group** (required, dropdown)
- **Photo path** (relative path to image file)
- **Timestamps**: Created, updated, deleted dates
- **Soft delete flag**

### Member Fields
- **Name** (required, 100 characters)
- **Relation to family** (required, dropdown):
  - Head of Family (HOF)
  - Spouse
  - Child (Son/Daughter)
  - Parent
  - Sibling
  - Other
- **Date of Birth** (required, date picker)
- **Date of Marriage** (optional, date picker, NULL if unmarried)
- **Profession** (100 characters)
- **Email** (optional but unique if provided, 100 characters)
- **Phone** (20 characters, format: +91-XXXXXXXXXX)
- **Is Head of Family** (boolean, exactly one per family)
- **Timestamps**: Created, updated, deleted dates
- **Soft delete flag**

### Departed Member Fields
- **Name** (required, 100 characters)
- **Relation** (required, same dropdown as members)
- **Date of Birth** (optional)
- **Date of Death** (required)
- **Notes** (optional, 500 characters - burial location, etc.)
- **Timestamps**: Created, updated

### Validation Rules
- At least one member must be marked as Head of Family
- Email must be unique across all active members (NULL emails not checked)
- Email format: basic regex validation (xxx@yyy.zzz)
- Phone format: optional formatting assistance
- DOB cannot be in the future
- DOD cannot be before DOB
- DOM cannot be before DOB

---

## 8. Multi-Step Add/Edit Wizard

### Step 1: Family Information
- **Fields**:
  - Family name (required)
  - Current address (optional but recommended)
  - Home address (optional)
  - Parish (required, dropdown from existing + "Add new")
  - Prayer group (required, dropdown)
- **Validation**:
  - Family name: 1-100 characters
  - No duplicate family names in same prayer group (warning, not error)
- **Navigation**: Next button enabled only when required fields filled

### Step 2: Add Members
- **Interface**: Editable table/form
- **Actions**:
  - Add Member button (opens member form)
  - Edit Member (inline or dialog)
  - Delete Member (removes from list before submission)
- **Member Form**:
  - All fields from Member structure above
  - HOF checkbox (radio button behavior - only one HOF)
  - Email duplication check on blur
- **Validation**:
  - At least one member required
  - Exactly one HOF required
  - All required member fields filled
- **Display**: List of added members shown in table
- **Navigation**: Next enabled when at least one valid member with HOF

### Step 3: Add Departed Members (Optional)
- **Interface**: Similar to Step 2, optional section
- **Actions**:
  - Add Departed Member
  - Edit Departed Member
  - Remove from list
- **Validation**:
  - All required departed member fields filled
  - DOD after DOB (if both provided)
- **Skip**: User can proceed without adding departed members
- **Navigation**: Next always enabled (section is optional)

### Step 4: Photo Upload
- **File chooser**: Opens file dialog (JPEG, PNG only)
- **Validation sequence**:
  1. Verify file is valid image format
     - If invalid: Error message, return to file chooser
  2. Check image dimensions
     - If < 160×120 (width OR height):
       - Show warning popup:
         - "The selected image is smaller than the minimum recommended size (160×120 pixels). The image quality may be reduced when displayed."
         - Buttons: "Choose Another Image" | "Continue with This Image"
       - If "Continue": Accept image (will be upscaled)
       - If "Choose Another": Return to file chooser
- **Preview**:
  - Show image in 160×120 box
  - Prayer group background color fills empty space (letterbox/pillarbox)
  - "Remove Photo" button to clear selection
- **Optional**: Photo can be skipped (placeholder image used)
- **Navigation**: Next always enabled

### Step 5: Review & Submit
- **Display**: Read-only summary of all entered data
  - Family details
  - Members list (table format)
  - Departed members list (if any)
  - Photo thumbnail
- **Actions**:
  - Edit buttons for each section (returns to respective step)
  - Submit button
  - Cancel button (confirms before discarding all data)
- **On Submit**:
  1. Begin transaction
  2. Insert family record
  3. Save photo file (if provided)
  4. Insert member records
  5. Insert departed member records (if any)
  6. Commit transaction
  7. Log action in audit log
  8. Show success message
  9. Navigate to new family's card view
- **On Error**:
  - Rollback transaction
  - Show error message
  - Allow user to retry or go back

### Edit Mode Differences
- Wizard used for both Add (Add-Member role) and Edit (Admin/Super Admin)
- Edit mode:
  - Pre-fills all existing data
  - "Save Changes" instead of "Submit"
  - Can delete individual members (soft delete)
  - Can mark family as deleted (soft delete)
  - Changes logged in audit log with before/after values

---

## 9. Notifications Panel

### Birthday Notifications
- **Date Range**: Current week (Sunday - Saturday)
- **Display**:
  - Member name
  - Age turning
  - Date (day of week)
  - Family name
- **Navigation**: Week selector (Previous/Next buttons)
- **Sorting**: Chronological within week

### Anniversary Notifications
- **Type**: Wedding anniversaries only
- **Date Range**: Current week (Sunday - Saturday)
- **Display**:
  - Couple names (HOF and spouse)
  - Years married
  - Date (day of week)
  - Family name
- **Data Source**: Member.date_of_marriage field
- **Navigation**: Same week selector as birthdays

### UI Layout
- Split panel: Birthdays (top), Anniversaries (bottom)
- Background color: Follows currently selected family's prayer group color
- Empty state: "No birthdays/anniversaries this week"

---

## 10. Soft Delete Behavior

### Family Soft Delete (Admin/Super Admin only)
- **Trigger**: "Soft Delete Family" button on family card
- **Confirmation**: Dialog with warning and reason input (optional)
- **Actions**:
  1. Set family.is_deleted = TRUE
  2. Set family.deleted_at = current timestamp
  3. Set is_deleted = TRUE for all members of family
  4. Set deleted_at for all members
  5. Log action in audit log (includes reason if provided)
- **Effect**:
  - Family hidden from standard navigation
  - Family hidden from searches (unless "Show deleted" enabled)
  - Family hidden from exports (unless "Include deleted" checked)
- **Departed members**: Not soft-deleted (remain visible in family card if restored)

### Member Soft Delete (Admin/Super Admin only)
- **Trigger**: Delete button next to individual member in edit mode
- **Validation**: Cannot delete the only HOF (must reassign HOF first)
- **Actions**:
  1. Set member.is_deleted = TRUE
  2. Set member.deleted_at = current timestamp
  3. Log action in audit log
- **Effect**:
  - Member hidden from family card
  - Member not counted in statistics
  - Member hidden from exports (unless "Include deleted" checked)

### Restore Deleted Records (Admin/Super Admin only)
- **Access**: Admin dashboard > Manage Deleted Records
- **UI**: List of deleted families and individual members
- **Filters**: Date deleted, prayer group, deleted by user
- **Actions**:
  - Restore button (sets is_deleted = FALSE, clears deleted_at)
  - Permanently delete button (only Super Admin, requires confirmation)
- **Family Restore**: Restores family and all its soft-deleted members
- **Member Restore**: Restores individual member only
- **Logging**: All restore actions logged in audit log

---

## 11. System Health & Monitoring

### Health Snapshots (Periodic)
- **Frequency**: Every 4 hours while app is running
- **Metrics Captured**:
  - CPU usage: Average over last 60 seconds
  - Database file size
  - Photo storage total size
  - Audit log table size
  - Total families (active)
  - Total members (active)
  - Active users (logged in within last 30 days)
- **Storage**: SystemHealth table (retain last 180 days, auto-purge older)

### Storage Warnings
- **Main Storage Check**: On app launch and before large operations
- **Threshold**: Warn if drive has < 10% free space
- **Warning Dialog**:
  - "Low disk space detected on [Drive]. Consider freeing up space or moving database to another location."
  - Options: Continue | Change DB Location | Exit
- **No database size limit**: App only warns about drive space, not DB size itself

### Crash Reporting
- **Automatic Generation**: On unhandled exceptions
- **Captured Data**:
  - Timestamp
  - Error type and message
  - Full stack trace
  - User action history (last 10 actions with timestamps)
  - App version
  - OS version
  - Current user role
  - Current view/screen
- **Storage**: CrashReports table (retain last 100 crashes)
- **Privacy**: No personally identifiable family data included
- **Super Admin Access**:
  - View crash report list
  - View full crash details
  - Export crash log as text file

### Super Admin Console - System Health View
- **Dashboard Display**:
  - Current metrics (latest snapshot)
  - Storage breakdown (pie chart):
    - Database structure
    - Photo storage
    - Audit logs
    - Crash reports
  - Historical chart (last 30 days):
    - DB size growth
    - Photo storage growth
- **Actions**:
  - Manual snapshot trigger
  - Export health history (Excel)
  - Clear old snapshots manually

---

## 12. Audit Logging

### Logged Actions
- **User Actions**:
  - Login/logout
  - Password changes
  - Password resets (by admin)
- **Data Actions**:
  - Add family/member/departed member
  - Edit family/member/departed member
  - Soft delete family/member
  - Restore deleted records
  - Permanently delete (Super Admin only)
- **System Actions**:
  - Export directory PDF
  - Export data to Excel
  - Backup creation
  - Backup restoration
  - Settings changes (DB location, color palette mode, etc.)
  - Prayer group creation/editing

### Log Entry Structure
- Timestamp
- User ID and username
- User role at time of action
- Action type (login, add, edit, delete, restore, export)
- Target table (families, members, departed_members, prayer_groups, users)
- Target ID (record ID affected)
- Details JSON:
  - For edits: Before and after values (limited to changed fields)
  - For deletes: Reason (if provided)
  - For exports: File type, filters applied
  - For system actions: Relevant parameters

### Log Retention
- **Retention Period**: 365 days (rolling)
- **Circular Log Behavior**:
  - When log table exceeds capacity (disk space or 365 days):
    - Oldest entries automatically deleted
    - New entries appended
  - Super Admin can manually purge logs older than X days
- **Capacity Management**:
  - Daily cleanup job: Delete logs older than 365 days
  - Warn Super Admin if log table exceeds 500 MB

### Super Admin Audit View
- **Filters**:
  - Date range (with presets: Today, Last 7 days, Last 30 days, Last 365 days)
  - User (dropdown of all users)
  - Action type (dropdown)
  - Target table (dropdown)
- **Display**: Paginated table (50 entries per page)
- **Actions**:
  - View full details (expands JSON in dialog)
  - Export filtered logs (Excel or PDF)
  - Export all logs (last 365 days)

---

## 13. Localization Planning

### Phase 1 (Current): English Only
- All UI strings in English
- Date formats: MM/DD/YYYY (US) or DD/MM/YYYY (configurable)
- Currency: Not applicable
- Number formats: Standard

### Phase 2 (Future): Malayalam Support
- **Architecture**:
  - Use Qt's translation system (.ts files)
  - All UI strings externalized to translation files
  - Language selection in settings (Super Admin)
- **Considerations**:
  - Right-to-left support not needed (Malayalam is LTR)
  - Font support: Ensure PySide6 can render Malayalam Unicode
  - PDF exports: ReportLab must support Unicode fonts
  - Database: Already UTF-8, no changes needed
- **Scope**:
  - UI labels, buttons, menus
  - System messages and errors
  - PDF headers and labels
  - User-entered data remains in entered language (mixed content OK)

---

## 14. Role Permissions Matrix

| Permission | View-Member | Add-Member | Admin | Super Admin |
|------------|-------------|------------|-------|-------------|
| View families/members | ✓ | ✓ | ✓ | ✗ |
| Search directory | ✓ | ✓ | ✓ | ✗ |
| Export family card PDF | ✓ | ✓ | ✓ | ✗ |
| View notifications | ✓ | ✓ | ✓ | ✗ |
| Add new family/members | ✗ | ✓ | ✓ | ✗ |
| Edit existing data | ✗ | ✗ | ✓ | ✗ |
| Soft delete family/member | ✗ | ✗ | ✓ | ✗ |
| Restore deleted records | ✗ | ✗ | ✓ | ✗ |
| Manage prayer groups | ✗ | ✗ | ✓ | ✓ |
| Export directory PDF | ✗ | ✗ | ✓ | ✗ |
| Export events PDF | ✗ | ✗ | ✓ | ✗ |
| View deleted records | ✗ | ✗ | ✓ | ✓ |
| Backup/restore database | ✗ | ✗ | ✓ | ✓ |
| Manage users | ✗ | ✗ | ✗ | ✓ |
| Export family list Excel | ✗ | ✗ | ✗ | ✓ |
| Export complete data Excel | ✗ | ✗ | ✗ | ✓ |
| View audit logs | ✗ | ✗ | ✗ | ✓ |
| Export audit logs | ✗ | ✗ | ✗ | ✓ |
| View system health | ✗ | ✗ | ✗ | ✓ |
| View crash reports | ✗ | ✗ | ✗ | ✓ |
| Change settings | ✗ | ✗ | Limited | Full |
| Reset user passwords | ✗ | ✗ | Limited | All users |

**Notes**:
- Super Admin deliberately has NO data viewing access (no family cards, no member details)
- Super Admin operates through console: reports, exports, system management only
- Admin has "limited" settings access: Backup location, PDF header image, but not DB location or color palette mode
- Admin can reset passwords for View-Member and Add-Member roles only

---

## 15. UI/UX Specifications

### Color Scheme (Default)
- **Predefined Palette** (for prayer groups):
  - Soft Blue: #E3F2FD
  - Mint Green: #E8F5E9
  - Lavender: #F3E5F5
  - Peach: #FFE0B2
  - Cream: #FFF8E1
  - Rose: #FCE4EC
  - Sky Blue: #E1F5FE
  - Pale Yellow: #FFFDE7
  - Light Coral: #FFEBEE
  - Aqua: #E0F2F1
  - (Plus 10-20 more gentle pastels)

### Typography
- **Primary Font**: Segoe UI (Windows default), fallback to Arial
- **Sizes**:
  - Headings: 16pt bold
  - Body text: 10pt regular
  - Labels: 9pt regular
  - Buttons: 10pt semi-bold
- **PDF Font**: Helvetica (standard, widely supported)

### Spacing & Layout
- **Margins**: 10-15px standard padding
- **Card padding**: 20px
- **Button spacing**: 8px between buttons
- **Form field spacing**: 12px vertical between fields
- **Sidebar width**: 250px (resizable 200-350px)
- **Notifications panel width**: 300px (resizable 250-400px)
- **Main content**: Flexible, takes remaining space

### Icons
- Use Qt's standard icons where possible
- Custom icons for:
  - Prayer groups (church/people icon)
  - Birthdays (cake icon)
  - Anniversaries (rings icon)
  - Departed members (cross/memorial icon)

### Responsive Behavior
- Minimum window size: 1024×768
- Panels resizable via splitters
- Table columns auto-size with horizontal scroll if needed
- Forms scroll vertically if content exceeds window height

---

## 16. Error Handling

### User-Facing Errors
- **Database Errors**:
  - "Unable to connect to database. Please check if the database file exists and is not corrupted."
  - Offer: Retry | Choose Different DB | Exit
- **File I/O Errors**:
  - "Cannot save photo: [reason]"
  - "Cannot access backup location: [reason]"
- **Validation Errors**:
  - Highlight offending field in red
  - Show specific message below field (e.g., "Email format invalid")
- **Permission Errors**:
  - "You do not have permission to perform this action."
  - Display role requirement if helpful

### System Errors
- **Unhandled Exceptions**:
  - Caught by global exception handler
  - Show apologetic error dialog
  - Generate crash report
  - Offer: Continue | Restart App | Exit
- **Data Corruption**:
  - Detect on app launch (integrity check)
  - Offer: Restore from Backup | Attempt Repair | Contact Support

### Logging
- **Application Log** (separate from audit log):
  - Stored in: `%APPDATA%/ChurchDirectory/logs/app.log`
  - Rotation: Daily, keep last 30 days
  - Content:
    - Errors and warnings
    - Database queries (debug level only)
    - File operations
    - Network operations (future phase)
  - Access: Super Admin can export in crash report context

---

## 17. Security Considerations

### Current (Offline) Security
- **Database Encryption**: Not implemented (SQLite file is plain)
  - Rationale: Offline use, physical access controlled, encryption adds complexity
  - Future: Consider SQLCipher if data sensitivity increases
- **Password Storage**: Argon2 hashed (strong)
- **File Permissions**: Standard OS file permissions (no custom ACLs)
- **Session Management**: Simple user state, no timeout (desktop app)
- **Backup Security**: Backups are unencrypted (user responsible for storage location)

### Future (Internet-Connected) Considerations
- Database encryption (SQLCipher)
- Session timeouts (auto-logout after inactivity)
- TLS for network communication
- Multi-factor authentication (optional)
- More robust audit logging with IP addresses
- Encrypted backups with user-provided password

### Data Privacy
- No telemetry or analytics
- No external network calls (except future online sync)
- Photos stored locally only
- User data never transmitted

---

## 18. Performance Targets

### Startup Time
- Cold start: < 3 seconds
- Warm start: < 1 second

### Database Operations
- Load family card: < 100ms
- Search: < 200ms for 1000+ families
- Add family: < 300ms (including photo save)
- Export directory PDF: < 5 seconds for 100 families

### Export Operations
- Family list Excel: < 2 seconds for 500 families
- Complete data Excel: < 5 seconds for 500 families + 2000 members
- Audit log Excel: < 3 seconds for 365 days

### Memory Usage
- Base app: < 50 MB
- With 500 families (images loaded): < 200 MB
- Target: Smooth operation on 4 GB RAM Windows 11 machine

---

## 19. Development Constraints

### Must Have (Phase 1)
- All core features as described
- Windows 10/11 support
- English UI
- Basic error handling
- User manual (PDF)

### Should Have (Phase 1)
- Keyboard shortcuts
- Inline help tooltips
- Settings validation
- Backup scheduling

### Could Have (Phase 1)
- Advanced search filters (date ranges, etc.)
- Custom report templates
- Batch member import (CSV)

### Won't Have (Phase 1)
- Malayalam localization (Phase 2)
- Online sync
- Mobile companion app
- Email notifications

---

## 20. Testing Requirements

### Unit Tests
- Database CRUD operations
- Password hashing/verification
- Image validation and processing
- Export generation (PDF, Excel)
- Search algorithms
- Soft delete logic

### Integration Tests
- Full wizard workflows (add, edit)
- Backup and restore
- User authentication and authorization
- Audit log generation

### UI Tests
- Navigation and layout
- Dialog workflows
- Error message display
- Export dialogs

### User Acceptance Testing
- Test with actual church staff (3-5 users)
- Test scenarios:
  - Add 50 families with photos
  - Search and filter
  - Generate exports
  - Simulate errors (corrupt DB, missing photos)
- Feedback collection and iteration

---

## Appendix A: Database Indexes

```sql
-- Performance indexes
CREATE INDEX idx_families_deleted ON Families(is_deleted);
CREATE INDEX idx_families_prayer_group ON Families(prayer_group_id);
CREATE INDEX idx_members_family ON Members(family_id);
CREATE INDEX idx_members_deleted ON Members(is_deleted);
CREATE INDEX idx_members_email ON Members(email);
CREATE INDEX idx_departed_family ON DepartedMembers(family_id);
CREATE INDEX idx_audit_timestamp ON AuditLog(timestamp);
CREATE INDEX idx_audit_user ON AuditLog(user_id);
CREATE INDEX idx_audit_action ON AuditLog(action);
```

## Appendix B: Sample Data

Provided in separate SQL script for development and testing.

---

**Document Version**: 2.0  
**Last Updated**: December 31, 2024  
**Author**: Development Team  
**Status**: Ready for Development