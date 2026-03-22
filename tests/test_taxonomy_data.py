"""
Test taxonomy data population (TDD for migration 002)

Validates:
1. All canonical tags are created with correct hierarchy
2. Translations exist for deities (Kannada + Hindi)
3. Synonyms are mapped correctly from tag-migration-mapping.csv
4. Parent-child relationships work
5. No duplicate tags/synonyms
"""

import pytest
import sqlite3
from pathlib import Path


@pytest.fixture
def db_connection():
    """Create test database with migrations applied"""
    # Use in-memory database for tests
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    def execute_migration(file_path):
        """Execute a SQL migration file, filtering out comments and rollback sections"""
        with open(file_path) as f:
            sql = f.read()
            
        # Remove rollback section (everything after "-- ============================================================================")
        # that contains "ROLLBACK"
        lines = sql.split('\n')
        filtered_lines = []
        in_rollback_section = False
        
        for line in lines:
            # Detect rollback section start
            if 'ROLLBACK' in line and line.strip().startswith('--'):
                in_rollback_section = True
            
            # Skip lines in rollback section
            if in_rollback_section:
                continue
                
            # Skip standalone comment lines
            if line.strip().startswith('--'):
                continue
            
            filtered_lines.append(line)
        
        # Rejoin and split by semicolon
        cleaned_sql = '\n'.join(filtered_lines)
        
        for statement in cleaned_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    conn.execute(statement)
                except sqlite3.Error as e:
                    print(f"Error executing: {statement[:100]}...")
                    raise
    
    # Apply schema migration (001)
    schema_path = Path(__file__).parent.parent / 'migrations' / '001_create_tag_taxonomy.sql'
    execute_migration(schema_path)
    
    # Apply data migration (002)
    data_path = Path(__file__).parent.parent / 'migrations' / '002_populate_taxonomy.sql'
    execute_migration(data_path)
    
    conn.commit()
    yield conn
    conn.close()


class TestTagHierarchy:
    """Test deity tag hierarchy"""
    
    def test_root_deity_category_exists(self, db_connection):
        """Root 'Deity' category should exist"""
        cursor = db_connection.execute(
            "SELECT * FROM tag_taxonomy WHERE name = 'Deity' AND category = 'root'"
        )
        root = cursor.fetchone()
        assert root is not None, "Root 'Deity' tag missing"
        assert root['level'] == 0
        assert root['parent_id'] is None
    
    def test_level_1_deities_exist(self, db_connection):
        """Shiva, Vishnu, Devi, Ganesha should be level 1"""
        cursor = db_connection.execute(
            "SELECT name FROM tag_taxonomy WHERE category = 'deity' AND level = 1 ORDER BY name"
        )
        level_1 = [row['name'] for row in cursor.fetchall()]
        
        expected = ['Devi', 'Ganesha', 'Shiva', 'Vishnu']
        assert level_1 == expected, f"Expected {expected}, got {level_1}"
    
    def test_hanuman_parent_is_shiva(self, db_connection):
        """Hanuman should be child of Shiva"""
        cursor = db_connection.execute("""
            SELECT t1.name as child, t2.name as parent
            FROM tag_taxonomy t1
            JOIN tag_taxonomy t2 ON t1.parent_id = t2.id
            WHERE t1.name = 'Hanuman'
        """)
        row = cursor.fetchone()
        assert row is not None, "Hanuman not found or has no parent"
        assert row['parent'] == 'Shiva', f"Hanuman parent should be Shiva, got {row['parent']}"
    
    def test_krishna_parent_is_vishnu(self, db_connection):
        """Krishna should be child of Vishnu"""
        cursor = db_connection.execute("""
            SELECT t1.name as child, t2.name as parent
            FROM tag_taxonomy t1
            JOIN tag_taxonomy t2 ON t1.parent_id = t2.id
            WHERE t1.name = 'Krishna'
        """)
        row = cursor.fetchone()
        assert row is not None, "Krishna not found or has no parent"
        assert row['parent'] == 'Vishnu', f"Krishna parent should be Vishnu, got {row['parent']}"
    
    def test_rama_parent_is_vishnu(self, db_connection):
        """Rama should be child of Vishnu"""
        cursor = db_connection.execute("""
            SELECT t1.name as child, t2.name as parent
            FROM tag_taxonomy t1
            JOIN tag_taxonomy t2 ON t1.parent_id = t2.id
            WHERE t1.name = 'Rama'
        """)
        row = cursor.fetchone()
        assert row is not None, "Rama not found or has no parent"
        assert row['parent'] == 'Vishnu', f"Rama parent should be Vishnu, got {row['parent']}"


class TestTagTypes:
    """Test bhajan type tags"""
    
    def test_all_types_exist(self, db_connection):
        """Bhajan, Stotra, Aarti, Chalisa, Kirtan, Mantra should exist"""
        cursor = db_connection.execute(
            "SELECT name FROM tag_taxonomy WHERE category = 'type' ORDER BY name"
        )
        types = [row['name'] for row in cursor.fetchall()]
        
        expected = ['Aarti', 'Bhajan', 'Chalisa', 'Kirtan', 'Mantra', 'Stotra']
        assert types == expected, f"Expected {expected}, got {types}"


class TestComposers:
    """Test composer tags"""
    
    def test_major_composers_exist(self, db_connection):
        """Purandara Dasa, Tyagaraja, Kanaka Dasa should exist"""
        cursor = db_connection.execute(
            "SELECT name FROM tag_taxonomy WHERE category = 'composer' ORDER BY name"
        )
        composers = [row['name'] for row in cursor.fetchall()]
        
        # At minimum these should exist
        required = ['Kanaka Dasa', 'Purandara Dasa', 'Tyagaraja']
        for composer in required:
            assert composer in composers, f"Composer '{composer}' missing"


class TestLanguages:
    """Test language tags"""
    
    def test_all_languages_exist(self, db_connection):
        """Kannada, Hindi, Sanskrit, Telugu, Tamil, English should exist"""
        cursor = db_connection.execute(
            "SELECT name FROM tag_taxonomy WHERE category = 'theme' AND name IN ('Kannada', 'Hindi', 'Sanskrit', 'Telugu', 'Tamil', 'English') ORDER BY name"
        )
        languages = [row['name'] for row in cursor.fetchall()]
        
        expected = ['English', 'Hindi', 'Kannada', 'Sanskrit', 'Tamil', 'Telugu']
        assert languages == expected, f"Expected {expected}, got {languages}"


class TestOccasions:
    """Test occasion tags"""
    
    def test_all_occasions_exist(self, db_connection):
        """Morning, Evening, Festival, Temple should exist"""
        cursor = db_connection.execute(
            "SELECT name FROM tag_taxonomy WHERE category = 'occasion' ORDER BY name"
        )
        occasions = [row['name'] for row in cursor.fetchall()]
        
        expected = ['Evening', 'Festival', 'Morning', 'Temple']
        assert occasions == expected, f"Expected {expected}, got {occasions}"


class TestTranslations:
    """Test tag translations"""
    
    def test_hanuman_has_kannada_translation(self, db_connection):
        """Hanuman should have Kannada translation"""
        cursor = db_connection.execute("""
            SELECT t.translation
            FROM tag_translations t
            JOIN tag_taxonomy tax ON t.tag_id = tax.id
            WHERE tax.name = 'Hanuman' AND t.language = 'kn'
        """)
        row = cursor.fetchone()
        assert row is not None, "Hanuman missing Kannada translation"
        assert row['translation'] == 'ಹನುಮಾನ್', f"Expected 'ಹನುಮಾನ್', got '{row['translation']}'"
    
    def test_hanuman_has_hindi_translation(self, db_connection):
        """Hanuman should have Hindi translation"""
        cursor = db_connection.execute("""
            SELECT t.translation
            FROM tag_translations t
            JOIN tag_taxonomy tax ON t.tag_id = tax.id
            WHERE tax.name = 'Hanuman' AND t.language = 'hi'
        """)
        row = cursor.fetchone()
        assert row is not None, "Hanuman missing Hindi translation"
        assert row['translation'] == 'हनुमान', f"Expected 'हनुमान', got '{row['translation']}'"
    
    def test_all_deities_have_translations(self, db_connection):
        """All level 1 & 2 deities should have Kannada + Hindi translations"""
        cursor = db_connection.execute("""
            SELECT tax.name, COUNT(DISTINCT t.language) as lang_count
            FROM tag_taxonomy tax
            LEFT JOIN tag_translations t ON tax.id = t.tag_id
            WHERE tax.category = 'deity' AND tax.level > 0
            GROUP BY tax.id, tax.name
        """)
        
        for row in cursor.fetchall():
            assert row['lang_count'] >= 2, f"{row['name']} missing translations (has {row['lang_count']}, need 2+)"


class TestSynonyms:
    """Test tag synonyms from migration mapping"""
    
    def test_anjaneya_synonym_exists(self, db_connection):
        """Anjaneya should be synonym for Hanuman"""
        cursor = db_connection.execute("""
            SELECT tax.name
            FROM tag_synonyms syn
            JOIN tag_taxonomy tax ON syn.tag_id = tax.id
            WHERE syn.synonym = 'Anjaneya'
        """)
        row = cursor.fetchone()
        assert row is not None, "Anjaneya synonym missing"
        assert row['name'] == 'Hanuman', f"Anjaneya should map to Hanuman, got {row['name']}"
    
    def test_maruti_synonym_exists(self, db_connection):
        """Maruti should be synonym for Hanuman"""
        cursor = db_connection.execute("""
            SELECT tax.name
            FROM tag_synonyms syn
            JOIN tag_taxonomy tax ON syn.tag_id = tax.id
            WHERE syn.synonym = 'maruti'
        """)
        row = cursor.fetchone()
        assert row is not None, "maruti synonym missing"
        assert row['name'] == 'Hanuman', f"maruti should map to Hanuman, got {row['name']}"
    
    def test_vijaya_maruti_synonym_exists(self, db_connection):
        """Vijaya Maruti should be synonym for Hanuman"""
        cursor = db_connection.execute("""
            SELECT tax.name
            FROM tag_synonyms syn
            JOIN tag_taxonomy tax ON syn.tag_id = tax.id
            WHERE syn.synonym = 'Vijaya Maruti'
        """)
        row = cursor.fetchone()
        assert row is not None, "Vijaya Maruti synonym missing"
        assert row['name'] == 'Hanuman', f"Vijaya Maruti should map to Hanuman, got {row['name']}"
    
    def test_no_duplicate_synonyms(self, db_connection):
        """Each synonym should appear only once"""
        cursor = db_connection.execute("""
            SELECT synonym, COUNT(*) as count
            FROM tag_synonyms
            GROUP BY synonym
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        assert len(duplicates) == 0, f"Duplicate synonyms found: {[d['synonym'] for d in duplicates]}"


class TestDataIntegrity:
    """Test overall data integrity"""
    
    def test_no_orphaned_translations(self, db_connection):
        """All translations should reference valid tags"""
        cursor = db_connection.execute("""
            SELECT t.id
            FROM tag_translations t
            LEFT JOIN tag_taxonomy tax ON t.tag_id = tax.id
            WHERE tax.id IS NULL
        """)
        orphans = cursor.fetchall()
        assert len(orphans) == 0, f"Found {len(orphans)} orphaned translations"
    
    def test_no_orphaned_synonyms(self, db_connection):
        """All synonyms should reference valid tags"""
        cursor = db_connection.execute("""
            SELECT s.id
            FROM tag_synonyms s
            LEFT JOIN tag_taxonomy tax ON s.tag_id = tax.id
            WHERE tax.id IS NULL
        """)
        orphans = cursor.fetchall()
        assert len(orphans) == 0, f"Found {len(orphans)} orphaned synonyms"
    
    def test_no_duplicate_tag_names(self, db_connection):
        """Tag names should be unique"""
        cursor = db_connection.execute("""
            SELECT name, COUNT(*) as count
            FROM tag_taxonomy
            GROUP BY name
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        assert len(duplicates) == 0, f"Duplicate tag names: {[d['name'] for d in duplicates]}"
    
    def test_hierarchy_levels_consistent(self, db_connection):
        """Child level should be parent level + 1"""
        cursor = db_connection.execute("""
            SELECT t1.name, t1.level as child_level, t2.level as parent_level
            FROM tag_taxonomy t1
            JOIN tag_taxonomy t2 ON t1.parent_id = t2.id
            WHERE t1.level != t2.level + 1
        """)
        inconsistent = cursor.fetchall()
        assert len(inconsistent) == 0, f"Inconsistent levels: {[(r['name'], r['child_level'], r['parent_level']) for r in inconsistent]}"
