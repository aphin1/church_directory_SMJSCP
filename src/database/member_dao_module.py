"""
Church Directory Management System - Member & Departed Member DAOs
Version: 2.0

Data Access Objects for Members, DepartedMembers, and related operations
including spouse linking for all in-law relationships.
"""

import sqlite3
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import date

from db_connection import BaseDAO, DatabaseError, db

logger = logging.getLogger(__name__)


class MemberDAO(BaseDAO):
    """Data Access Object for Members table"""
    
    # All in-law relationship types
    IN_LAW_RELATIONS = ['Son-in-law', 'Daughter-in-law']
    
    def create_member(
        self,
        family_id: int,
        name: str,
        gender: str,
        relation: str,
        birth_day: Optional[int] = None,
        birth_month: Optional[int] = None,
        birth_year: Optional[int] = None,
        marriage_day: Optional[int] = None,
        marriage_month: Optional[int] = None,
        marriage_year: Optional[int] = None,
        profession: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_head_of_family: bool = False,
        spouse_member_id: Optional[int] = None
    ) -> int:
        """
        Create new family member
        
        Args:
            family_id: Family this member belongs to
            name: Member name
            gender: Male, Female, or Other
            relation: Relationship to family (Head of Family, Spouse, Son, Daughter, 
                     Son-in-law, Daughter-in-law, Parent, Sibling, Other)
            birth_day: Day of birth (1-31)
            birth_month: Month of birth (1-12)
            birth_year: Year of birth (optional)
            marriage_day: Day of marriage (1-31, optional)
            marriage_month: Month of marriage (1-12, optional)
            marriage_year: Year of marriage (optional)
            profession: Member's profession
            email: Unique email address (used for access control)
            phone: Phone number (international format)
            is_head_of_family: Whether this is the head of family
            spouse_member_id: For in-laws, links to son/daughter member_id
        
        Returns:
            int: New member_id
        
        Raises:
            DatabaseError: If validation fails or constraints violated
        """
        # Validate in-law spouse requirement
        if relation in self.IN_LAW_RELATIONS and not spouse_member_id:
            raise DatabaseError(f"{relation} must have a spouse selected")
        
        # Validate date fields
        if (birth_day and not birth_month) or (birth_month and not birth_day):
            raise DatabaseError("Birth day and month must both be provided or both be null")
        
        if (marriage_day and not marriage_month) or (marriage_month and not marriage_day):
            raise DatabaseError("Marriage day and month must both be provided or both be null")
        
        with self.db.get_cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO Members (
                        family_id, name, gender, relation, spouse_member_id,
                        birth_day, birth_month, birth_year,
                        marriage_day, marriage_month, marriage_year,
                        profession, email, phone, is_head_of_family
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    family_id, name, gender, relation, spouse_member_id,
                    birth_day, birth_month, birth_year,
                    marriage_day, marriage_month, marriage_year,
                    profession, email, phone, is_head_of_family
                ))
                
                member_id = cursor.lastrowid
                logger.info(f"Member created: {name} (ID: {member_id}, Family: {family_id})")
                return member_id
                
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed: Members.email' in str(e):
                    raise DatabaseError(f"Email already exists: {email}")
                elif 'Family already has a Head of Family' in str(e):
                    raise DatabaseError("Family already has a Head of Family")
                raise DatabaseError(f"Member creation failed: {e}")
    
    def get_member(self, member_id: int) -> Optional[Dict[str, Any]]:
        """Get member by ID"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM Members WHERE member_id = ?", (member_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_family_members(
        self,
        family_id: int,
        include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all members of a family"""
        with self.db.get_cursor() as cursor:
            deleted_condition = "" if include_deleted else "AND is_deleted = 0"
            
            cursor.execute(f"""
                SELECT * FROM Members
                WHERE family_id = ? {deleted_condition}
                ORDER BY 
                    CASE 
                        WHEN is_head_of_family = 1 THEN 0
                        WHEN relation = 'Spouse' THEN 1
                        ELSE 2
                    END,
                    birth_year DESC NULLS LAST
            """, (family_id,))
            
            return self._rows_to_list(cursor.fetchall())
    
    def get_potential_spouses_for_inlaw(
        self,
        family_id: int,
        inlaw_relation: str
    ) -> List[Dict[str, Any]]:
        """
        Get potential spouse options for in-law selection
        
        Args:
            family_id: Family ID
            inlaw_relation: 'Son-in-law' or 'Daughter-in-law'
        
        Returns:
            List of sons (for daughter-in-law) or daughters (for son-in-law)
        """
        if inlaw_relation not in self.IN_LAW_RELATIONS:
            return []
        
        # Son-in-law links to Daughter, Daughter-in-law links to Son
        target_relation = 'Daughter' if inlaw_relation == 'Son-in-law' else 'Son'
        
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT member_id, name, birth_year
                FROM Members
                WHERE family_id = ? 
                AND relation = ?
                AND is_deleted = 0
                ORDER BY name
            """, (family_id, target_relation))
            
            return self._rows_to_list(cursor.fetchall())
    
    def get_spouse_info(self, member_id: int) -> Optional[Dict[str, Any]]:
        """Get spouse information for a member (used for anniversary display)"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT m2.member_id, m2.name, m2.relation
                FROM Members m1
                JOIN Members m2 ON m1.spouse_member_id = m2.member_id
                WHERE m1.member_id = ?
            """, (member_id,))
            
            return self._row_to_dict(cursor.fetchone())
    
    def update_member(
        self,
        member_id: int,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        relation: Optional[str] = None,
        birth_day: Optional[int] = None,
        birth_month: Optional[int] = None,
        birth_year: Optional[int] = None,
        marriage_day: Optional[int] = None,
        marriage_month: Optional[int] = None,
        marriage_year: Optional[int] = None,
        profession: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_head_of_family: Optional[bool] = None,
        spouse_member_id: Optional[int] = None
    ):
        """Update member information"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if gender is not None:
            updates.append("gender = ?")
            params.append(gender)
        
        if relation is not None:
            updates.append("relation = ?")
            params.append(relation)
        
        if birth_day is not None:
            updates.append("birth_day = ?")
            params.append(birth_day)
        
        if birth_month is not None:
            updates.append("birth_month = ?")
            params.append(birth_month)
        
        if birth_year is not None:
            updates.append("birth_year = ?")
            params.append(birth_year)
        
        if marriage_day is not None:
            updates.append("marriage_day = ?")
            params.append(marriage_day)
        
        if marriage_month is not None:
            updates.append("marriage_month = ?")
            params.append(marriage_month)
        
        if marriage_year is not None:
            updates.append("marriage_year = ?")
            params.append(marriage_year)
        
        if profession is not None:
            updates.append("profession = ?")
            params.append(profession)
        
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        
        if is_head_of_family is not None:
            updates.append("is_head_of_family = ?")
            params.append(is_head_of_family)
        
        if spouse_member_id is not None:
            updates.append("spouse_member_id = ?")
            params.append(spouse_member_id)
        
        if not updates:
            return
        
        params.append(member_id)
        
        with self.db.get_cursor() as cursor:
            try:
                cursor.execute(f"""
                    UPDATE Members 
                    SET {', '.join(updates)}
                    WHERE member_id = ?
                """, params)
                logger.info(f"Member updated: ID {member_id}")
            except sqlite3.IntegrityError as e:
                raise DatabaseError(f"Member update failed: {e}")
    
    def soft_delete_member(self, member_id: int, reason: str):
        """
        Soft delete member
        
        Args:
            member_id: Member to delete
            reason: Mandatory deletion reason (10-500 characters)
        """
        if len(reason) < 10 or len(reason) > 500:
            raise DatabaseError("Deletion reason must be 10-500 characters")
        
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE Members 
                SET is_deleted = 1, 
                    deleted_at = CURRENT_TIMESTAMP,
                    deletion_reason = ?
                WHERE member_id = ?
            """, (reason, member_id))
            logger.info(f"Member soft deleted: ID {member_id}")
    
    def restore_member(self, member_id: int):
        """Restore soft-deleted member"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE Members 
                SET is_deleted = 0, 
                    deleted_at = NULL,
                    deletion_reason = NULL
                WHERE member_id = ?
            """, (member_id,))
            logger.info(f"Member restored: ID {member_id}")
    
    def get_birthdays_for_week(
        self,
        week_start: date,
        week_end: date
    ) -> List[Dict[str, Any]]:
        """
        Get birthdays for a specific week
        
        Args:
            week_start: Start date of week (Sunday)
            week_end: End date of week (Saturday)
        
        Returns:
            List of members with birthdays in the week
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    m.member_id, m.name, m.birth_day, m.birth_month, m.birth_year,
                    f.family_name, pg.group_name AS prayer_group_name
                FROM Members m
                JOIN Families f ON m.family_id = f.family_id
                JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
                WHERE m.is_deleted = 0 
                AND f.is_deleted = 0
                AND m.birth_month IS NOT NULL
                AND m.birth_day IS NOT NULL
                ORDER BY m.birth_month, m.birth_day
            """)
            
            all_birthdays = self._rows_to_list(cursor.fetchall())
            
            # Filter for current week
            week_birthdays = []
            for member in all_birthdays:
                # Create a date object for comparison (use current year)
                try:
                    birthday_date = date(week_start.year, member['birth_month'], member['birth_day'])
                    
                    # Handle year wrap (December to January)
                    if birthday_date < week_start and week_start.month == 12:
                        birthday_date = birthday_date.replace(year=week_start.year + 1)
                    
                    if week_start <= birthday_date <= week_end:
                        # Calculate age if birth year available
                        if member['birth_year']:
                            member['age'] = week_start.year - member['birth_year']
                        else:
                            member['age'] = None
                        week_birthdays.append(member)
                except ValueError:
                    # Invalid date (e.g., Feb 30)
                    continue
            
            return week_birthdays
    
    def get_anniversaries_for_week(
        self,
        week_start: date,
        week_end: date
    ) -> List[Dict[str, Any]]:
        """
        Get wedding anniversaries for a specific week
        Includes proper spouse pairing for all relationships including in-laws
        
        Args:
            week_start: Start date of week (Sunday)
            week_end: End date of week (Saturday)
        
        Returns:
            List of couples with anniversaries in the week
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    m1.member_id, m1.name, m1.relation,
                    m1.marriage_day, m1.marriage_month, m1.marriage_year,
                    m2.member_id AS spouse_id, m2.name AS spouse_name, m2.relation AS spouse_relation,
                    f.family_name, pg.group_name AS prayer_group_name
                FROM Members m1
                JOIN Families f ON m1.family_id = f.family_id
                JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
                LEFT JOIN Members m2 ON m1.spouse_member_id = m2.member_id
                WHERE m1.is_deleted = 0 
                AND f.is_deleted = 0
                AND m1.marriage_month IS NOT NULL
                AND m1.marriage_day IS NOT NULL
                AND m1.relation IN ('Head of Family', 'Son', 'Daughter', 'Son-in-law', 'Daughter-in-law')
                ORDER BY m1.marriage_month, m1.marriage_day
            """)
            
            all_anniversaries = self._rows_to_list(cursor.fetchall())
            
            # Filter for current week and format display names
            week_anniversaries = []
            for couple in all_anniversaries:
                try:
                    anniversary_date = date(week_start.year, couple['marriage_month'], couple['marriage_day'])
                    
                    # Handle year wrap
                    if anniversary_date < week_start and week_start.month == 12:
                        anniversary_date = anniversary_date.replace(year=week_start.year + 1)
                    
                    if week_start <= anniversary_date <= week_end:
                        # Calculate years married if marriage year available
                        if couple['marriage_year']:
                            couple['years_married'] = week_start.year - couple['marriage_year']
                        else:
                            couple['years_married'] = None
                        
                        # Format couple display name
                        if couple['spouse_name']:
                            # In-law case: "John (Son) & Mary (Daughter-in-law)"
                            if couple['relation'] in self.IN_LAW_RELATIONS:
                                couple['couple_display'] = f"{couple['spouse_name']} ({couple['spouse_relation']}) & {couple['name']} ({couple['relation']})"
                            else:
                                couple['couple_display'] = f"{couple['name']} ({couple['relation']}) & {couple['spouse_name']} ({couple['spouse_relation']})"
                        else:
                            # Fallback if spouse not linked (shouldn't happen but handle gracefully)
                            couple['couple_display'] = f"{couple['name']} ({couple['relation']})"
                        
                        week_anniversaries.append(couple)
                except ValueError:
                    continue
            
            return week_anniversaries
    
    def get_member_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get member by email (used for access control)"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT m.*, f.family_name, pg.group_name AS prayer_group_name
                FROM Members m
                JOIN Families f ON m.family_id = f.family_id
                JOIN PrayerGroups pg ON f.prayer_group_id = pg.group_id
                WHERE m.email = ? AND m.is_deleted = 0
            """, (email,))
            
            return self._row_to_dict(cursor.fetchone())


class DepartedMemberDAO(BaseDAO):
    """Data Access Object for DepartedMembers table"""
    
    def create_departed_member(
        self,
        family_id: int,
        name: str,
        gender: str,
        relation: str,
        death_day: int,
        death_month: int,
        death_year: Optional[int] = None,
        birth_day: Optional[int] = None,
        birth_month: Optional[int] = None,
        birth_year: Optional[int] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Create new departed member record
        
        Args:
            family_id: Family this member belonged to
            name: Member name
            gender: Male, Female, or Other
            relation: Relationship to family
            death_day: Day of death (1-31, required)
            death_month: Month of death (1-12, required)
            death_year: Year of death (optional)
            birth_day: Day of birth (1-31, optional)
            birth_month: Month of birth (1-12, optional)
            birth_year: Year of birth (optional)
            notes: Additional notes (burial location, etc.)
        
        Returns:
            int: New departed_id
        """
        # Validate date fields
        if (birth_day and not birth_month) or (birth_month and not birth_day):
            raise DatabaseError("Birth day and month must both be provided or both be null")
        
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO DepartedMembers (
                    family_id, name, gender, relation,
                    death_day, death_month, death_year,
                    birth_day, birth_month, birth_year,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                family_id, name, gender, relation,
                death_day, death_month, death_year,
                birth_day, birth_month, birth_year,
                notes
            ))
            
            departed_id = cursor.lastrowid
            logger.info(f"Departed member created: {name} (ID: {departed_id}, Family: {family_id})")
            return departed_id
    
    def get_departed_member(self, departed_id: int) -> Optional[Dict[str, Any]]:
        """Get departed member by ID"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM DepartedMembers WHERE departed_id = ?", (departed_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_family_departed_members(
        self,
        family_id: int,
        include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all departed members of a family"""
        with self.db.get_cursor() as cursor:
            deleted_condition = "" if include_deleted else "AND is_deleted = 0"
            
            cursor.execute(f"""
                SELECT * FROM DepartedMembers
                WHERE family_id = ? {deleted_condition}
                ORDER BY death_year DESC NULLS LAST, death_month DESC, death_day DESC
            """, (family_id,))
            
            return self._rows_to_list(cursor.fetchall())
    
    def update_departed_member(
        self,
        departed_id: int,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        relation: Optional[str] = None,
        death_day: Optional[int] = None,
        death_month: Optional[int] = None,
        death_year: Optional[int] = None,
        birth_day: Optional[int] = None,
        birth_month: Optional[int] = None,
        birth_year: Optional[int] = None,
        notes: Optional[str] = None
    ):
        """Update departed member information"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if gender is not None:
            updates.append("gender = ?")
            params.append(gender)
        
        if relation is not None:
            updates.append("relation = ?")
            params.append(relation)
        
        if death_day is not None:
            updates.append("death_day = ?")
            params.append(death_day)
        
        if death_month is not None:
            updates.append("death_month = ?")
            params.append(death_month)
        
        if death_year is not None:
            updates.append("death_year = ?")
            params.append(death_year)
        
        if birth_day is not None:
            updates.append("birth_day = ?")
            params.append(birth_day)
        
        if birth_month is not None:
            updates.append("birth_month = ?")
            params.append(birth_month)
        
        if birth_year is not None:
            updates.append("birth_year = ?")
            params.append(birth_year)
        
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        
        if not updates:
            return
        
        params.append(departed_id)
        
        with self.db.get_cursor() as cursor:
            cursor.execute(f"""
                UPDATE DepartedMembers 
                SET {', '.join(updates)}
                WHERE departed_id = ?
            """, params)
            logger.info(f"Departed member updated: ID {departed_id}")
    
    def soft_delete_departed_member(self, departed_id: int, reason: str):
        """
        Soft delete departed member
        
        Args:
            departed_id: Departed member to delete
            reason: Mandatory deletion reason (10-500 characters)
        """
        if len(reason) < 10 or len(reason) > 500:
            raise DatabaseError("Deletion reason must be 10-500 characters")
        
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE DepartedMembers 
                SET is_deleted = 1, 
                    deleted_at = CURRENT_TIMESTAMP,
                    deletion_reason = ?
                WHERE departed_id = ?
            """, (reason, departed_id))
            logger.info(f"Departed member soft deleted: ID {departed_id}")
    
    def restore_departed_member(self, departed_id: int):
        """Restore soft-deleted departed member"""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE DepartedMembers 
                SET is_deleted = 0, 
                    deleted_at = NULL,
                    deletion_reason = NULL
                WHERE departed_id = ?
            """, (departed_id,))
            logger.info(f"Departed member restored: ID {departed_id}")


# Initialize global DAO instances
member_dao = MemberDAO()
departed_member_dao = DepartedMemberDAO()


if __name__ == "__main__":
    # Test member operations
    print("Testing Member DAO...")
    try:
        # Test getting potential spouses for in-law
        spouses = member_dao.get_potential_spouses_for_inlaw(1, 'Son-in-law')
        print(f"✓ Potential spouses query works: {len(spouses)} results")
        
        print("\n✓ Member DAO module ready!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
