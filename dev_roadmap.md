# Church Directory Application - Development Roadmap

## Project Timeline: 12-16 Weeks

---

## Phase 1: Foundation & Setup (Weeks 1-2)

### Milestone 1.1: Development Environment Setup
**Duration**: 2 days

**Tasks**:
- [ ] Install Python 3.11+
- [ ] Set up virtual environment
- [ ] Install PySide6, openpyxl, ReportLab, argon2-cffi
- [ ] Configure IDE (VS Code/PyCharm)
- [ ] Set up Git repository
- [ ] Create project structure:
  ```
  church_directory/
  ├── src/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── database/
  │   ├── ui/
  │   ├── models/
  │   ├── controllers/
  │   ├── utils/
  │   └── exports/
  ├── tests/
  ├── docs/
  ├── resources/
  │   ├── icons/
  │   └── styles/
  └── requirements.txt
  ```

**Deliverables**:
- Working development environment
- Project skeleton with empty modules
- Version control initialized

---

### Milestone 1.2: Database Design & Implementation
**Duration**: 5 days

**Tasks**:
- [ ] Create SQLite schema from design document
- [ ] Write database initialization script
- [ ] Implement database connection manager
- [ ] Create ORM/data access layer:
  - [ ] Users table CRUD
  - [ ] Families table CRUD
  - [ ] Members table CRUD
  - [ ] DepartedMembers table CRUD
  - [ ] PrayerGroups table CRUD
  - [ ] AuditLog table CRUD
  - [ ] CrashReports table CRUD
  - [ ] AppSettings table CRUD
  - [ ] SystemHealth table CRUD
- [ ] Create database indexes
- [ ] Write unit tests for database operations
- [ ] Create sample data script

**Deliverables**:
- Fully functional database layer
- 100% test coverage for CRUD operations
- Sample data for testing

---

### Milestone 1.3: First-Run Setup Wizard
**Duration**: 3 days

**Tasks**:
- [ ] Design wizard UI (5 steps)
- [ ] Implement welcome screen
- [ ] Implement Super Admin creation screen:
  - [ ] Username validation
  - [ ] Password policy enforcement
  - [ ] Recovery code generation
- [ ] Implement configuration screen (DB location, photo storage)
- [ ] Implement initial prayer groups screen (optional)
- [ ] Implement completion screen
- [ ] Write wizard flow logic
- [ ] Test wizard thoroughly

**Deliverables**:
- Functional first-run wizard
- Super Admin account created successfully
- Database and photo directories initialized

**Testing Checklist**:
- [ ] Password policy validation works
- [ ] Recovery code generated and stored securely
- [ ] Database created in correct location
- [ ] Photo directory created
- [ ] Wizard doesn't run on subsequent launches

---

## Phase 2: Authentication & User Management (Weeks 3-4)

### Milestone 2.1: Authentication System
**Duration**: 4 days

**Tasks**:
- [ ] Design login screen UI
- [ ] Implement password hashing (Argon2)
- [ ] Create login controller
- [ ] Implement session management
- [ ] Create user state manager
- [ ] Implement password change functionality
- [ ] Implement password reset (admin-mediated)
- [ ] Implement Super Admin recovery code reset
- [ ] Write authentication unit tests
- [ ] Test various attack scenarios (SQL injection, etc.)

**Deliverables**:
- Secure login system
- Password change functionality
- Password reset functionality
- Session state management

**Testing Checklist**:
- [ ] Passwords hashed with Argon2
- [ ] Login attempts logged in audit log
- [ ] Failed login attempts handled gracefully
- [ ] Session persists correctly
- [ ] Recovery code works for Super Admin

---

### Milestone 2.2: User Management (Super Admin)
**Duration**: 3 days

**Tasks**:
- [ ] Design user management UI
- [ ] Implement user CRUD operations:
  - [ ] Add user (with role selection)
  - [ ] Edit user (change role, deactivate)
  - [ ] Delete user (soft delete)
  - [ ] Reset user password
- [ ] Implement role-based access control (RBAC)
- [ ] Create permission checking decorator/utility
- [ ] Implement user activity tracking
- [ ] Write RBAC unit tests

**Deliverables**:
- User management interface (Super Admin only)
- RBAC system enforcing permissions
- User activity tracking

**Testing Checklist**:
- [ ] Only Super Admin can access user management
- [ ] Roles correctly restrict access to features
- [ ] User creation/editing works correctly
- [ ] Password resets logged in audit log

---

### Milestone 2.3: Audit Logging System
**Duration**: 3 days

**Tasks**:
- [ ] Implement audit log writer utility
- [ ] Create logging decorators for data operations
- [ ] Implement audit log viewer UI (Super Admin):
  - [ ] Paginated list
  - [ ] Filters (date, user, action, table)
  - [ ] Detail view (JSON display)
- [ ] Implement 365-day retention with auto-purge
- [ ] Implement audit log export (Excel, PDF)
- [ ] Write audit logging tests

**Deliverables**:
- Comprehensive audit logging for all actions
- Audit log viewer with filters
- Export functionality
- Automatic old log purging

**Testing Checklist**:
- [ ] All CRUD operations logged
- [ ] Login/logout logged
- [ ] Export operations logged
- [ ] Logs older than 365 days purged automatically
- [ ] Super Admin can view and export logs

---

## Phase 3: Core UI & Navigation (Weeks 5-6)

### Milestone 3.1: Main Window Layout
**Duration**: 4 days

**Tasks**:
- [ ] Design main window with PySide6
- [ ] Implement menu bar:
  - [ ] File menu (Backup, Restore, Exit)
  - [ ] Edit menu (role-dependent)
  - [ ] Tools menu (Settings, Admin Dashboard)
  - [ ] Help menu (About, User Manual)
- [ ] Implement three-panel layout:
  - [ ] Left sidebar (navigation)
  - [ ] Center panel (family card)
  - [ ] Right panel (notifications)
- [ ] Implement resizable splitters
- [ ] Implement status bar
- [ ] Apply basic styling (Qt stylesheet)

**Deliverables**:
- Functional main window with layout
- Menu bar with placeholders
- Resizable panels

---

### Milestone 3.2: Left Sidebar - Navigation
**Duration**: 3 days

**Tasks**:
- [ ] Implement search box with live filtering
- [ ] Implement A-Z family list:
  - [ ] Alphabetical grouping
  - [ ] Click to select family
  - [ ] Active family highlight
- [ ] Implement prayer group section:
  - [ ] Expandable/collapsible groups
  - [ ] Family list per group
  - [ ] Group background colors
- [ ] Implement "Show deleted" toggle (Admin/Super Admin)
- [ ] Write navigation tests

**Deliverables**:
- Fully functional navigation sidebar
- Search with live filtering
- Prayer group navigation

**Testing Checklist**:
- [ ] Search filters families, members, email, phone
- [ ] A-Z list updates when search active
- [ ] Prayer groups show correct families
- [ ] Deleted families hidden by default
- [ ] "Show deleted" toggle works for Admin/Super Admin

---

### Milestone 3.3: Center Panel - Family Card View
**Duration**: 5 days

**Tasks**:
- [ ] Design family card layout
- [ ] Implement family header:
  - [ ] Photo container (160×120)
  - [ ] Family details (name, addresses, parish, prayer group)
- [ ] Implement members table:
  - [ ] Column headers
  - [ ] HOF badge
  - [ ] Responsive layout
- [ ] Implement departed members section (collapsible)
- [ ] Implement action buttons:
  - [ ] Export Card PDF
  - [ ] Edit Members (Admin only)
  - [ ] Soft Delete Family (Admin only)
- [ ] Apply prayer group background color
- [ ] Handle empty state (no family selected)

**Deliverables**:
- Beautiful family card UI
- Role-based button visibility
- Dynamic background color from prayer group

---

### Milestone 3.4: Right Panel - Notifications
**Duration**: 2 days

**Tasks**:
- [ ] Design notifications layout
- [ ] Implement birthday section:
  - [ ] Week selector (prev/next)
  - [ ] Birthday list for current week
  - [ ] Calculate ages
- [ ] Implement anniversary section:
  - [ ] Week selector (prev/next)
  - [ ] Anniversary list for current week
  - [ ] Calculate years married
- [ ] Implement empty states
- [ ] Style notification cards

**Deliverables**:
- Functional notifications panel
- Week navigation
- Birthday and anniversary lists

**Testing Checklist**:
- [ ] Birthdays show for current week (Sun-Sat)
- [ ] Anniversaries show for current week
- [ ] Week navigation updates correctly
- [ ] Empty state when no events
- [ ] Background color follows selected family's prayer group

---

## Phase 4: Data Entry & Editing (Weeks 7-8)

### Milestone 4.1: Multi-Step Add Family Wizard
**Duration**: 6 days

**Tasks**:
- [ ] Design wizard dialog (5 steps)
- [ ] **Step 1**: Family Information
  - [ ] Form fields with validation
  - [ ] Parish dropdown (with "Add new")
  - [ ] Prayer group dropdown
- [ ] **Step 2**: Add Members
  - [ ] Editable table/list
  - [ ] Add member dialog
  - [ ] Email duplication check
  - [ ] HOF validation (exactly one)
- [ ] **Step 3**: Add Departed Members (Optional)
  - [ ] Similar to Step 2
  - [ ] Date validation (DOD > DOB)
- [ ] **Step 4**: Photo Upload
  - [ ] File chooser (JPEG, PNG only)
  - [ ] Image validation
  - [ ] Small image warning popup
  - [ ] Preview with prayer group background
- [ ] **Step 5**: Review & Submit
  - [ ] Read-only summary
  - [ ] Edit buttons to return to steps
  - [ ] Transaction-based submission
- [ ] Implement wizard controller
- [ ] Write wizard integration tests

**Deliverables**:
- Fully functional add family wizard
- Comprehensive validation at each step
- Transaction-based data persistence

**Testing Checklist**:
- [ ] Cannot proceed without required fields
- [ ] Email duplication detected
- [ ] Exactly one HOF enforced
- [ ] Image validation works
- [ ] Small image warning displayed correctly
- [ ] Preview shows image in 160×120 box with background color
- [ ] Submission saves all data atomically
- [ ] Audit log created on submission

---

### Milestone 4.2: Edit Family & Members (Admin)
**Duration**: 4 days

**Tasks**:
- [ ] Reuse add wizard for edit mode
- [ ] Pre-fill all existing data
- [ ] Implement individual member soft delete
- [ ] Implement family soft delete
- [ ] Track before/after values for audit log
- [ ] Validate changes (e.g., cannot remove only HOF)
- [ ] Write edit functionality tests

**Deliverables**:
- Edit mode in wizard
- Soft delete for members and families
- Audit log with before/after values

**Testing Checklist**:
- [ ] Edit wizard pre-fills existing data
- [ ] Changes saved correctly
- [ ] Soft delete sets is_deleted flag
- [ ] Cannot delete only HOF without reassignment
- [ ] Audit log shows before/after values

---

## Phase 5: Prayer Groups & Settings (Week 9)

### Milestone 5.1: Prayer Group Management
**Duration**: 3 days

**Tasks**:
- [ ] Design prayer group management UI
- [ ] Implement CRUD operations:
  - [ ] Add prayer group
  - [ ] Edit prayer group (name, color)
  - [ ] Deactivate prayer group (cannot delete if families assigned)
- [ ] Implement color picker:
  - [ ] Predefined palette mode (default)
  - [ ] Free color selection mode (Super Admin toggle)
  - [ ] Color uniqueness validation
- [ ] Write prayer group tests

**Deliverables**:
- Prayer group management interface
- Color picker with palette/free modes
- Color uniqueness enforcement

---

### Milestone 5.2: Application Settings
**Duration**: 2 days

**Tasks**:
- [ ] Design settings dialog
- [ ] Implement settings categories:
  - [ ] Database location (Admin/Super Admin)
  - [ ] Photo storage location (Super Admin)
  - [ ] Backup location (Admin/Super Admin)
  - [ ] PDF header image import
  - [ ] Color palette mode toggle (Super Admin)
- [ ] Store settings in AppSettings table
- [ ] Write settings tests

**Deliverables**:
- Settings dialog with role-based sections
- Settings persistence
- Validation for paths and files

---

### Milestone 5.3: Backup & Restore
**Duration**: 2 days

**Tasks**:
- [ ] Implement backup functionality:
  - [ ] Create ZIP with DB, photos, settings
  - [ ] Timestamped filename
  - [ ] Progress indicator
- [ ] Implement restore functionality:
  - [ ] Extract ZIP
  - [ ] Validate contents
  - [ ] Restore DB and photos
  - [ ] Restart application
- [ ] Implement scheduled backups (weekly, configurable)
- [ ] Write backup/restore tests

**Deliverables**:
- Manual backup/restore
- Scheduled backups
- Progress indicators

**Testing Checklist**:
- [ ] Backup creates valid ZIP
- [ ] Restore extracts and applies correctly
- [ ] Scheduled backup runs weekly
- [ ] Progress shown during operations

---

## Phase 6: Export & Reporting (Weeks 10-11)

### Milestone 6.1: PDF Exports
**Duration**: 5 days

**Tasks**:
- [ ] Implement family card PDF:
  - [ ] Header image support
  - [ ] Family photo in correct size
  - [ ] Family details section
  - [ ] Members table
  - [ ] Departed members (optional checkbox)
  - [ ] Footer with date and page number
- [ ] Implement directory PDF (Admin):
  - [ ] One family per page
  - [ ] Progress indicator
  - [ ] Include/exclude deleted families option
- [ ] Implement events PDF (Admin):
  - [ ] Birthdays by week/month
  - [ ] Anniversaries by week/month
  - [ ] Grouped by prayer group (optional)
- [ ] Write PDF generation tests

**Deliverables**:
- Family card PDF export
- Full directory PDF export
- Events PDF export
- Custom PDF header image support

**Testing Checklist**:
- [ ] PDF header image displayed correctly
- [ ] Family photo scales correctly in PDF
- [ ] Members table formatted properly
- [ ] Departed members included/excluded based on checkbox
- [ ] Directory PDF contains all families
- [ ] Events PDF shows correct dates

---

### Milestone 6.2: Excel Exports (Super Admin)
**Duration**: 4 days

**Tasks**:
- [ ] Implement family list Excel export:
  - [ ] Single worksheet with family summary
  - [ ] Columns: ID, Name, Prayer Group, Parish, Addresses, Member counts
  - [ ] Include/exclude deleted families option
- [ ] Implement complete data Excel export:
  - [ ] Multiple worksheets (Families, Members, Departed, Prayer Groups, Users)
  - [ ] All fields included
  - [ ] User data sanitized (no password hashes)
- [ ] Implement audit log Excel export:
  - [ ] Paginated for large datasets
  - [ ] Filtered by date/user/action
- [ ] Add progress indicators
- [ ] Write Excel export tests

**Deliverables**:
- Family list Excel export
- Complete data Excel export
- Audit log Excel export

**Testing Checklist**:
- [ ] Excel files open correctly in Excel/LibreOffice
- [ ] All data exported accurately
- [ ] Multiple worksheets created for complete export
- [ ] Password hashes not included in user export
- [ ] Filters applied correctly for audit log export

---

## Phase 7: Super Admin Console & System Health (Week 12)

### Milestone 7.1: Super Admin Console UI
**Duration**: 3 days

**Tasks**:
- [ ] Design Super Admin console layout
- [ ] Implement console sections:
  - [ ] Data exports (already done, add UI)
  - [ ] User management (already done, add UI)
  - [ ] System health dashboard
  - [ ] Crash reports viewer
  - [ ] Prayer group management (link to existing)
  - [ ] Settings (link to existing)
- [ ] Ensure Super Admin has no data viewing access
- [ ] Write console access tests

**Deliverables**:
- Super Admin console interface
- Access restrictions enforced
- All admin functions accessible from console

---

### Milestone 7.2: System Health Monitoring
**Duration**: 3 days

**Tasks**:
- [ ] Implement periodic health snapshots:
  - [ ] CPU usage (60-second average)
  - [ ] DB size
  - [ ] Photo storage size
  - [ ] Audit log size
  - [ ] Active families/members/users counts
- [ ] Implement health dashboard:
  - [ ] Current metrics display
  - [ ] Storage breakdown pie chart
  - [ ] Historical chart (last 30 days)
- [ ] Implement drive space check:
  - [ ] Check on app launch
  - [ ] Warn if < 10% free space
- [ ] Implement health snapshot export
- [ ] Write health monitoring tests

**Deliverables**:
- Automated health snapshots every 4 hours
- Health dashboard for Super Admin
- Low disk space warnings

---

### Milestone 7.3: Crash Reporting
**Duration**: 1 day

**Tasks**:
- [ ] Implement global exception handler
- [ ] Capture crash data:
  - [ ] Timestamp, error type, stack trace
  - [ ] Last 10 user actions
  - [ ] App and OS version
  - [ ] Current user role
- [ ] Store in CrashReports table (last 100 crashes)
- [ ] Implement crash report viewer (Super Admin):
  - [ ] List of crashes
  - [ ] Detail view
  - [ ] Export to text file
- [ ] Write crash reporting tests

**Deliverables**:
- Automatic crash report generation
- Crash report viewer
- Export crash logs

**Testing Checklist**:
- [ ] Unhandled exceptions trigger crash report
- [ ] User action history captured (last 10 actions)
- [ ] Crash report stored in database
- [ ] Super Admin can view and export crash reports
- [ ] No PII included in crash reports

---

## Phase 8: Testing & Polish (Weeks 13-14)

### Milestone 8.1: Comprehensive Testing
**Duration**: 5 days

**Tasks**:
- [ ] Run all unit tests (target: 80%+ coverage)
- [ ] Run all integration tests
- [ ] Perform manual UI testing:
  - [ ] Test all user roles
  - [ ] Test all workflows (add, edit, delete, restore)
  - [ ] Test all exports (PDF, Excel)
  - [ ] Test error scenarios
- [ ] Performance testing:
  - [ ] Load 500+ families
  - [ ] Test search performance
  - [ ] Test export performance
- [ ] Security testing:
  - [ ] Password policy enforcement
  - [ ] SQL injection attempts
  - [ ] RBAC enforcement
- [ ] Fix all critical and high-priority bugs

**Deliverables**:
- 80%+ code coverage
- All critical bugs fixed
- Performance benchmarks met

---

### Milestone 8.2: UI/UX Polish
**Duration**: 3 days

**Tasks**:
- [ ] Refine color scheme and styling
- [ ] Add keyboard shortcuts
- [ ] Add tooltips for complex features
- [ ] Improve error messages (user-friendly)
- [ ] Add loading indicators for slow operations
- [ ] Ensure consistent spacing and alignment
- [ ] Test on different screen resolutions
- [ ] Add icons where helpful

**Deliverables**:
- Polished, professional-looking UI
- Keyboard shortcuts implemented
- Tooltips added
- Consistent styling throughout

---

### Milestone 8.3: User Acceptance Testing (UAT)
**Duration**: 2 days

**Tasks**:
- [ ] Recruit 3-5 church staff for UAT
- [ ] Prepare UAT scenarios:
  - [ ] Add 50 families with photos
  - [ ] Search and filter
  - [ ] Generate reports
  - [ ] Test error handling
- [ ] Conduct UAT sessions
- [ ] Collect feedback
- [ ] Prioritize feedback items
- [ ] Fix high-priority issues

**Deliverables**:
- UAT feedback collected
- High-priority issues fixed
- User satisfaction confirmed

---

## Phase 9: Documentation & Deployment (Weeks 15-16)

### Milestone 9.1: User Manual
**Duration**: 4 days

**Tasks**:
- [ ] Write user manual (PDF):
  - [ ] Introduction
  - [ ] Getting started (first-run wizard)
  - [ ] User roles and permissions
  - [ ] Adding families and members
  - [ ] Editing and deleting data
  - [ ] Searching and filtering
  - [ ] Generating reports and exports
  - [ ] Prayer group management
  - [ ] Backup and restore
  - [ ] Troubleshooting
  - [ ] FAQ
- [ ] Add screenshots for all major features
- [ ] Create quick start guide (2-page PDF)
- [ ] Review and edit manual

**Deliverables**:
- Comprehensive user manual (PDF)
- Quick start guide (PDF)

---

### Milestone 9.2: Technical Documentation
**Duration**: 2 days

**Tasks**:
- [ ] Write developer documentation:
  - [ ] Architecture overview
  - [ ] Database schema
  - [ ] Code structure
  - [ ] Key design decisions
  - [ ] Adding new features guide
- [ ] Document API (if applicable)
- [ ] Add inline code comments where needed
- [ ] Create README.md with setup instructions

**Deliverables**:
- Developer documentation
- Updated code comments
- README.md

---

### Milestone 9.3: Packaging & Deployment
**Duration**: 3 days

**Tasks**:
- [ ] Set up PyInstaller for Windows executable
- [ ] Create installer (NSIS or Inno Setup):
  - [ ] Install Python runtime (if needed)
  - [ ] Install application files
  - [ ] Create desktop shortcut
  - [ ] Create Start Menu entry
  - [ ] Set up file associations
- [ ] Test installer on clean Windows 10 and Windows 11 machines
- [ ] Create uninstaller
- [ ] Sign executable (optional, for production)
- [ ] Create release notes

**Deliverables**:
- Windows installer (.exe)
- Uninstaller
- Release notes

**Testing Checklist**:
- [ ] Installer runs on Windows 10
- [ ] Installer runs on Windows 11
- [ ] Application launches successfully
- [ ] First-run wizard appears on clean install
- [ ] Uninstaller removes all files
- [ ] No errors in Windows Event Log

---

### Milestone 9.4: Training & Handoff
**Duration**: 1 day

**Tasks**:
- [ ] Conduct training session for church staff:
  - [ ] Super Admin features
  - [ ] Admin features
  - [ ] Add-Member features
  - [ ] View-Member features
- [ ] Provide user manual and quick start guide
- [ ] Demonstrate backup and restore
- [ ] Q&A session
- [ ] Handoff to client

**Deliverables**:
- Trained staff
- Installed application
- Support contact information

---

## Post-Launch Support (Ongoing)

### Month 1: Bug Fixes & Minor Enhancements
- [ ] Monitor for bug reports
- [ ] Release patches as needed
- [ ] Collect feature requests
- [ ] Provide remote support

### Month 2-3: Stability & Optimization
- [ ] Performance optimization based on real-world usage
- [ ] Database optimization (indexes, queries)
- [ ] UI tweaks based on user feedback

### Phase 2 Planning (Future)
- [ ] Malayalam localization
- [ ] Online sync feature
- [ ] Mobile companion app (research)

---

## Risk Management

### High-Risk Items
1. **Image handling performance** (500+ photos)
   - Mitigation: Implement lazy loading, thumbnail cache
2. **PDF generation for large directories** (500+ families)
   - Mitigation: Progress indicators, background processing
3. **Database corruption**
   - Mitigation: Regular backups, integrity checks, WAL mode
4. **User resistance to change**
   - Mitigation: Comprehensive training, intuitive UI, user manual

### Dependencies
- PySide6 updates (monitor for breaking changes)
- Windows OS updates (test on Windows Insider builds)
- Python security patches (stay on latest 3.11.x)

---

## Resource Requirements

### Team
- **1 Full-stack Developer** (primary)
- **1 UI/UX Designer** (part-time, weeks 3-6)
- **1 QA Tester** (part-time, weeks 13-14)
- **1 Technical Writer** (part-time, weeks 15-16)

### Hardware
- Windows 10/11 development machine (8+ GB RAM)
- Test machine (clean Windows install)
- Optional: Older machine (4 GB RAM) for performance testing

### Software
- Python 3.11+
- PySide6
- PyInstaller
- NSIS or Inno Setup (for installer)
- Git
- IDE (VS Code or PyCharm)

---

## Success Criteria

### Must Have
- [x] All features from requirements document implemented
- [x] 80%+ code coverage
- [x] No critical or high-priority bugs
- [x] Performance targets met
- [x] User manual and documentation complete
- [x] Windows installer working on Windows 10/11

### Should Have
- [x] UAT passed with user satisfaction
- [x] Keyboard shortcuts implemented
- [x] Tooltips and inline help
- [x] Professional, polished UI

### Nice to Have
- [ ] Advanced search filters
- [ ] Custom report templates
- [ ] Batch import from CSV

---

## Version History

**Version 1.0** (Planned Release: Week 16)
- Initial release with all core features
- Windows 10/11 support
- English UI only

**Version 1.1** (Planned: 3 months post-launch)
- Bug fixes and performance improvements
- Minor UI enhancements
- Additional report templates

**Version 2.0** (Planned: 6-12 months post-launch)
- Malayalam localization
- Online sync feature
- Advanced search and filtering
- Batch import/export

---

**Roadmap Version**: 1.0  
**Created**: December 31, 2024  
**Status**: Ready for Development