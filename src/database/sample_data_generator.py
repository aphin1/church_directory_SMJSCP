"""
Church Directory Management System - Sample Data Generator
Version: 2.0

Generates realistic test data including:
- 3 prayer groups with unique colors
- 50+ families across prayer groups
- 200+ members with realistic Indian Christian names
- In-law relationships with spouse linking
- Dates with and without years (testing optional year feature)
- Duplicate family names for alert testing
- Departed members
- Initial admin users
"""

import random
import logging
from datetime import date, timedelta
from argon2 import PasswordHasher

# Import DAO classes
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from db_connection import db, user_dao, prayer_group_dao, family_dao
from member_dao_module import member_dao, departed_member_dao
from utility_dao_module import audit_log_dao

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ph = PasswordHasher()


# Sample data lists
KERALA_CHRISTIAN_SURNAMES = [
    'Thomas', 'Mathew', 'John', 'Joseph', 'George', 'Abraham', 'Jacob', 
    'Samuel', 'Daniel', 'David', 'Benjamin', 'Paul', 'Philip', 'Simon',
    'Stephen', 'Peter', 'Michael', 'Gabriel', 'Emmanuel', 'Joshua',
    'Zachariah', 'Isaac', 'Luke', 'Mark', 'Elias', 'Moses', 'Aaron',
    'Reuben', 'Solomon', 'Timothy', 'Titus', 'James', 'Andrew'
]

MALE_FIRST_NAMES = [
    'Abraham', 'Alexander', 'Benjamin', 'Daniel', 'David', 'Emmanuel',
    'George', 'Isaac', 'Jacob', 'James', 'John', 'Joseph', 'Joshua',
    'Luke', 'Mark', 'Mathew', 'Michael', 'Moses', 'Paul', 'Peter',
    'Philip', 'Reuben', 'Samuel', 'Simon', 'Solomon', 'Stephen', 'Thomas',
    'Timothy', 'Zachariah', 'Aaron', 'Andrew', 'Elias', 'Gabriel'
]

FEMALE_FIRST_NAMES = [
    'Anna', 'Elizabeth', 'Esther', 'Grace', 'Hannah', 'Leah', 'Lydia',
    'Maria', 'Martha', 'Mary', 'Miriam', 'Naomi', 'Rachel', 'Rebecca',
    'Ruth', 'Sarah', 'Susan', 'Tabitha', 'Abigail', 'Deborah', 'Eve',
    'Joanna', 'Julia', 'Magdalene', 'Phoebe', 'Priscilla', 'Rhoda',
    'Salome', 'Susanna', 'Zipporah', 'Alice', 'Rose', 'Margaret'
]

PROFESSIONS = [
    'Engineer', 'Teacher', 'Doctor', 'Nurse', 'Accountant', 'Businessman',
    'Software Developer', 'Manager', 'Architect', 'Lawyer', 'Professor',
    'Pharmacist', 'Chef', 'Electrician', 'Plumber', 'Mechanic',
    'Sales Executive', 'Bank Officer', 'Government Employee', 'Retired',
    'Student', 'Homemaker', 'Farmer', 'Contractor', 'Technician'
]

KERALA_CITIES = [
    'Kochi', 'Thiruvananthapuram', 'Kozhikode', 'Thrissur', 'Kollam',
    'Palakkad', 'Alappuzha', 'Kannur', 'Kottayam', 'Ernakulam'
]

PARISHES = [
    'St. Thomas Cathedral', 'St. Mary\'s Church', 'Holy Family Church',
    'St. Joseph\'s Church', 'Sacred Heart Church', 'St. George Church',
    'St. Sebastian Church', 'Our Lady of Lourdes Church', 'St. Anthony\'s Church',
    'Christ Church', 'St. Paul\'s Church', 'St. Peter\'s Church'
]

PRAYER_GROUPS = [
    ('St. Mary\'s Group', '#E3F2FD'),
    ('St. Joseph\'s Group', '#E8F5E9'),
    ('Holy Family Group', '#F3E5F5')
]

# Families that will have duplicates (for testing duplicate alerts)
DUPLICATE_FAMILIES = ['Thomas', 'Abraham', 'John']


def generate_random_date(start_year: int, end_year: int, include_year: bool = True):
    """Generate random date with optional year"""
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Safe for all months
    
    if include_year:
        year = random.randint(start_year, end_year)
        return day, month, year
    else:
        return day, month, None


def generate_indian_phone():
    """Generate Indian phone number"""
    return f"+91-{random.randint(8000000000, 9999999999)}"


def generate_email(first_name: str, surname: str):
    """Generate email address"""
    return f"{first_name.lower()}.{surname.lower()}{random.randint(1, 999)}@email.com"


def generate_address(city: str):
    """Generate Kerala address"""
    street_num = random.randint(1, 999)
    streets = ['Church Street', 'Market Road', 'Temple Road', 'Station Road', 'Beach Road']
    return f"{street_num} {random.choice(streets)}, {city}, Kerala, India {random.randint(680001, 695999)}"


def create_prayer_groups():
    """Create prayer groups"""
    logger.info("Creating prayer groups...")
    
    group_ids = []
    for name, color in PRAYER_GROUPS:
        try:
            group_id = prayer_group_dao.create_prayer_group(name, color)
            group_ids.append(group_id)
            logger.info(f"Created prayer group: {name}")
        except Exception as e:
            logger.error(f"Failed to create prayer group {name}: {e}")
    
    return group_ids


def create_admin_users():
    """Create Super Admin and Admin users"""
    logger.info("Creating admin users...")
    
    users = []
    
    # Super Admin
    try:
        super_admin_id = user_dao.create_user(
            email='superadmin@church.org',
            password_hash=ph.hash('SuperAdmin@123'),
            role='Super Admin',
            recovery_code_hash=ph.hash('RECOVERY-CODE-ABC123XYZ789')
        )
        users.append(('Super Admin', 'superadmin@church.org', 'SuperAdmin@123'))
        logger.info("Created Super Admin user")
    except Exception as e:
        logger.error(f"Failed to create Super Admin: {e}")
    
    # Admin (Vicar)
    try:
        admin_id = user_dao.create_user(
            email='vicar@church.org',
            password_hash=ph.hash('Vicar@123'),
            role='Admin'
        )
        users.append(('Admin', 'vicar@church.org', 'Vicar@123'))
        logger.info("Created Admin user")
    except Exception as e:
        logger.error(f"Failed to create Admin: {e}")
    
    return users


def create_family_with_members(
    surname: str,
    prayer_group_id: int,
    include_inlaws: bool = False,
    include_departed: bool = False
):
    """
    Create a complete family with members
    
    Returns:
        tuple: (family_id, member_emails) for Add-Member user creation
    """
    city = random.choice(KERALA_CITIES)
    parish = random.choice(PARISHES)
    
    # Create family
    family_id = family_dao.create_family(
        family_name=surname,
        prayer_group_id=prayer_group_id,
        current_address=generate_address(city),
        home_address=generate_address(city) if random.random() > 0.5 else None,
        parish=parish
    )
    
    member_emails = []
    
    # Head of Family (40-70 years old)
    hof_first_name = random.choice(MALE_FIRST_NAMES)
    hof_birth = generate_random_date(1954, 1984, include_year=random.random() > 0.2)
    hof_email = generate_email(hof_first_name, surname)
    
    hof_id = member_dao.create_member(
        family_id=family_id,
        name=f"{hof_first_name} {surname}",
        gender='Male',
        relation='Head of Family',
        birth_day=hof_birth[0],
        birth_month=hof_birth[1],
        birth_year=hof_birth[2],
        profession=random.choice(PROFESSIONS),
        email=hof_email,
        phone=generate_indian_phone(),
        is_head_of_family=True
    )
    member_emails.append(hof_email)
    
    # Spouse (similar age)
    spouse_first_name = random.choice(FEMALE_FIRST_NAMES)
    spouse_birth = generate_random_date(1956, 1986, include_year=random.random() > 0.2)
    marriage_date = generate_random_date(1980, 2005, include_year=random.random() > 0.3)
    spouse_email = generate_email(spouse_first_name, surname)
    
    spouse_id = member_dao.create_member(
        family_id=family_id,
        name=f"{spouse_first_name} {surname}",
        gender='Female',
        relation='Spouse',
        birth_day=spouse_birth[0],
        birth_month=spouse_birth[1],
        birth_year=spouse_birth[2],
        marriage_day=marriage_date[0],
        marriage_month=marriage_date[1],
        marriage_year=marriage_date[2],
        profession=random.choice(PROFESSIONS),
        email=spouse_email,
        phone=generate_indian_phone()
    )
    member_emails.append(spouse_email)
    
    # Children (1-4 children)
    num_children = random.randint(1, 4)
    children_ids = []
    
    for i in range(num_children):
        is_son = random.random() > 0.5
        child_first_name = random.choice(MALE_FIRST_NAMES if is_son else FEMALE_FIRST_NAMES)
        child_birth = generate_random_date(1995, 2015, include_year=random.random() > 0.1)
        child_email = generate_email(child_first_name, surname)
        
        child_id = member_dao.create_member(
            family_id=family_id,
            name=f"{child_first_name} {surname}",
            gender='Male' if is_son else 'Female',
            relation='Son' if is_son else 'Daughter',
            birth_day=child_birth[0],
            birth_month=child_birth[1],
            birth_year=child_birth[2],
            profession='Student' if child_birth[2] and child_birth[2] > 2005 else random.choice(PROFESSIONS),
            email=child_email,
            phone=generate_indian_phone() if random.random() > 0.3 else None
        )
        children_ids.append((child_id, 'Son' if is_son else 'Daughter', child_first_name))
        member_emails.append(child_email)
    
    # Add in-laws if requested and children exist
    if include_inlaws and children_ids:
        # Pick a random child to have spouse
        child_id, child_relation, child_name = random.choice(children_ids)
        
        if child_relation == 'Son':
            # Add daughter-in-law
            inlaw_first_name = random.choice(FEMALE_FIRST_NAMES)
            inlaw_relation = 'Daughter-in-law'
            gender = 'Female'
        else:
            # Add son-in-law
            inlaw_first_name = random.choice(MALE_FIRST_NAMES)
            inlaw_relation = 'Son-in-law'
            gender = 'Male'
        
        inlaw_birth = generate_random_date(1995, 2015, include_year=random.random() > 0.1)
        inlaw_marriage = generate_random_date(2018, 2024, include_year=random.random() > 0.1)
        inlaw_email = generate_email(inlaw_first_name, 'inlaw')
        
        inlaw_id = member_dao.create_member(
            family_id=family_id,
            name=f"{inlaw_first_name} {surname}",
            gender=gender,
            relation=inlaw_relation,
            spouse_member_id=child_id,  # Link to child
            birth_day=inlaw_birth[0],
            birth_month=inlaw_birth[1],
            birth_year=inlaw_birth[2],
            marriage_day=inlaw_marriage[0],
            marriage_month=inlaw_marriage[1],
            marriage_year=inlaw_marriage[2],
            profession=random.choice(PROFESSIONS),
            email=inlaw_email,
            phone=generate_indian_phone()
        )
        member_emails.append(inlaw_email)
    
    # Add departed member if requested
    if include_departed:
        departed_first_name = random.choice(MALE_FIRST_NAMES if random.random() > 0.5 else FEMALE_FIRST_NAMES)
        departed_birth = generate_random_date(1920, 1960, include_year=random.random() > 0.3)
        departed_death = generate_random_date(2000, 2023, include_year=random.random() > 0.2)
        
        departed_member_dao.create_departed_member(
            family_id=family_id,
            name=f"{departed_first_name} {surname} Sr.",
            gender='Male' if random.random() > 0.5 else 'Female',
            relation='Parent',
            birth_day=departed_birth[0],
            birth_month=departed_birth[1],
            birth_year=departed_birth[2],
            death_day=departed_death[0],
            death_month=departed_death[1],
            death_year=departed_death[2],
            notes=f"Buried at {random.choice(PARISHES)} Cemetery" if random.random() > 0.5 else None
        )
    
    logger.info(f"Created family: {surname} (ID: {family_id}, Members: {len(member_emails)})")
    return family_id, member_emails


def generate_all_sample_data():
    """Generate complete sample dataset"""
    logger.info("=" * 70)
    logger.info("Starting sample data generation...")
    logger.info("=" * 70)
    
    # Create prayer groups
    prayer_group_ids = create_prayer_groups()
    
    if len(prayer_group_ids) < 3:
        logger.error("Failed to create all prayer groups. Aborting.")
        return
    
    # Create admin users
    admin_users = create_admin_users()
    
    # Create families
    logger.info("\nCreating families...")
    all_member_emails = []
    family_count = 0
    
    # Distribute families across prayer groups
    for i, surname in enumerate(KERALA_CHRISTIAN_SURNAMES):
        prayer_group_id = prayer_group_ids[i % len(prayer_group_ids)]
        
        # Determine if this family should have special features
        include_inlaws = random.random() > 0.7  # 30% chance
        include_departed = random.random() > 0.6  # 40% chance
        
        try:
            family_id, emails = create_family_with_members(
                surname=surname,
                prayer_group_id=prayer_group_id,
                include_inlaws=include_inlaws,
                include_departed=include_departed
            )
            all_member_emails.extend(emails)
            family_count += 1
        except Exception as e:
            logger.error(f"Failed to create family {surname}: {e}")
    
    # Create duplicate families (for testing duplicate alerts)
    logger.info("\nCreating duplicate families for testing...")
    for surname in DUPLICATE_FAMILIES:
        prayer_group_id = random.choice(prayer_group_ids)
        try:
            family_id, emails = create_family_with_members(
                surname=surname,
                prayer_group_id=prayer_group_id,
                include_inlaws=False,
                include_departed=False
            )
            all_member_emails.extend(emails)
            family_count += 1
        except Exception as e:
            logger.error(f"Failed to create duplicate family {surname}: {e}")
    
    # Create Add-Member users from existing members
    logger.info("\nCreating Add-Member users...")
    add_member_count = 0
    
    # Pick 5 random members to be Add-Member users
    sample_emails = random.sample(all_member_emails, min(5, len(all_member_emails)))
    
    for email in sample_emails:
        try:
            # Pick another random email as reference
            reference_email = random.choice([e for e in all_member_emails if e != email])
            
            user_dao.create_user(
                email=email,
                password_hash=ph.hash('Member@123'),
                role='Add-Member',
                reference_email=reference_email
            )
            add_member_count += 1
            logger.info(f"Created Add-Member user: {email}")
        except Exception as e:
            logger.error(f"Failed to create Add-Member user {email}: {e}")
    
    # Log summary action
    audit_log_dao.log_action(
        user_id=None,
        action='add',
        target_table='system',
        details={
            'action': 'sample_data_generation',
            'families_created': family_count,
            'prayer_groups_created': len(prayer_group_ids),
            'add_member_users_created': add_member_count
        }
    )
    
    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("SAMPLE DATA GENERATION COMPLETE!")
    logger.info("=" * 70)
    logger.info(f"Prayer Groups Created: {len(prayer_group_ids)}")
    logger.info(f"Families Created: {family_count}")
    logger.info(f"Total Member Emails: {len(all_member_emails)}")
    logger.info(f"Admin Users Created: {len(admin_users)}")
    logger.info(f"Add-Member Users Created: {add_member_count}")
    
    logger.info("\n📋 Admin User Credentials:")
    for role, email, password in admin_users:
        logger.info(f"  {role}: {email} / {password}")
    
    logger.info("\n📋 Add-Member User Credentials:")
    logger.info(f"  Any of the 5 created users / Member@123")
    
    logger.info("\n📊 Database Statistics:")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM Families")
    logger.info(f"  Total Families: {cursor.fetchone()['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM Members WHERE is_deleted = 0")
    logger.info(f"  Active Members: {cursor.fetchone()['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM DepartedMembers WHERE is_deleted = 0")
    logger.info(f"  Departed Members: {cursor.fetchone()['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM DuplicateFamilyAlerts WHERE is_resolved = 0")
    duplicate_count = cursor.fetchone()['count']
    logger.info(f"  Unresolved Duplicate Alerts: {duplicate_count}")
    
    cursor.execute("SELECT COUNT(*) as count FROM AuditLog")
    logger.info(f"  Audit Log Entries: {cursor.fetchone()['count']}")
    
    logger.info(f"\n💾 Database Size: {db.get_db_size() / 1024:.2f} KB")
    logger.info(f"📍 Database Location: {db._db_path}")
    
    logger.info("\n✅ Ready for testing!")
    logger.info("=" * 70)


if __name__ == "__main__":
    try:
        # Confirm before generating
        print("\n" + "=" * 70)
        print("CHURCH DIRECTORY - SAMPLE DATA GENERATOR")
        print("=" * 70)
        print("\nThis will generate:")
        print("  • 3 Prayer Groups")
        print("  • 50+ Families")
        print("  • 200+ Members")
        print("  • 10+ Departed Members")
        print("  • Duplicate family names (for alert testing)")
        print("  • Admin and Add-Member users")
        print("\n⚠️  WARNING: This will modify the database!")
        print(f"📍 Database: {db._db_path}")
        
        response = input("\nProceed with data generation? (yes/no): ").strip().lower()
        
        if response == 'yes':
            generate_all_sample_data()
        else:
            print("\n❌ Data generation cancelled.")
            
    except KeyboardInterrupt:
        print("\n\n❌ Data generation interrupted.")
    except Exception as e:
        logger.error(f"Fatal error during data generation: {e}")
        import traceback
        traceback.print_exc()
