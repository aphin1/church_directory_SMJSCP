# Requirements Updates Summary

## All Changes Incorporated ✅

Below is a comprehensive list of all updates made to the requirements document based on your suggestions:

---

## 1. ✅ Soft Delete with Mandatory Reason

### What Changed:
- **All soft delete operations** (families, members, departed members) now require a **mandatory reason field**
- Reason must be 10-500 characters
- Deletion cannot proceed without entering a reason
- Reason is stored in the record and audit log

### Impact:
- Better audit trail for deletions
- Accountability for all delete actions
- Helps with future review/restoration decisions

**Implementation Notes:**
- Add `deletion_reason` column to Families, Members, DepartedMembers tables
- Update delete dialogs with mandatory text area
- Validate reason length before allowing deletion

---

## 2. ✅ Photo Aspect Ratio - No Stretching

### What Changed:
- Photos are **never stretched** to fit the 160×120 box
- Images maintain their **original aspect ratio**
- Empty space (letterbox/pillarbox) is filled with **transparent background** that shows the prayer group color
- If aspect ratio doesn't match 4:3, image fits according to its actual proportions

### Previous Behavior:
- Empty space was filled with solid prayer group color
- Could potentially stretch images

### New Behavior:
- Scale image to fit while preserving exact aspect ratio
- Use transparency for empty areas
- Background color shows through transparent areas

**Implementation Notes:**
- Use Qt's `Qt.KeepAspectRatio` with `Qt.SmoothTransformation`
- Set transparent background on QLabel/QPixmap
- Prayer group color applied to container, not image

---

## 3. ✅ Field Renamed: "Family Name" → "Head of Family Name (Family Name)"

### What Changed:
- Field label now reads: **"Head of Family Name (Family Name)"**
- Makes it clear the family is identified by the head of family's name
- More culturally appropriate for church context

### Impact:
- Clearer understanding of what name to enter
- Reduces confusion about family naming conventions

**Implementation Notes:**
- Update all UI labels
- Update database column comment/documentation
- Update exports and PDFs to use new terminology

---

## 4. ✅ Gender Field Added (Hidden from Main Views)

### What Changed:
- **New required field**: Gender (Male/Female/Other)
- Added to both **Members** and **Departed Members**
- **Visible during**:
  - Add member wizard
  - Edit member dialog
  - Admin views
  - Exports (Excel, PDF)
- **Hidden in**:
  - Main family card view (regular users)
  - Member lists in navigation
  - Notifications panel

### Purpose:
- Demographic data collection
- Useful for reports and analysis
- Privacy-sensitive, so hidden from casual viewing

**Implementation Notes:**
- Add `gender` column to Members and DepartedMembers tables
- Add dropdown in member form (Male/Female/Other)
- Apply visibility rules based on context and user role
- Include in export data

---

## 5. ✅ International Phone Numbers

### What Changed:
- Phone field now accepts **international format**: `+XX-XXXXXXXXXX`
- Maximum length increased to **30 characters** (was 20)
- Validation updated to support country codes

### Examples:
- India: `+91-9876543210`
- USA: `+1-555-123-4567`
- UK: `+44-20-7123-4567`

**Implementation Notes:**
- Update phone field max length to 30
- Add international phone regex validation
- Update UI placeholder text to show format
- Consider using libphonenumber library for validation (optional)

---

## 6. ✅ Soft Delete Flag Visibility

### What Changed:
- Soft delete flag/status is now **visible to Admin and Super Admin only**
- Regular users (Add-Member) never see delete status
- Admin views show badge or indicator for deleted records

### Previous Behavior:
- Not explicitly specified

### New Behavior:
- Deleted records show "Deleted" badge in Admin views
- Include deletion date and reason when viewing details
- Regular users see clean interface without delete indicators

**Implementation Notes:**
- Add role-based visibility checks
- Display "Deleted" badge with red color in Admin views
- Show deletion metadata on hover or in details panel

---

## 7. ✅ Family Name Minimum 3 Characters

### What Changed:
- Family name minimum length: **3 characters** (was 1)
- Helps ensure meaningful family names
- Prevents accidental single-letter entries

**Implementation Notes:**
- Update validation to check `len(family_name) >= 3`
- Show error message: "Family name must be at least 3 characters"
- Apply to both add and edit operations

---

## 8. ✅ Duplicate Family Name Handling

### What Changed:
- When a duplicate family name is entered:
  1. **Warning popup** appears: "A family with this name already exists. Do you want to proceed?"
  2. Buttons: "Change Name" | "Proceed Anyway"
  3. If "Proceed Anyway":
     - Family is created
     - **Notification sent to Admin**: "Duplicate family name detected: [Name]. Review families with ID [ID1] and [ID2]."
     - Admin dashboard shows **alert card** with:
       - Both family IDs and names
       - Options: "View Families" | "Keep Both" | "Delete One"
     - If "Delete One": Opens soft delete dialog with reason
- **New table**: `DuplicateFamilyAlerts` to track these cases

### Purpose:
- Prevents accidental duplicates while allowing legitimate ones (e.g., multiple "Abraham" families)
- Admin oversight for data quality
- Non-blocking for data entry

**Implementation Notes:**
- Check for duplicate names on form submission
- Create alert record in DuplicateFamilyAlerts table
- Admin dashboard widget to show unresolved alerts
- Notification system to alert Admin users

---

## 9. ✅ Anniversary Notification - Spouse Selection for In-Laws

### What Changed:
- When adding a **Son-in-law** or **Daughter-in-law**:
  - Additional field appears: **"Spouse"** (dropdown)
  - Dropdown populated with family's **son/daughter names**
  - Links the in-law to the family member
- Used for **anniversary notifications**:
  - Shows: "John (Son) & Mary (Daughter-in-law)"
  - Correctly identifies couples for anniversary tracking

### Previous Behavior:
- No mechanism to link in-laws to family members
- Anniversary notifications unclear for in-law marriages

**Implementation Notes:**
- Add `spouse_member_id` column to Members table (foreign key to member_id)
- Show spouse dropdown only when relation is "Son-in-law" or "Daughter-in-law"
- Filter dropdown to show only sons/daughters of the family
- Update anniversary notification logic to use spouse link

---

## 10. ✅ Departed Members Can Be Soft-Deleted

### What Changed:
- Departed members can now be **soft-deleted** with mandatory reason
- Previously, departed members couldn't be deleted
- Useful for correcting data entry errors

### Workflow:
1. Admin clicks delete button on departed member
2. Dialog appears with mandatory reason field
3. Departed member is soft-deleted (is_deleted = TRUE)
4. Can be restored by Admin/Super Admin

**Implementation Notes:**
- Add `is_deleted`, `deleted_at`, `deletion_reason` to DepartedMembers table
- Add delete button in departed members section (Admin only)
- Implement soft delete logic similar to members
- Add restore option in Admin dashboard

---

## 11. ✅ Change Password for All Users

### What Changed:
- **All users** can change their own password
- Located in: **Settings > Change Password** or user menu
- Workflow:
  1. Enter current password
  2. Enter new password (must meet policy)
  3. Confirm new password
  4. Submit to change

### User Roles That Can Change Password:
- Add-Member ✅
- Admin ✅
- Super Admin ✅

### Separate from Password Reset:
- Password reset = Admin/Super Admin resets another user's password
- Password change = User changes their own password

**Implementation Notes:**
- Add "Change Password" menu item/button
- Create change password dialog
- Validate current password before allowing change
- Enforce password policy on new password
- Log password change in audit log

---

## 12. ✅ Audit Log Deletion Tracking

### What Changed:
- Audit log now tracks **how logs were deleted**:
  - **"Auto-deleted by system"** - When logs older than 365 days or exceeding 500MB are automatically purged
  - **"Deleted by Super Admin: [username]"** - When Super Admin manually purges logs
- New field: `deletion_method` in AuditLog table

### Purpose:
- Transparency in log management
- Distinguish between automatic cleanup and manual purging
- Accountability for manual deletions

**Implementation Notes:**
- Add `deletion_method` column to AuditLog table
- Update automatic cleanup job to mark deletion method
- Update manual purge function to include username
- Show deletion method in audit log viewer

---

## 13. ✅ Audit Log Size: 500MB Sufficient?

### Answer: Yes, 500MB is adequate

**Why 500MB is enough:**
- Typical audit log entry: 500 bytes to 2KB (includes JSON details)
- **500MB ≈ 250,000 to 1,000,000 log entries**
- For a church with 500 families:
  - ~10-50 actions per day = 3,650-18,250 entries per year
  - **500MB can store 15-100+ years of logs**
- With 365-day retention, space usage will be much lower (typically 5-50MB)

### Monitoring:
- Warn Super Admin when log size reaches 450MB (90% threshold)
- Automatic cleanup prevents exceeding 500MB
- Circular log behavior ensures oldest entries removed first

**Decision: Keep 500MB limit as specified**

---

## 14. ✅ Date Format: DD/MM/YYYY with Optional Year

### What Changed:
- **Data Entry Format**: DD/MM/YYYY
- **Year is optional** across all date fields in application:
  - Date of Birth (DOB)
  - Date of Death (DOD)
  - Date of Marriage (DOM)
- If year is omitted, stored as NULL in database

### Database Storage:
- Store day/month as DATE type or separate columns
- Store year in separate `year` column (INT, nullable)
- Examples:
  - `date_of_birth` = '15-03' (March 15)
  - `birth_year` = 1975 (or NULL if not provided)

### Display Rules:
- **Add-Member/View Access (Regular Users)**:
  - Active Members page: Shows **DD/MM only** (no year, no age)
  - Example: "Birthday: 15/03"
- **Admin Page**:
  - Shows **full DD/MM/YYYY and calculated age**
  - Example: "Birthday: 15/03/1975 (49 years old)"

### Purpose:
- Privacy for regular users
- Flexibility for incomplete historical data
- Cultural sensitivity (some people prefer not to share age)

**Implementation Notes:**
- Create separate date and year columns
- Update date picker UI to make year optional
- Add role-based logic for displaying year and age
- Update all date displays throughout app
- Handle NULL years in age calculations

---

## 15. ✅ Email-Based Access Control (Replaces View-Member Role)

### What Changed:
- **View-Member role eliminated** completely
- **Email-based access** system:
  - Add-Member users must have email in Members table
  - Any email in Members table can view data (automatic view access)
  - No separate user role needed for viewing

### New User Creation Workflow:

#### Add-Member User Creation (by Admin):
1. Admin creates new Add-Member user
2. Required fields:
   - **New user's email** (must exist in Members table)
   - **Reference person's email** (existing member who vouches)
   - Password
3. Validation:
   - New email must be in Members table
   - Reference email must be in Members table
   - Neither can be admin email
   - Both must be unique (not already user accounts)
4. Result:
   - User can login with email
   - Can add new families/members
   - Can view data (email is in Members table)

### Access Control Rules:
- **Admin Email**: Separate from member emails, cannot be reused
- **Add-Member Email**: Must be in Members table
- **View Access**: Automatic for any email in Members table
- **Email Uniqueness**: Enforced across all members

### Database Changes:
- Users table:
  - Change `username` to `email` (primary identifier)
  - Add `reference_email` field (for Add-Member users)
  - Remove "View-Member" from role enum

**Benefits:**
1. Simplified role management (only 3 roles now)
2. Email serves as both identifier and access token
3. Reference email creates accountability
4. Automatic view access eliminates configuration
5. All access tied to actual church members

**Implementation Notes:**
- Update Users table schema
- Rewrite authentication to use email
- Implement email validation against Members table
- Add reference email field to user creation form
- Update permission checks throughout app
- Remove all View-Member role references

---

## 16. ✅ Admin Can Only Create Add-Member Users

### What Changed:
- **Admin can only create Add-Member role users**
- Admin **cannot create other Admins or Super Admins**
- Super Admin creates Admin users
- Prevents unauthorized privilege escalation

### Hierarchy:
- **Super Admin** → Creates: Admin, Add-Member
- **Admin** → Creates: Add-Member only
- **Add-Member** → Creates: Nothing (cannot manage users)

**Implementation Notes:**
- Restrict role dropdown in Admin's user creation form
- Show only "Add-Member" option
- Super Admin sees all role options
- Add validation to prevent role manipulation

---

## 17. ✅ Admin Can Disable Add-Member Users

### What Changed:
- Admin can **disable** Add-Member users (soft delete user account)
- Disabled users cannot log in
- Admin can **re-enable** disabled users
- User data remains in database

### Workflow:
1. Admin goes to User Management
2. Selects Add-Member user
3. Clicks "Disable User"
4. User's `is_active` flag set to FALSE
5. User cannot log in until re-enabled

**Implementation Notes:**
- Add "Disable" button in user management
- Set `is_active = FALSE` on disable
- Check `is_active` during login
- Add "Enable" button to re-activate users
- Log disable/enable actions in audit log

---

## 18. ✅ Panel Resizing - Admin Only

### What Changed:
- **Only Admin and Super Admin** can resize panels via splitters
- **Add-Member users** see fixed default layout (no resizable splitters)

### Default Layout for Add-Member:
- Left sidebar: 250px (fixed)
- Right notifications panel: 300px (fixed)
- Center panel: Remaining space

### Resizable for Admin/Super Admin:
- Left sidebar: 200-350px (via splitter)
- Right panel: 250-400px (via splitter)

### Purpose:
- Simpler interface for regular users
- Prevents layout confusion
- Admin users get flexibility they need

**Implementation Notes:**
- Check user role on app launch
- Enable/disable splitter handles based on role
- Save panel sizes in AppSettings (Admin only)
- Restore default sizes for Add-Member users

---

## Summary Statistics

### Total Changes: 18 Major Updates
- **Database Schema**: 8 new/modified columns
- **New Table**: DuplicateFamilyAlerts
- **Role Changes**: View-Member role eliminated
- **New Features**: 6 (gender field, spouse linking, change password, etc.)
- **Enhanced Features**: 8 (soft delete, date format, phone format, etc.)
- **UI Changes**: 4 (panel resizing, visibility rules, etc.)

---

## Next Steps for Development

### Immediate Actions:
1. ✅ **Update Database Schema** - Add all new columns and tables
2. ✅ **Update ERD** - Already done
3. ✅ **Update Requirements Doc** - Already done
4. **Update Wireframe** - Reflect role changes and new fields
5. **Update Roadmap** - Adjust milestones for new features

### Phase 1 Priorities (Weeks 1-2):
1. Database schema implementation
2. Email-based authentication system
3. Soft delete with mandatory reasons
4. Gender field addition
5. Date format handling (DD/MM/YYYY with optional year)

### Testing Priorities:
- Email uniqueness and access control
- Soft delete with reasons
- Duplicate family name detection
- Spouse linking for in-laws
- Date entry with optional year
- Role-based visibility (gender, year/age, soft delete flags)

---

**All requirements have been successfully updated! Ready to proceed with development.** 🚀