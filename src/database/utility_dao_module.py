"""
Church Directory Management System - Utility DAOs
Version: 2.0

Data Access Objects for AuditLog, DuplicateFamilyAlerts, AppSettings,
SystemHealth, and CrashReports.
"""

import sqlite3
import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from db_connection import BaseDAO, DatabaseError, db

logger = logging.getLogger(__name__)


class AuditLogDAO(BaseDAO):
    """Data Access Object for AuditLog table"""
    
    MAX_LOG_SIZE_MB = 500
    RETENTION_DAYS = 365
    
    def log_action(
        self,
        user_id: Optional[int],
        action: str,
        target_table: Optional[str] = None,
        target_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an action to audit trail
        
        Args:
            user_id: User who performed the action (None for system actions)
            action: Action type (login, logout, add, edit, delete, restore, export, etc.)
            target_table: Table affected (families, members, etc.)
            target_id: ID of affected record
            details: Additional details as dict (will be JSON encoded)
        """
        details_json = json.dumps(details) if details else None
        
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO AuditLog 
                (user_id, action, target_table, target_id, details_json)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, action, target_table, target_id, details_json))
            
            # Check if cleanup needed (every 100 inserts approximately)
            if cursor.lastrowid % 100 == 0:
                self._auto_cleanup()
    
    def _auto_cleanup(self):
        """Automatic cleanup of old audit logs (365 days or 500MB limit)"""
        with self.db.get_cursor() as cursor:
            # Delete logs older than 365 days
            cutoff_date = datetime.now() - timedelta(days=self.RETENTION_DAYS)
            cursor.execute("""
                UPDATE AuditLog
                SET deletion_method = 'Auto-deleted by system'
                WHERE timestamp < ? AND deletion_method IS NULL
            """, (cutoff_date,))
            
            # Check total log size
            cursor.execute("SELECT COUNT(*) * 1000 FROM AuditLog")  # Rough estimate
            estimated_size_kb = cursor.fetchone()[0]
            
            if estimated_size_kb > self.MAX_LOG_SIZE_MB * 1024:
                # Delete oldest 10% of logs
                cursor.execute("""
                    DELETE FROM AuditLog
                    WHERE log_id IN (
                        SELECT log_id FROM AuditLog
                        ORDER BY timestamp ASC
                        LIMIT (SELECT COUNT(*) / 10 FROM AuditLog)
                    )
                """)
                logger.info(f"Auto-cleanup: Deleted oldest logs due to size limit")
    
    def manual_purge(self, days_to_keep: int, admin_username: str):
        """
        Manually purge logs older than specified days (Super Admin only)
        
        Args:
            days_to_keep: Keep logs from last N days
            admin_username: Super Admin username performing the purge
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE AuditLog
                SET deletion_method = ?
                WHERE timestamp < ? AND deletion_method IS NULL
            """, (f"Deleted by Super Admin: {admin_username}", cutoff_date))
            
            deleted_count = cursor.rowcount
            logger.info(f"Manual purge by {admin_username}: {deleted_count} logs marked")
            
            return deleted_count
    
    def get_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        target_table: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs with filters
        
        Args:
            user_id: Filter by user ID
            action: Filter by action type
            target_table: Filter by target table
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            offset: Pagination offset
        
        Returns:
            List of log entries
        """
        conditions = []
        params = []
        
        if user_id is not None:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if action:
            conditions.append("action = ?")
            params.append(action)
        
        if target_table:
            conditions.append("target_table = ?")
            params.append(target_table)
        
        if start_date:
            conditions.append("timestamp >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("timestamp <= ?")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        params.extend([limit, offset])
        
        with self.db.get_cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    al.log_id, al.user_id, u.email AS user_email, u.role,
                    al.action, al.target_table, al.target_id, al.details_json,
                    al.deletion_method, al.timestamp
                FROM AuditLog al
                LEFT JOIN Users u ON al.user_id = u.user_id
                {where_clause}
                ORDER BY al.timestamp DESC
                LIMIT ? OFFSET ?
            """, params)
            
            logs = self._rows_to_list(cursor.fetchall())
            
            # Parse JSON details
            for log in logs:
                if log['details_json']:
                    try:
                        log['details'] = json.loads(log['details_json'])
                    except:
                        log['details'] = {}
                else:
                    log['details'] = {}
            
            return logs
    
    def get_log_count(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        target_table: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Get total count of logs matching filters"""
        conditions = []
        params = []
        
        if user_id is not None:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if action:
            conditions.append("action = ?")
            params.append(action)
        
        if target_table:
            conditions.append("target_table = ?")
            params.append(target_table)
        
        if start_date:
            conditions.append("timestamp >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("timestamp <= ?")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        with self.db.get_cursor() as cursor:
            cursor.execute(f"""
                SELECT COUNT(*) as count FROM AuditLog {where_clause}
            """, params)
            
            return cursor.fetchone()['count']
    
    def get_storage_size(self) -> int:
        """Get approximate audit log storage size in bytes"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) * 1500 FROM AuditLog")  # Rough estimate
            return cursor.fetchone()[0]


class DuplicateFamilyAlertDAO(BaseDAO):
    """Data Access Object for DuplicateFamilyAlerts table"""
    
    def get_unresolved_alerts(self) -> List[Dict[str, Any]]:
        """Get all unresolved duplicate family name alerts"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    dfa.alert_id, dfa.family_name, dfa.detected_at,
                    f1.family_id AS family_1_id, f1.current_address AS family_1_address,
                    f2.family_id AS family_2_id, f2.current_address AS family_2_address,
                    pg1.group_name AS family_1_prayer_group,
                    pg2.group_name AS family_2_prayer_group
                FROM DuplicateFamilyAlerts dfa
                JOIN Families f1 ON dfa.family_id_1 = f1.family_id
                JOIN Families f2 ON dfa.family_id_2 = f2.family_id
                JOIN PrayerGroups pg1 ON f1.prayer_group_id = pg1.group_id
                JOIN PrayerGroups pg2 ON f2.prayer_group_id = pg2.group_id
                WHERE dfa.is_resolved = 0
                ORDER BY dfa.detected_at DESC
            """)
            
            return self._rows_to_list(cursor.fetchall())
    
    def resolve_alert(
        self,
        alert_id: int,
        resolution_action: str,
        resolved_by_user_id: int
    ):
        """
        Resolve a duplicate family alert
        
        Args:
            alert_id: Alert to resolve
            resolution_action: 'keep_both', 'deleted_one', or 'renamed'
            resolved_by_user_id: User who resolved the alert
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE DuplicateFamilyAlerts
                SET is_resolved = 1,
                    resolution_action = ?,
                    resolved_by_user_id = ?,
                    resolved_at = CURRENT_TIMESTAMP
                WHERE alert_id = ?
            """, (resolution_action, resolved_by_user_id, alert_id))
            
            logger.info(f"Duplicate alert resolved: ID {alert_id}, Action: {resolution_action}")
    
    def get_alert(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """Get specific alert by ID"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT dfa.*, 
                    f1.family_name AS family_1_name,
                    f2.family_name AS family_2_name
                FROM DuplicateFamilyAlerts dfa
                JOIN Families f1 ON dfa.family_id_1 = f1.family_id
                JOIN Families f2 ON dfa.family_id_2 = f2.family_id
                WHERE dfa.alert_id = ?
            """, (alert_id,))
            
            return self._row_to_dict(cursor.fetchone())


class AppSettingsDAO(BaseDAO):
    """Data Access Object for AppSettings table"""
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get setting value by key"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT value FROM AppSettings WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result['value'] if result else None
    
    def set_setting(
        self,
        key: str,
        value: str,
        updated_by_user_id: Optional[int] = None
    ):
        """Set or update setting value"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO AppSettings (key, value, updated_by_user_id)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_by_user_id = excluded.updated_by_user_id,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value, updated_by_user_id))
            
            logger.info(f"Setting updated: {key}")
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings as dictionary"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT key, value FROM AppSettings")
            return {row['key']: row['value'] for row in cursor.fetchall()}
    
    def get_predefined_colors(self) -> List[str]:
        """Get predefined color palette"""
        colors_json = self.get_setting('predefined_colors')
        if colors_json:
            try:
                return json.loads(colors_json)
            except:
                pass
        return []
    
    def is_color_palette_mode_free(self) -> bool:
        """Check if color palette mode is set to 'free' (Super Admin enabled)"""
        mode = self.get_setting('color_palette_mode')
        return mode == 'free'


class SystemHealthDAO(BaseDAO):
    """Data Access Object for SystemHealth table"""
    
    def record_snapshot(
        self,
        cpu_usage_percent: float,
        db_size_bytes: int,
        photo_storage_bytes: int,
        log_storage_bytes: int,
        total_families: int,
        total_members: int,
        active_users: int
    ):
        """Record system health snapshot"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO SystemHealth (
                    cpu_usage_percent, db_size_bytes, photo_storage_bytes,
                    log_storage_bytes, total_families, total_members, active_users
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cpu_usage_percent, db_size_bytes, photo_storage_bytes,
                log_storage_bytes, total_families, total_members, active_users
            ))
            
            # Keep only last 180 days of snapshots
            cursor.execute("""
                DELETE FROM SystemHealth
                WHERE snapshot_time < datetime('now', '-180 days')
            """)
    
    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get most recent health snapshot"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM SystemHealth
                ORDER BY snapshot_time DESC
                LIMIT 1
            """)
            return self._row_to_dict(cursor.fetchone())
    
    def get_snapshots(
        self,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get health snapshots for last N days"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM SystemHealth
                WHERE snapshot_time >= datetime('now', '-' || ? || ' days')
                ORDER BY snapshot_time DESC
                LIMIT ?
            """, (days, limit))
            
            return self._rows_to_list(cursor.fetchall())
    
    def get_storage_breakdown(self) -> Dict[str, int]:
        """Get current storage breakdown"""
        snapshot = self.get_latest_snapshot()
        if not snapshot:
            return {
                'database': 0,
                'photos': 0,
                'logs': 0,
                'total': 0
            }
        
        return {
            'database': snapshot['db_size_bytes'],
            'photos': snapshot['photo_storage_bytes'],
            'logs': snapshot['log_storage_bytes'],
            'total': snapshot['db_size_bytes'] + snapshot['photo_storage_bytes'] + snapshot['log_storage_bytes']
        }


class CrashReportDAO(BaseDAO):
    """Data Access Object for CrashReports table"""
    
    MAX_CRASH_REPORTS = 100
    
    def create_crash_report(
        self,
        error_type: str,
        stack_trace: str,
        user_action_history: List[Dict[str, Any]],
        app_version: str,
        os_version: str,
        user_id: Optional[int] = None,
        user_role: Optional[str] = None
    ) -> int:
        """
        Create new crash report
        
        Args:
            error_type: Type of error (exception class name)
            stack_trace: Full stack trace
            user_action_history: List of last 10 user actions
            app_version: Application version
            os_version: Operating system version
            user_id: Current user ID (if logged in)
            user_role: Current user role
        
        Returns:
            int: New crash_id
        """
        action_history_json = json.dumps(user_action_history)
        
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO CrashReports (
                    error_type, stack_trace, user_action_history,
                    app_version, os_version, user_id, user_role
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                error_type, stack_trace, action_history_json,
                app_version, os_version, user_id, user_role
            ))
            
            crash_id = cursor.lastrowid
            logger.error(f"Crash report created: ID {crash_id}, Type: {error_type}")
            
            # Keep only last 100 crash reports
            cursor.execute("""
                DELETE FROM CrashReports
                WHERE crash_id NOT IN (
                    SELECT crash_id FROM CrashReports
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
            """, (self.MAX_CRASH_REPORTS,))
            
            return crash_id
    
    def get_crash_report(self, crash_id: int) -> Optional[Dict[str, Any]]:
        """Get crash report by ID"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT cr.*, u.email AS user_email
                FROM CrashReports cr
                LEFT JOIN Users u ON cr.user_id = u.user_id
                WHERE cr.crash_id = ?
            """, (crash_id,))
            
            report = self._row_to_dict(cursor.fetchone())
            
            if report and report['user_action_history']:
                try:
                    report['action_history'] = json.loads(report['user_action_history'])
                except:
                    report['action_history'] = []
            
            return report
    
    def get_all_crash_reports(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all crash reports"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    crash_id, timestamp, error_type, app_version, os_version,
                    user_role, (SELECT email FROM Users WHERE user_id = cr.user_id) AS user_email
                FROM CrashReports cr
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return self._rows_to_list(cursor.fetchall())
    
    def get_crash_count(self, days: int = 30) -> int:
        """Get crash count for last N days"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM CrashReports
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
            """, (days,))
            
            return cursor.fetchone()['count']


# Initialize global DAO instances
audit_log_dao = AuditLogDAO()
duplicate_alert_dao = DuplicateFamilyAlertDAO()
app_settings_dao = AppSettingsDAO()
system_health_dao = SystemHealthDAO()
crash_report_dao = CrashReportDAO()


if __name__ == "__main__":
    # Test utility DAOs
    print("Testing Utility DAOs...")
    try:
        # Test app settings
        settings = app_settings_dao.get_all_settings()
        print(f"✓ App settings loaded: {len(settings)} settings")
        
        # Test predefined colors
        colors = app_settings_dao.get_predefined_colors()
        print(f"✓ Predefined colors: {len(colors)} colors available")
        
        # Test health snapshot
        latest_health = system_health_dao.get_latest_snapshot()
        if latest_health:
            print(f"✓ Latest health snapshot: {latest_health['snapshot_time']}")
        else:
            print("  (No health snapshots yet)")
        
        print("\n✓ Utility DAO module ready!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
