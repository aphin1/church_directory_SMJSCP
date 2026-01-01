-- ============================================================================
-- Church Directory Management System - SQLite Database Schema
-- Version: 2.0
-- Date: December 31, 2024
-- Python 3.11+ | PySide6 | SQLite 3
-- ============================================================================

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- Table: Users
-- Description: System users with role-based access control
-- ============================================================================
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,  -- Primary identifier, must be in Members table for Add-Member
    password_hash TEXT NOT NULL,  -- Argon2 hashed password
    role TEXT NOT NULL CHECK(role IN ('Super Admin', 'Admin', 'Add-Member')),
    reference_email TEXT,  -- For Add-Member: existing member email who vouched
    recovery_code_hash TEXT,  -- For Super Admin only: hashed recovery code
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT 1,
    
    -- Constraints
    CONSTRAINT chk_admin_no_reference CHECK (
        role != 'Admin' OR reference_email IS NULL
    ),
    CONSTRAINT chk_super_admin_no_reference CHECK (
        role != 'Super Admin' OR reference_email IS NULL
    )
);

-- ============================================================================
-- Table: PrayerGroups
-- Description: Prayer groups with unique background colors
-- ============================================================================
CREATE TABLE IF NOT EXISTS PrayerGroups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL UNIQUE,
    background_color TEXT NOT NULL UNIQUE,  -- Hex color code (e.g., #E3F2FD)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    
    -- Constraints
    CONSTRAINT chk_group_name_length CHECK (LENGTH(group_name) >= 1 AND LENGTH(group_name) <= 100),
    CONSTRAINT chk_color_format CHECK (background_color LIKE '#%' AND LENGTH(background_color) = 7)
);

-- ============================================================================
-- Table: Families
-- Description: Family records with head of family name
-- ============================================================================
CREATE TABLE IF NOT EXISTS Families (
    family_id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_name TEXT NOT NULL,  -- Head of Family Name, minimum 3 characters
    current_address TEXT,
    home_address TEXT,
    parish TEXT,
    prayer_group_id INTEGER NOT NULL,
    photo_path TEXT,  -- Relative path to family photo
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT 0,  -- Soft delete flag (visible to Admin only)
    deleted_at DATETIME,
    deletion_reason TEXT,  -- Mandatory reason for soft delete (10-500 chars)
    
    -- Foreign Keys
    FOREIGN KEY (prayer_group_id) REFERENCES PrayerGroups(group_id) ON DELETE RESTRICT,
    
    -- Constraints
    CONSTRAINT chk_family_name_length CHECK (LENGTH(family_name) >= 3 AND LENGTH(family_name) <= 100),
    CONSTRAINT chk_current_address_length CHECK (LENGTH(current_address) <= 500),
    CONSTRAINT chk_home_address_length CHECK (LENGTH(home_address) <= 500),
    CONSTRAINT chk_parish_length CHECK (LENGTH(parish) <= 100),
    CONSTRAINT chk_deletion_reason_length CHECK (
        deletion_reason IS NULL OR 
        (LENGTH(deletion_reason) >= 10 AND LENGTH(deletion_reason) <= 500)
    ),
    CONSTRAINT chk_deleted_requires_reason CHECK (
        (is_deleted = 0 AND deletion_reason IS NULL AND deleted_at IS NULL) OR
        (is_deleted = 1 AND deletion_reason IS NOT NULL AND deleted_at IS NOT NULL)
    )
);

-- ============================================================================
-- Table: Members
-- Description: Family members with demographic and contact information
-- ============================================================================
CREATE TABLE IF NOT EXISTS Members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female', 'Other')),
    relation TEXT NOT NULL CHECK(relation IN (
        'Head of Family', 'Spouse', 'Son', 'Daughter', 
        'Son-in-law', 'Daughter-in-law', 'Parent', 'Sibling', 'Other'
    )),
    spouse_member_id INTEGER,  -- For in-laws: links to son/daughter member_id
    
    -- Date fields with optional year
    birth_day INTEGER,  -- 1-31
    birth_month INTEGER,  -- 1-12
    birth_year INTEGER,  -- Optional: NULL if not provided
    
    marriage_day INTEGER,  -- 1-31, NULL if unmarried
    marriage_month INTEGER,  -- 1-12, NULL if unmarried
    marriage_year INTEGER,  -- Optional: NULL if not provided
    
    profession TEXT,
    email TEXT UNIQUE,  -- Unique across all members, used for access control
    phone TEXT,  -- International format: +XX-XXXXXXXXXX
    is_head_of_family BOOLEAN DEFAULT 0,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT 0,  -- Soft delete flag (visible to Admin only)
    deleted_at DATETIME,
    deletion_reason TEXT,  -- Mandatory reason for soft delete (10-500 chars)
    
    -- Foreign Keys
    FOREIGN KEY (family_id) REFERENCES Families(family_id) ON DELETE CASCADE,
    FOREIGN KEY (spouse_member_id) REFERENCES Members(member_id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_name_length CHECK (LENGTH(name) >= 1 AND LENGTH(name) <= 100),
    CONSTRAINT chk_profession_length CHECK (LENGTH(profession) <= 100),
    CONSTRAINT chk_email_length CHECK (LENGTH(email) <= 100),
    CONSTRAINT chk_phone_length CHECK (LENGTH(phone) <= 30),
    CONSTRAINT chk_birth_day CHECK (birth_day IS NULL OR (birth_day >= 1 AND birth_day <= 31)),
    CONSTRAINT chk_birth_month CHECK (birth_month IS NULL OR (birth_month >= 1 AND birth_month <= 12)),
    CONSTRAINT chk_marriage_day CHECK (marriage_day IS NULL OR (marriage_day >= 1 AND marriage_day <= 31)),
    CONSTRAINT chk_marriage_month CHECK (marriage_month IS NULL OR (marriage_month >= 1 AND marriage_month <= 12)),
    CONSTRAINT chk_birth_date_complete CHECK (
        (birth_day IS NULL AND birth_month IS NULL) OR
        (birth_day IS NOT NULL AND birth_month IS NOT NULL)
    ),
    CONSTRAINT chk_marriage_date_complete CHECK (
        (marriage_day IS NULL AND marriage_month IS NULL) OR
        (marriage_day IS NOT NULL AND marriage_month IS NOT NULL)
    ),
    CONSTRAINT chk_deletion_reason_length CHECK (
        deletion_reason IS NULL OR 
        (LENGTH(deletion_reason) >= 10 AND LENGTH(deletion_reason) <= 500)
    ),
    CONSTRAINT chk_deleted_requires_reason CHECK (
        (is_deleted = 0 AND deletion_reason IS NULL AND deleted_at IS NULL) OR
        (is_deleted = 1 AND deletion_reason IS NOT NULL AND deleted_at IS NOT NULL)
    ),
    CONSTRAINT chk_spouse_for_inlaws CHECK (
        (relation NOT IN ('Son-in-law', 'Daughter-in-law')) OR 
        spouse_member_id IS NOT NULL
    )
);

-- ============================================================================
-- Table: DepartedMembers
-- Description: Deceased family members
-- ============================================================================
CREATE TABLE IF NOT EXISTS DepartedMembers (
    departed_id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female', 'Other')),
    relation TEXT NOT NULL CHECK(relation IN (
        'Head of Family', 'Spouse', 'Son', 'Daughter', 
        'Son-in-law', 'Daughter-in-law', 'Parent', 'Sibling', 'Other'
    )),
    
    -- Date of Birth (optional, with optional year)
    birth_day INTEGER,  -- 1-31
    birth_month INTEGER,  -- 1-12
    birth_year INTEGER,  -- Optional
    
    -- Date of Death (required day/month, optional year)
    death_day INTEGER NOT NULL,  -- 1-31
    death_month INTEGER NOT NULL,  -- 1-12
    death_year INTEGER,  -- Optional
    
    notes TEXT,  -- Burial location, etc.
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT 0,  -- Soft delete flag (visible to Admin only)
    deleted_at DATETIME,
    deletion_reason TEXT,  -- Mandatory reason for soft delete (10-500 chars)
    
    -- Foreign Keys
    FOREIGN KEY (family_id) REFERENCES Families(family_id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_name_length CHECK (LENGTH(name) >= 1 AND LENGTH(name) <= 100),
    CONSTRAINT chk_notes_length CHECK (LENGTH(notes) <= 500),
    CONSTRAINT chk_birth_day CHECK (birth_day IS NULL OR (birth_day >= 1 AND birth_day <= 31)),
    CONSTRAINT chk_birth_month CHECK (birth_month IS NULL OR (birth_month >= 1 AND birth_month <= 12)),
    CONSTRAINT chk_death_day CHECK (death_day >= 1 AND death_day <= 31),
    CONSTRAINT chk_death_month CHECK (death_month >= 1 AND death_month <= 12),
    CONSTRAINT chk_birth_date_complete CHECK (
        (birth_day IS NULL AND birth_month IS NULL) OR
        (birth_day IS NOT NULL AND birth_month IS NOT NULL)
    ),
    CONSTRAINT chk_deletion_reason_length CHECK (
        deletion_reason IS NULL OR 
        (LENGTH(deletion_reason) >= 10 AND LENGTH(deletion_reason) <= 500)
    ),
    CONSTRAINT chk_deleted_requires_reason CHECK (
        (is_deleted = 0 AND deletion_reason IS NULL AND deleted_at IS NULL) OR
        (is_deleted = 1 AND deletion_reason IS NOT NULL AND deleted_at IS NOT NULL)
    )
);

-- ============================================================================
-- Table: DuplicateFamilyAlerts
-- Description: Tracks duplicate family names for Admin review
-- ============================================================================
CREATE TABLE IF NOT EXISTS DuplicateFamilyAlerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id_1 INTEGER NOT NULL,
    family_id_2 INTEGER NOT NULL,
    family_name TEXT NOT NULL,  -- Duplicate name
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT 0,
    resolution_action TEXT CHECK(resolution_action IN ('keep_both', 'deleted_one', 'renamed', NULL)),
    resolved_by_user_id INTEGER,
    resolved_at DATETIME,
    
    -- Foreign Keys
    FOREIGN KEY (family_id_1) REFERENCES Families(family_id) ON DELETE CASCADE,
    FOREIGN KEY (family_id_2) REFERENCES Families(family_id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by_user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_different_families CHECK (family_id_1 != family_id_2),
    CONSTRAINT chk_resolved_requires_action CHECK (
        (is_resolved = 0 AND resolution_action IS NULL AND resolved_at IS NULL) OR
        (is_resolved = 1 AND resolution_action IS NOT NULL AND resolved_at IS NOT NULL)
    )
);

-- ============================================================================
-- Table: AuditLog
-- Description: Comprehensive audit trail for all system actions
-- ============================================================================
CREATE TABLE IF NOT EXISTS AuditLog (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL CHECK(action IN (
        'login', 'logout', 'add', 'edit', 'delete', 'restore', 
        'export', 'backup', 'restore_backup', 'settings_change',
        'password_change', 'password_reset', 'user_create', 'user_disable'
    )),
    target_table TEXT CHECK(target_table IN (
        'families', 'members', 'departed_members', 'prayer_groups', 
        'users', 'app_settings', 'system', NULL
    )),
    target_id INTEGER,  -- ID of affected record
    details_json TEXT,  -- JSON with before/after values and additional details
    deletion_method TEXT,  -- "Auto-deleted by system" or "Deleted by Super Admin: [username]"
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL
);

-- ============================================================================
-- Table: CrashReports
-- Description: Application crash tracking for debugging
-- ============================================================================
CREATE TABLE IF NOT EXISTS CrashReports (
    crash_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    error_type TEXT NOT NULL,
    stack_trace TEXT NOT NULL,
    user_action_history TEXT,  -- JSON array of last 10 actions before crash
    app_version TEXT,
    os_version TEXT,
    user_id INTEGER,
    user_role TEXT,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL
);

-- ============================================================================
-- Table: AppSettings
-- Description: Application configuration settings
-- ============================================================================
CREATE TABLE IF NOT EXISTS AppSettings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,  -- Setting name (e.g., 'db_location', 'backup_path')
    value TEXT,  -- Setting value (can be JSON for complex settings)
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by_user_id INTEGER,
    
    -- Foreign Keys
    FOREIGN KEY (updated_by_user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_key_length CHECK (LENGTH(key) >= 1 AND LENGTH(key) <= 100)
);

-- ============================================================================
-- Table: SystemHealth
-- Description: Periodic system health snapshots
-- ============================================================================
CREATE TABLE IF NOT EXISTS SystemHealth (
    health_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    cpu_usage_percent REAL,  -- Average CPU usage over last 60 seconds
    db_size_bytes INTEGER,
    photo_storage_bytes INTEGER,
    log_storage_bytes INTEGER,
    total_families INTEGER,
    total_members INTEGER,
    active_users INTEGER,  -- Users logged in within last 30 days
    
    -- Constraints
    CONSTRAINT chk_cpu_usage CHECK (cpu_usage_percent >= 0 AND cpu_usage_percent <= 100)
);

-- ============================================================================
-- INDEXES for Performance Optimization
-- ============================================================================

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON Users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON Users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON Users(is_active);

-- Families indexes
CREATE INDEX IF NOT EXISTS idx_families_deleted ON Families(is_deleted);
CREATE INDEX IF NOT EXISTS idx_families_prayer_group ON Families(prayer_group_id);
CREATE INDEX IF NOT EXISTS idx_families_name ON Families(family_name);
CREATE INDEX IF NOT EXISTS idx_families_parish ON Families(parish);

-- Members indexes
CREATE INDEX IF NOT EXISTS idx_members_family ON Members(family_id);
CREATE INDEX IF NOT EXISTS idx_members_deleted ON Members(is_deleted);
CREATE INDEX IF NOT EXISTS idx_members_email ON Members(email);
CREATE INDEX IF NOT EXISTS idx_members_hof ON Members(is_head_of_family);
CREATE INDEX IF NOT EXISTS idx_members_birth_month ON Members(birth_month);
CREATE INDEX IF NOT EXISTS idx_members_marriage_month ON Members(marriage_month);

-- DepartedMembers indexes
CREATE INDEX IF NOT EXISTS idx_departed_family ON DepartedMembers(family_id);
CREATE INDEX IF NOT EXISTS idx_departed_deleted ON DepartedMembers(is_deleted);

-- DuplicateFamilyAlerts indexes
CREATE INDEX IF NOT EXISTS idx_duplicate_alerts_resolved ON DuplicateFamilyAlerts(is_resolved);
CREATE INDEX IF NOT EXISTS idx_duplicate_alerts_detected ON DuplicateFamilyAlerts(detected_at);

-- AuditLog indexes
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON AuditLog(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_user ON AuditLog(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON AuditLog(action);
CREATE INDEX IF NOT EXISTS idx_audit_target_table ON AuditLog(target_table);

-- CrashReports indexes
CREATE INDEX IF NOT EXISTS idx_crash_timestamp ON CrashReports(timestamp);

-- AppSettings indexes
CREATE INDEX IF NOT EXISTS idx_settings_key ON AppSettings(key);

-- SystemHealth indexes
CREATE INDEX IF NOT EXISTS idx_health_snapshot_time ON SystemHealth(snapshot_time);

-- ============================================================================
-- TRIGGERS for Automatic Timestamp Updates
-- ============================================================================

-- Update Families.updated_at on UPDATE
CREATE TRIGGER IF NOT EXISTS trg_families_updated_at
AFTER UPDATE ON Families
FOR EACH ROW
BEGIN
    UPDATE Families SET updated_at = CURRENT_TIMESTAMP WHERE family_id = NEW.family_id;
END;

-- Update Members.updated_at on UPDATE
CREATE TRIGGER IF NOT EXISTS trg_members_updated_at
AFTER UPDATE ON Members
FOR EACH ROW
BEGIN
    UPDATE Members SET updated_at = CURRENT_TIMESTAMP WHERE member_id = NEW.member_id;
END;

-- Update DepartedMembers.updated_at on UPDATE
CREATE TRIGGER IF NOT EXISTS trg_departed_updated_at
AFTER UPDATE ON DepartedMembers
FOR EACH ROW
BEGIN
    UPDATE DepartedMembers SET updated_at = CURRENT_TIMESTAMP WHERE departed_id = NEW.departed_id;
END;

-- Update PrayerGroups.updated_at on UPDATE
CREATE TRIGGER IF NOT EXISTS trg_prayer_groups_updated_at
AFTER UPDATE ON PrayerGroups
FOR EACH ROW
BEGIN
    UPDATE PrayerGroups SET updated_at = CURRENT_TIMESTAMP WHERE group_id = NEW.group_id;
END;

-- Update AppSettings.updated_at on UPDATE
CREATE TRIGGER IF NOT EXISTS trg_app_settings_updated_at
AFTER UPDATE ON AppSettings
FOR EACH ROW
BEGIN
    UPDATE AppSettings SET updated_at = CURRENT_TIMESTAMP WHERE setting_id = NEW.setting_id;
END;

-- ============================================================================
-- TRIGGERS for Data Integrity
-- ============================================================================

-- Ensure exactly one Head of Family per family (active members only)
CREATE TRIGGER IF NOT EXISTS trg_check_single_hof_insert
BEFORE INSERT ON Members
FOR EACH ROW
WHEN NEW.is_head_of_family = 1
BEGIN
    SELECT RAISE(ABORT, 'Family already has a Head of Family')
    WHERE EXISTS (
        SELECT 1 FROM Members 
        WHERE family_id = NEW.family_id 
        AND is_head_of_family = 1 
        AND is_deleted = 0
        AND member_id != NEW.member_id
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_check_single_hof_update
BEFORE UPDATE ON Members
FOR EACH ROW
WHEN NEW.is_head_of_family = 1
BEGIN
    SELECT RAISE(ABORT, 'Family already has a Head of Family')
    WHERE EXISTS (
        SELECT 1 FROM Members 
        WHERE family_id = NEW.family_id 
        AND is_head_of_family = 1 
        AND is_deleted = 0
        AND member_id != NEW.member_id
    );
END;

-- Soft delete all members when family is soft deleted
CREATE TRIGGER IF NOT EXISTS trg_soft_delete_family_members
AFTER UPDATE OF is_deleted ON Families
FOR EACH ROW
WHEN NEW.is_deleted = 1 AND OLD.is_deleted = 0
BEGIN
    UPDATE Members
    SET is_deleted = 1,
        deleted_at = CURRENT_TIMESTAMP,
        deletion_reason = 'Family deleted: ' || NEW.deletion_reason
    WHERE family_id = NEW.family_id
    AND is_deleted = 0;
END;

-- Prevent deletion of prayer group if families are assigned
CREATE TRIGGER IF NOT EXISTS trg_prevent_prayer_group_delete
BEFORE DELETE ON PrayerGroups
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Cannot delete prayer group: families are assigned to it')
    WHERE EXISTS (
        SELECT 1 FROM Families WHERE prayer_group_id = OLD.group_id AND is_deleted = 0
    );
END;

-- ============================================================================
-- VIEWS for Common Queries
-- ============================================================================

-- Active families with prayer group info
CREATE VIEW IF NOT EXISTS v_active_families AS
SELECT 
    f.family_id,
    f.family_name,
    f.current_address,
    f.home_address,
    f.parish,
    f.photo_path,
    pg.group_name AS prayer_group_name,
    pg.background_color,
    f.created_at,
    f.updated_at,
    (SELECT COUNT(*) FROM Members WHERE family_id = f.family_id AND is_deleted = 0) AS member_count,
    (SELECT COUNT(*) FROM DepartedMembers WHERE family_id = f.family_id AND is_deleted = 0) AS departed_count
FROM Families f
JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
WHERE f.is_deleted = 0;

-- Active members with family info
CREATE VIEW IF NOT EXISTS v_active_members AS
SELECT 
    m.member_id,
    m.family_id,
    f.family_name,
    m.name,
    m.gender,
    m.relation,
    m.birth_day,
    m.birth_month,
    m.birth_year,
    m.marriage_day,
    m.marriage_month,
    m.marriage_year,
    m.profession,
    m.email,
    m.phone,
    m.is_head_of_family,
    pg.group_name AS prayer_group_name,
    pg.background_color
FROM Members m
JOIN Families f ON m.family_id = f.family_id
JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
WHERE m.is_deleted = 0 AND f.is_deleted = 0;

-- Upcoming birthdays (current week)
CREATE VIEW IF NOT EXISTS v_upcoming_birthdays AS
SELECT 
    m.member_id,
    m.name,
    m.birth_day,
    m.birth_month,
    m.birth_year,
    f.family_name,
    pg.group_name AS prayer_group_name
FROM Members m
JOIN Families f ON m.family_id = f.family_id
JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
WHERE m.is_deleted = 0 
AND f.is_deleted = 0
AND m.birth_month IS NOT NULL
AND m.birth_day IS NOT NULL;

-- Upcoming anniversaries (current week)
CREATE VIEW IF NOT EXISTS v_upcoming_anniversaries AS
SELECT 
    m1.member_id AS member1_id,
    m1.name AS member1_name,
    m1.relation AS member1_relation,
    m2.member_id AS member2_id,
    m2.name AS member2_name,
    m2.relation AS member2_relation,
    m1.marriage_day,
    m1.marriage_month,
    m1.marriage_year,
    f.family_name,
    pg.group_name AS prayer_group_name
FROM Members m1
JOIN Families f ON m1.family_id = f.family_id
JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
LEFT JOIN Members m2 ON m1.spouse_member_id = m2.member_id
WHERE m1.is_deleted = 0 
AND f.is_deleted = 0
AND m1.marriage_month IS NOT NULL
AND m1.marriage_day IS NOT NULL
AND (m1.relation IN ('Head of Family', 'Son', 'Daughter', 'Son-in-law', 'Daughter-in-law'));

-- ============================================================================
-- DEFAULT DATA INSERTION
-- ============================================================================

-- Insert default app settings
INSERT OR IGNORE INTO AppSettings (key, value) VALUES 
    ('db_location', '%APPDATA%/ChurchDirectory/church_directory.db'),
    ('photo_storage_location', '%APPDATA%/ChurchDirectory/photos/'),
    ('backup_location', '%USERPROFILE%/Documents/ChurchDirectory/Backups/'),
    ('pdf_header_image_path', NULL),
    ('color_palette_mode', 'predefined'),  -- 'predefined' or 'free'
    ('backup_schedule', 'weekly'),  -- 'daily', 'weekly', 'monthly'
    ('last_backup_date', NULL),
    ('app_version', '1.0.0'),
    ('date_format', 'DD/MM/YYYY');

-- Insert default predefined color palette for prayer groups
-- (These are just available colors, actual prayer groups created during setup)
INSERT OR IGNORE INTO AppSettings (key, value) VALUES 
    ('predefined_colors', '["#E3F2FD","#E8F5E9","#F3E5F5","#FFE0B2","#FFF8E1","#FCE4EC","#E1F5FE","#FFFDE7","#FFEBEE","#E0F2F1","#F1F8E9","#FFF3E0","#EDE7F6","#E0F7FA","#F9FBE7","#FBE9E7","#EFEBE9","#ECEFF1","#F5F5F5","#FAFAFA"]');

-- ============================================================================
-- VACUUM and ANALYZE for Initial Optimization
-- ============================================================================

-- These commands should be run after initial setup
-- VACUUM; -- Reclaim unused space and defragment
-- ANALYZE; -- Update query planner statistics

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Schema version tracking
INSERT OR IGNORE INTO AppSettings (key, value) VALUES ('schema_version', '2.0');

-- Notes:
-- 1. First-run setup wizard will create the initial Super Admin user
-- 2. Prayer groups should be created during or after setup
-- 3. Run VACUUM and ANALYZE periodically for optimization
-- 4. Backup database regularly using built-in backup feature
-- 5. Monitor AuditLog table size (500MB limit with auto-cleanup)
-- 6. SystemHealth snapshots run every 4 hours automatically