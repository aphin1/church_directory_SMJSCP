"""
Church Directory Management System - Database Connection Module
Version: 2.0
Python 3.11+ | SQLite 3

This module provides database connection management and data access layer
for all CRUD operations with proper error handling and logging.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass


class DatabaseConnection:
    """
    Singleton database connection manager with connection pooling
    and automatic schema initialization.
    """
    
    _instance = None
    _connection = None
    _db_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection manager"""
        if self._connection is None:
            self._initialize_default_path()
    
    def _initialize_default_path(self):
        """Set default database path"""
        app_data = os.getenv('APPDATA') or os.path.expanduser('~/.local/share')
        self._db_path = Path(app_data) / 'ChurchDirectory' / 'church_directory.db'
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def set_database_path(self, path: str):
        """
        Set custom database path
        
        Args:
            path: Full path to database file
        """
        self._db_path = Path(path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Close existing connection if any
        if self._connection:
            self._connection.close()
            self._connection = None
        
        logger.info(f"Database path set to: {self._db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection (creates if doesn't exist)
        
        Returns:
            sqlite3.Connection: Active database connection
        """
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(
                    str(self._db_path),
                    check_same_thread=False,
                    timeout=30.0
                )
                # Enable foreign keys
                self._connection.execute("PRAGMA foreign_keys = ON")
                # Use WAL mode for better concurrency
                self._connection.execute("PRAGMA journal_mode = WAL")
                # Row factory for dict-like access
                self._connection.row_factory = sqlite3.Row
                
                logger.info(f"Database connection established: {self._db_path}")
                
                # Check if schema exists, if not initialize
                if not self._schema_exists():
                    self._initialize_schema()
                
            except sqlite3.Error as e:
                logger.error(f"Database connection error: {e}")
                raise DatabaseError(f"Failed to connect to database: {e}")
        
        return self._connection
    
    def _schema_exists(self) -> bool:
        """Check if database schema is initialized"""
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='Users'"
            )
            return cursor.fetchone() is not None
        except sqlite3.Error:
            return False
    
    def _initialize_schema(self):
        """Initialize database schema from SQL file"""
        schema_path = Path(__file__).parent / 'schema.sql'
        
        if not schema_path.exists():
            logger.warning("Schema file not found. Database will be empty.")
            return
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            self._connection.executescript(schema_sql)
            self._connection.commit()
            logger.info("Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Schema initialization error: {e}")
            raise DatabaseError(f"Failed to initialize schema: {e}")
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor with automatic commit/rollback
        
        Usage:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM Users")
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    def get_db_size(self) -> int:
        """Get database file size in bytes"""
        if self._db_path.exists():
            return self._db_path.stat().st_size
        return 0
    
    def vacuum(self):
        """Run VACUUM to optimize database"""
        try:
            conn = self.get_connection()
            conn.execute("VACUUM")
            conn.commit()
            logger.info("Database VACUUM completed")
        except sqlite3.Error as e:
            logger.error(f"VACUUM failed: {e}")
            raise DatabaseError(f"Database optimization failed: {e}")
    
    def analyze(self):
        """Run ANALYZE to update query planner statistics"""
        try:
            conn = self.get_connection()
            conn.execute("ANALYZE")
            conn.commit()
            logger.info("Database ANALYZE completed")
        except sqlite3.Error as e:
            logger.error(f"ANALYZE failed: {e}")


# Global database instance
db = DatabaseConnection()


class BaseDAO:
    """Base Data Access Object with common CRUD operations"""
    
    def __init__(self):
        self.db = db
    
    def _dict_to_row(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dict with None values to proper SQL NULL"""
        return {k: (v if v != '' else None) for k, v in data.items()}
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert sqlite3.Row to dictionary"""
        if row is None:
            return None
        return dict(row)
    
    def _rows_to_list(self, rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        """Convert list of sqlite3.Row to list of dictionaries"""
        return [self._row_to_dict(row) for row in rows]


class UserDAO(BaseDAO):
    """Data Access Object for Users table"""
    
    def create_user(
        self,
        email: str,
        password_hash: str,
        role: str,
        reference_email: Optional[str] = None,
        recovery_code_hash: Optional[str] = None
    ) -> int:
        """
        Create new user
        
        Args:
            email: User email (must be in Members table for Add-Member)
            password_hash: Argon2 hashed password
            role: 'Super Admin', 'Admin', or 'Add-Member'
            reference_email: For Add-Member, existing member who vouched
            recovery_code_hash: For Super Admin, hashed recovery code
        
        Returns:
            int: New user_id
        
        Raises:
            DatabaseError: If user creation fails
        """
        with self.db.get_cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO Users (email, password_hash, role, reference_email, recovery_code_hash)
                    VALUES (?, ?, ?, ?, ?)
                """, (email, password_hash, role, reference_email, recovery_code_hash))
                
                user_id = cursor.lastrowid
                logger.info(f"User created: {email} (ID: {user_id}, Role: {role})")
                return user_id
                
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed: Users.email' in str(e):
                    raise DatabaseError(f"Email already exists: {email}")
                raise DatabaseError(f"User creation failed: {e}")
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def update_password(self, user_id: int, new_password_hash: str):
        """Update user password"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE Users 
                SET password_hash = ? 
                WHERE user_id = ?
            """, (new_password_hash, user_id))
            logger.info(f"Password updated for user ID: {user_id}")
    
    def update_last_login(self, user_id: int):
        """Update last login timestamp"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE Users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            """, (user_id,))
    
    def disable_user(self, user_id: int):
        """Disable user account"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE Users 
                SET is_active = 0 
                WHERE user_id = ?
            """, (user_id,))
            logger.info(f"User disabled: ID {user_id}")
    
    def enable_user(self, user_id: int):
        """Enable user account"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE Users 
                SET is_active = 1 
                WHERE user_id = ?
            """, (user_id,))
            logger.info(f"User enabled: ID {user_id}")
    
    def get_all_users(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all users"""
        with self.db.get_cursor() as cursor:
            if include_inactive:
                cursor.execute("SELECT * FROM Users ORDER BY role, email")
            else:
                cursor.execute("""
                    SELECT * FROM Users 
                    WHERE is_active = 1 
                    ORDER BY role, email
                """)
            return self._rows_to_list(cursor.fetchall())
    
    def verify_email_in_members(self, email: str) -> bool:
        """Check if email exists in Members table"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM Members 
                WHERE email = ? AND is_deleted = 0
            """, (email,))
            return cursor.fetchone() is not None


class PrayerGroupDAO(BaseDAO):
    """Data Access Object for PrayerGroups table"""
    
    def create_prayer_group(
        self,
        group_name: str,
        background_color: str
    ) -> int:
        """
        Create new prayer group
        
        Args:
            group_name: Unique group name
            background_color: Hex color code (e.g., #E3F2FD)
        
        Returns:
            int: New group_id
        """
        with self.db.get_cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO PrayerGroups (group_name, background_color)
                    VALUES (?, ?)
                """, (group_name, background_color))
                
                group_id = cursor.lastrowid
                logger.info(f"Prayer group created: {group_name} (ID: {group_id})")
                return group_id
                
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed: PrayerGroups.group_name' in str(e):
                    raise DatabaseError(f"Prayer group name already exists: {group_name}")
                elif 'UNIQUE constraint failed: PrayerGroups.background_color' in str(e):
                    raise DatabaseError(f"Color already in use: {background_color}")
                raise DatabaseError(f"Prayer group creation failed: {e}")
    
    def get_prayer_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get prayer group by ID"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM PrayerGroups WHERE group_id = ?", (group_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_all_prayer_groups(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all prayer groups"""
        with self.db.get_cursor() as cursor:
            if include_inactive:
                cursor.execute("SELECT * FROM PrayerGroups ORDER BY group_name")
            else:
                cursor.execute("""
                    SELECT * FROM PrayerGroups 
                    WHERE is_active = 1 
                    ORDER BY group_name
                """)
            return self._rows_to_list(cursor.fetchall())
    
    def update_prayer_group(
        self,
        group_id: int,
        group_name: Optional[str] = None,
        background_color: Optional[str] = None
    ):
        """Update prayer group"""
        updates = []
        params = []
        
        if group_name is not None:
            updates.append("group_name = ?")
            params.append(group_name)
        
        if background_color is not None:
            updates.append("background_color = ?")
            params.append(background_color)
        
        if not updates:
            return
        
        params.append(group_id)
        
        with self.db.get_cursor() as cursor:
            try:
                cursor.execute(f"""
                    UPDATE PrayerGroups 
                    SET {', '.join(updates)}
                    WHERE group_id = ?
                """, params)
                logger.info(f"Prayer group updated: ID {group_id}")
            except sqlite3.IntegrityError as e:
                raise DatabaseError(f"Prayer group update failed: {e}")
    
    def deactivate_prayer_group(self, group_id: int):
        """Deactivate prayer group (cannot delete if families assigned)"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE PrayerGroups 
                SET is_active = 0 
                WHERE group_id = ?
            """, (group_id,))
            logger.info(f"Prayer group deactivated: ID {group_id}")
    
    def is_color_available(self, color: str, exclude_group_id: Optional[int] = None) -> bool:
        """Check if color is available (not used by other groups)"""
        with self.db.get_cursor() as cursor:
            if exclude_group_id:
                cursor.execute("""
                    SELECT 1 FROM PrayerGroups 
                    WHERE background_color = ? AND group_id != ?
                """, (color, exclude_group_id))
            else:
                cursor.execute("""
                    SELECT 1 FROM PrayerGroups 
                    WHERE background_color = ?
                """, (color,))
            
            return cursor.fetchone() is None


class FamilyDAO(BaseDAO):
    """Data Access Object for Families table"""
    
    def create_family(
        self,
        family_name: str,
        prayer_group_id: int,
        current_address: Optional[str] = None,
        home_address: Optional[str] = None,
        parish: Optional[str] = None,
        photo_path: Optional[str] = None
    ) -> int:
        """
        Create new family
        
        Args:
            family_name: Head of Family Name (min 3 characters)
            prayer_group_id: Prayer group assignment
            current_address: Current address
            home_address: Home address
            parish: Parish name
            photo_path: Relative path to family photo
        
        Returns:
            int: New family_id
        """
        # Check for duplicate family name
        duplicate_id = self._check_duplicate_name(family_name)
        
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO Families 
                (family_name, prayer_group_id, current_address, home_address, parish, photo_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (family_name, prayer_group_id, current_address, home_address, parish, photo_path))
            
            family_id = cursor.lastrowid
            logger.info(f"Family created: {family_name} (ID: {family_id})")
            
            # Create duplicate alert if needed
            if duplicate_id:
                self._create_duplicate_alert(family_id, duplicate_id, family_name)
            
            return family_id
    
    def _check_duplicate_name(self, family_name: str) -> Optional[int]:
        """Check for duplicate family name, return existing family_id if found"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT family_id FROM Families 
                WHERE family_name = ? AND is_deleted = 0
            """, (family_name,))
            result = cursor.fetchone()
            return result['family_id'] if result else None
    
    def _create_duplicate_alert(self, family_id_1: int, family_id_2: int, family_name: str):
        """Create duplicate family name alert"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO DuplicateFamilyAlerts 
                (family_id_1, family_id_2, family_name)
                VALUES (?, ?, ?)
            """, (family_id_1, family_id_2, family_name))
            logger.warning(f"Duplicate family name alert created: {family_name}")
    
    def get_family(self, family_id: int) -> Optional[Dict[str, Any]]:
        """Get family by ID with prayer group info"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT f.*, pg.group_name, pg.background_color
                FROM Families f
                JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
                WHERE f.family_id = ?
            """, (family_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_all_families(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Get all families"""
        with self.db.get_cursor() as cursor:
            if include_deleted:
                cursor.execute("""
                    SELECT * FROM v_active_families
                    UNION ALL
                    SELECT 
                        f.family_id, f.family_name, f.current_address, f.home_address,
                        f.parish, f.photo_path, pg.group_name AS prayer_group_name,
                        pg.background_color, f.created_at, f.updated_at,
                        (SELECT COUNT(*) FROM Members WHERE family_id = f.family_id AND is_deleted = 0) AS member_count,
                        (SELECT COUNT(*) FROM DepartedMembers WHERE family_id = f.family_id AND is_deleted = 0) AS departed_count
                    FROM Families f
                    JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
                    WHERE f.is_deleted = 1
                    ORDER BY family_name
                """)
            else:
                cursor.execute("SELECT * FROM v_active_families ORDER BY family_name")
            
            return self._rows_to_list(cursor.fetchall())
    
    def search_families(self, query: str, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        Search families by name, member name, email, phone, or parish
        
        Args:
            query: Search term
            include_deleted: Include soft-deleted families
        
        Returns:
            List of matching families
        """
        search_pattern = f"%{query}%"
        
        with self.db.get_cursor() as cursor:
            deleted_condition = "" if include_deleted else "AND f.is_deleted = 0"
            
            cursor.execute(f"""
                SELECT DISTINCT f.*, pg.group_name, pg.background_color
                FROM Families f
                JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
                LEFT JOIN Members m ON f.family_id = m.family_id
                WHERE (
                    f.family_name LIKE ? OR
                    f.parish LIKE ? OR
                    m.name LIKE ? OR
                    m.email LIKE ? OR
                    m.phone LIKE ?
                ) {deleted_condition}
                ORDER BY f.family_name
            """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            
            return self._rows_to_list(cursor.fetchall())
    
    def update_family(
        self,
        family_id: int,
        family_name: Optional[str] = None,
        prayer_group_id: Optional[int] = None,
        current_address: Optional[str] = None,
        home_address: Optional[str] = None,
        parish: Optional[str] = None,
        photo_path: Optional[str] = None
    ):
        """Update family information"""
        updates = []
        params = []
        
        if family_name is not None:
            updates.append("family_name = ?")
            params.append(family_name)
        
        if prayer_group_id is not None:
            updates.append("prayer_group_id = ?")
            params.append(prayer_group_id)
        
        if current_address is not None:
            updates.append("current_address = ?")
            params.append(current_address)
        
        if home_address is not None:
            updates.append("home_address = ?")
            params.append(home_address)
        
        if parish is not None:
            updates.append("parish = ?")
            params.append(parish)
        
        if photo_path is not None:
            updates.append("photo_path = ?")
            params.append(photo_path)
        
        if not updates:
            return
        
        params.append(family_id)
        
        with self.db.get_cursor() as cursor:
            cursor.execute(f"""
                UPDATE Families 
                SET {', '.join(updates)}
                WHERE family_id = ?
            """, params)
            logger.info(f"Family updated: ID {family_id}")
    
    def soft_delete_family(self, family_id: int, reason: str):
        """
        Soft delete family (triggers cascade to members)
        
        Args:
            family_id: Family to delete
            reason: Mandatory deletion reason (10-500 characters)
        """
        if len(reason) < 10 or len(reason) > 500:
            raise DatabaseError("Deletion reason must be 10-500 characters")
        
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE Families 
                SET is_deleted = 1, 
                    deleted_at = CURRENT_TIMESTAMP,
                    deletion_reason = ?
                WHERE family_id = ?
            """, (reason, family_id))
            logger.info(f"Family soft deleted: ID {family_id}, Reason: {reason[:50]}...")
    
    def restore_family(self, family_id: int):
        """Restore soft-deleted family"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE Families 
                SET is_deleted = 0, 
                    deleted_at = NULL,
                    deletion_reason = NULL
                WHERE family_id = ?
            """, (family_id,))
            logger.info(f"Family restored: ID {family_id}")
    
    def get_families_by_prayer_group(
        self,
        prayer_group_id: int,
        include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """Get families in a specific prayer group"""
        with self.db.get_cursor() as cursor:
            deleted_condition = "" if include_deleted else "AND is_deleted = 0"
            
            cursor.execute(f"""
                SELECT * FROM v_active_families
                WHERE prayer_group_name = (
                    SELECT group_name FROM PrayerGroups WHERE group_id = ?
                )
                {deleted_condition}
                ORDER BY family_name
            """, (prayer_group_id,))
            
            return self._rows_to_list(cursor.fetchall())


# Initialize global DAO instances for easy import
user_dao = UserDAO()
prayer_group_dao = PrayerGroupDAO()
family_dao = FamilyDAO()


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    try:
        conn = db.get_connection()
        print(f"✓ Connected to: {db._db_path}")
        print(f"✓ Database size: {db.get_db_size() / 1024:.2f} KB")
        
        # Test schema
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✓ Tables found: {len(tables)}")
        for table in tables:
            print(f"  - {table['name']}")
        
        print("\n✓ Database module ready!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        db.close()
