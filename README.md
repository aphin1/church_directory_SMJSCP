# Church Directory Desktop Application

> A comprehensive, secure, and user-friendly desktop application for managing church family directories with role-based access control, event notifications, and robust reporting capabilities.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://pypi.org/project/PySide6/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Screenshots](#screenshots)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [User Roles](#user-roles)
- [Usage Guide](#usage-guide)
- [Export & Reporting](#export--reporting)
- [Security](#security)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## 🌟 Overview

The Church Directory Desktop Application is a stand-alone Windows application designed to help churches manage their member directories efficiently. Built with Python and PySide6, it provides an elegant, intuitive interface for viewing, searching, adding, and editing family and member information while maintaining strict role-based access controls.

### Why This Application?

- **Offline-First**: No internet required; all data stored locally with full control
- **Role-Based Security**: Four distinct user roles with granular permissions
- **Comprehensive Records**: Track families, members, and departed members with detailed information
- **Event Notifications**: Never miss a birthday or anniversary
- **Professional Exports**: Generate PDF directories and Excel reports
- **Prayer Group Organization**: Color-coded groups for easy visual identification
- **Audit Trail**: Complete activity logging for transparency and accountability
- **Future-Proof**: Built on modern, long-term supported technologies

---

## ✨ Key Features

### 📇 Family & Member Management

- **Compact Card View**: Elegant family cards with photos (160×120px) and complete details
- **Multi-Step Wizard**: Guided process for adding families with validation at each step
- **Soft Delete System**: Safely archive records without permanent data loss
- **Duplicate Detection**: Smart warnings for duplicate family names with admin review workflow
- **International Support**: Phone numbers with country code validation (+XX-XXXXXXXXXX format)
- **Flexible Date Fields**: Optional year entry for DOB/DOM/DOD fields

### 🔍 Search & Navigation

- **Real-Time Search**: Instant results as you type
- **Multi-Field Search**: Search by family name, member name, email, phone, or parish
- **Alphabetical Index**: Quick A-Z family navigation
- **Prayer Group Browser**: Expandable groups with unique color coding
- **Smart Filtering**: Hide/show deleted records based on user role

### 🎂 Event Notifications

- **Birthday Tracking**: Weekly birthday list with ages
- **Anniversary Reminders**: Couple names with years married
- **Week Navigation**: Browse past and future weeks
- **Family Context**: See which family each event belongs to
- **Smart Couple Linking**: Automatic pairing of spouses and in-laws

### 📊 Export & Reporting

**For Admins:**
- Full directory PDF with family cards (one per page)
- Birthday/anniversary reports (weekly or monthly)
- Departed member lists (weekly or monthly)

**For Super Admins:**
- Family list in Excel table format
- Complete database export (multi-sheet Excel workbook)
- Audit log exports (last 365 days)
- System health reports

### 🎨 Prayer Group Management

- **Predefined Color Palette**: 20-30 gentle, soothing pastel colors
- **Advanced Color Picker**: Optional custom RGB selection (Super Admin only)
- **Visual Organization**: Each group has unique background color
- **Smart Assignment**: Easy dropdown selection when adding families

### 🔒 Security & Privacy

- **Argon2 Password Hashing**: Industry-standard password protection
- **Role-Based Access**: Four user levels with distinct permissions
- **Password Policy**: Strong requirements (10+ chars, mixed case, numbers, symbols)
- **Recovery System**: Secure password reset for all roles
- **Audit Logging**: Complete 365-day activity history
- **No External Calls**: 100% offline, no telemetry or tracking

### 💾 Backup & Recovery

- **Automated Backups**: Scheduled weekly backups (configurable)
- **One-Click Backup**: Manual backup anytime
- **Complete Archives**: ZIP bundles containing database, photos, and settings
- **Easy Restore**: Simple restoration from backup archives
- **Configurable Locations**: Choose your own backup directory

### 📈 System Monitoring

- **Health Snapshots**: CPU, memory, and storage tracking every 4 hours
- **Storage Breakdown**: Visual breakdown of database, photos, and logs
- **Crash Reporting**: Automatic crash log generation for troubleshooting
- **Low Space Warnings**: Alerts when drive space is running low

---

## 🖼️ Screenshots

> 📸 Screenshots coming soon! (Add screenshots of main interface, family card, wizard, exports, etc.)

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.11+ | Long-term support, mature ecosystem |
| **GUI Framework** | PySide6 (Qt6) | Cross-platform, future-proof, elegant UI |
| **Database** | SQLite 3 | Portable, reliable, zero-config |
| **PDF Generation** | ReportLab | Professional PDF creation with images |
| **Excel Export** | openpyxl | Full Excel format support |
| **Password Hashing** | Argon2 (argon2-cffi) | Modern, secure password storage |
| **Image Processing** | Pillow | Image validation and manipulation |

---

## 📦 Installation

### Prerequisites

- **Operating System**: Windows 10 or Windows 11
- **Python**: Version 3.11 or higher
- **Disk Space**: Minimum 100 MB (more for photos and data)
- **RAM**: 4 GB recommended

### Step 1: Clone the Repository

```bash
git clone https://github.com/aphin1/church_directory_SMJSCP.git
cd church-directory
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
```
PySide6>=6.5.0
ReportLab>=4.0.0
openpyxl>=3.1.0
argon2-cffi>=23.1.0
Pillow>=10.0.0
```

### Step 3: Run the Application

```bash
python main.py
```

### First Launch Setup

On first launch, the **Initial Setup Wizard** will guide you through:

1. **Welcome Screen**: Introduction and privacy notice
2. **Super Admin Creation**: Set up the first administrative account
3. **Basic Configuration**: Choose database and photo storage locations
4. **Prayer Groups**: Optionally create initial prayer groups
5. **Completion**: Launch the application

**Important:** Save your Super Admin recovery code! It's displayed only once and is required for password recovery.

---

## 👥 User Roles

The application implements a hierarchical role-based access control system:

### 🔑 Super Admin

**Purpose**: System oversight and high-level reporting

- ✅ Export complete data (Excel)
- ✅ Export family lists (table view)
- ✅ View and export audit logs (365 days)
- ✅ View system health and crash reports
- ✅ Manage all users and settings
- ✅ Reset any user's password
- ✅ Manage prayer groups
- ❌ **No data viewing** (no family cards or member details)

### 👨‍💼 Admin (Vicar)

**Purpose**: Day-to-day data management and operations

- ✅ View, search, and browse all families
- ✅ Edit existing families and members
- ✅ Soft delete and restore records
- ✅ Export directory PDF (with/without deleted)
- ✅ Export birthday/anniversary/departed PDFs
- ✅ Manage prayer groups
- ✅ Create Add-Member users
- ✅ Reset Add-Member passwords
- ✅ Backup and restore database
- ❌ Cannot add new families (separation of duties)

### ✍️ Add-Member

**Purpose**: Data entry for new families

- ✅ Add new families and members via wizard
- ✅ View families using registered email (own data only)
- ✅ Export own family card PDF
- ✅ View notifications for own family
- ❌ Cannot edit after submission
- ❌ Cannot delete records
- ❌ Fixed panel layout (no resizing)

---

## 📖 Usage Guide

### Adding a New Family

1. **Login** as Add-Member or Admin
2. Click **"Add Family"** button
3. Follow the **5-step wizard**:
   - **Step 1**: Enter family information (name, addresses, parish, prayer group)
   - **Step 2**: Add family members (name, relation, DOB, email, phone, etc.)
   - **Step 3**: Add departed members (optional)
   - **Step 4**: Upload family photo (JPEG/PNG, minimum 160×120 recommended)
   - **Step 5**: Review and submit
4. Wizard validates data at each step and shows timeline progress
5. On successful submission, view the new family card

### Searching for Families

- Type in the **search box** at the top of the sidebar
- Results filter in real-time as you type
- Search works across:
  - Family names
  - Member names
  - Email addresses
  - Phone numbers
  - Parish names
- Click any result to view the family card

### Editing Family Information

**Admin only:**

1. Select a family from the sidebar
2. Click **"Edit Members"** button on the family card
3. The same multi-step wizard opens, pre-filled with existing data
4. Make changes and save
5. All edits are logged in the audit trail

### Managing Deleted Records

**Admin/Super Admin only:**

1. Open **Admin Dashboard** → **Manage Deleted Records**
2. View list of soft-deleted families, members, and departed members
3. **Restore**: Click restore button to reactivate
4. **View Reason**: See why the record was deleted
5. **Permanently Delete**: Super Admin can permanently remove (with confirmation)

### Exporting Reports

#### Directory PDF (Admin)

1. Open **Admin Dashboard**
2. Click **"Export Directory PDF"**
3. Choose options:
   - ☐ Include deleted families
4. Select save location
5. Watch progress bar; file generated on completion

#### Complete Data Export (Super Admin)

1. Open **Super Admin Console**
2. Click **"Export Complete Data to Excel"**
3. Choose save location
4. Multi-sheet workbook created with all tables

### Weekly Notifications

- **Right sidebar** shows current week's events
- **Birthdays** at the top, **Anniversaries** below
- Use **< Previous** and **Next >** buttons to navigate weeks
- Background color matches currently selected family's prayer group

---

## 📄 Export & Reporting

### PDF Reports

All PDF exports include:
- Custom header image (uploaded by admin)
- Professional formatting with margins
- Page numbers and export date in footer
- Family photos maintained at 160×120 aspect ratio

### Excel Reports

| Report Type | Access | Contains |
|-------------|--------|----------|
| **Family List** | Super Admin | Family ID, Name, Prayer Group, Parish, Addresses |
| **Complete Data** | Super Admin | All tables (Families, Members, Departed, Groups, Users) |
| **Audit Logs** | Super Admin | Full activity log (365 days), filterable |

---

## 🔐 Security

### Password Management

- **Minimum 10 characters** with complexity requirements
- **Argon2 hashing** with unique salts (never stored in plain text)
- **Recovery code** for Super Admin (20-character alphanumeric)
- **Admin-mediated reset** for regular users (in-person verification)
- **Forced change** on temporary password login

### Data Protection

- **Soft delete** preserves data integrity
- **Audit logging** tracks all changes (365 days)
- **No external calls** – 100% offline operation
- **File permissions** rely on standard Windows security
- **Backup encryption** (optional, future phase)

### Role Isolation

- Super Admin sees **only reports**, not raw data
- Admin can edit but **not add** families (separation of duties)
- Add-Member can add but **not edit** after submission
- All actions **logged with username and timestamp**

---

## 🧑‍💻 Development

### Project Structure

```
church_directory_project/
├── main.py                 # Application entry point
├── controllers/            # Business logic
│   ├── auth_controller.py
│   ├── family_controller.py
│   ├── member_controller.py
│   └── export_controller.py
├── models/                 # Database models
│   ├── database.py
│   ├── family.py
│   ├── member.py
│   ├── departed.py
│   ├── user.py
│   └── audit.py
├── views/                  # UI components
│   ├── family_card.py
│   ├── sidebar.py
│   ├── add_edit_dialog.py
│   ├── notifications.py
│   └── admin_dashboard.py
├── utils/                  # Helper functions
│   ├── image_utils.py
│   └── pdf_utils.py
├── assets/                 # Icons and images
├── docs/                   # Documentation
│   └── refined_requirements.md
├── tests/                  # Unit and integration tests
├── requirements.txt        # Python dependencies
├── LICENSE
└── README.md
```

### Running Tests

```bash
# Unit tests
python -m pytest tests/unit

# Integration tests
python -m pytest tests/integration

# All tests with coverage
python -m pytest --cov=. tests/
```

### Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build standalone executable
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py

# Output in dist/main.exe
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Code Standards

- Follow **PEP 8** style guidelines
- Write **docstrings** for all functions and classes
- Add **unit tests** for new features
- Update **documentation** as needed
- Keep **commit messages** clear and descriptive

### Testing

- All PRs must pass existing tests
- Add tests for new functionality
- Maintain or improve code coverage

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details. (coming soon)

---

## 🆘 Support

### Documentation

- [Refined Requirements](docs/refined_requirements.md) – Complete feature specification
- [User Manual](docs/user_manual.pdf) – Step-by-step usage guide (coming soon)
- [API Documentation](docs/api.md) – Developer reference (coming soon)

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/church-directory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/church-directory/discussions)
- **Email**: smjsc.pune@gmail.com

### Reporting Bugs

When reporting bugs, please include:

- Operating System and version
- Python version
- Application version
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots (if applicable)
- Error messages or crash reports

---

## 🗺️ Roadmap

### Phase 1: Core Features (Current)

- ✅ Family and member management
- ✅ Multi-step wizard
- ✅ Search and navigation
- ✅ Role-based access control
- ✅ PDF and Excel exports
- ✅ Backup and restore
- ✅ Audit logging
- ✅ Event notifications

### Phase 2: Enhancements (Planned)

- ⏳ Malayalam localization
- ⏳ Batch CSV import
- ⏳ Custom report templates
- ⏳ Advanced search filters
- ⏳ Keyboard shortcuts
- ⏳ Database encryption (SQLCipher)

### Phase 3: Future Vision

- 🔮 Online sync across multiple installations
- 🔮 Mobile companion app (iOS/Android)
- 🔮 Email/SMS notifications
- 🔮 Web-based viewer (read-only)
- 🔮 Multi-language support

---

## 🙏 Acknowledgments

- **PySide6/Qt** for the excellent GUI framework
- **SQLite** for reliable, embedded database technology
- **ReportLab** for professional PDF generation
- All contributors and testers who helped refine this application

---

## 📞 Contact

**Project Maintainer**: [aphin1](mailto:aphin.proc@outlook.com)  
**Project Link**: [https://github.com/yourusername/church-directory](https://github.com/aphin1/church_directory_SMJSCP)

---

<div align="center">

**Made with ❤️ for churches everywhere**

⭐ **Star this repo** if you find it helpful!

</div>
