"""
Test configuration and fixtures for Belaguru Bhajans tests.

All tests should use these fixtures to ensure proper isolation:
- test_db: Provides an isolated in-memory SQLAlchemy session
- client: Provides a FastAPI TestClient with the test database
- test_db_path: Creates a temporary SQLite file for tests needing file-based DB

Tests should create their own data and validate against it.
Tests should NOT depend on production database state.
"""
import pytest
import tempfile
import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="function")
def test_db_path():
    """
    Create a temporary SQLite file for tests.
    
    Sets DATABASE_PATH and DATABASE_URL environment variables.
    Creates all tables from models.py.
    Returns the path to the database file.
    """
    # Create temporary file
    fd, db_path = tempfile.mkstemp(suffix='.db', prefix='test_bhajans_')
    os.close(fd)
    
    # Set environment variables BEFORE importing models
    os.environ["DATABASE_PATH"] = db_path
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    
    # Now import and set up
    # Force reimport of models to pick up new env vars
    if 'models' in sys.modules:
        del sys.modules['models']
    if 'main' in sys.modules:
        del sys.modules['main']
    if 'dual_write' in sys.modules:
        del sys.modules['dual_write']
    
    from models import Base
    
    # Create engine and all tables
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    engine.dispose()
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except:
            pass
    
    # Reset environment
    if "DATABASE_PATH" in os.environ:
        del os.environ["DATABASE_PATH"]
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]


@pytest.fixture(scope="function")
def test_engine(test_db_path):
    """Create an engine for the test database"""
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False}
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """
    Create isolated database session for each test.
    
    Yields a session connected to the test database.
    Session is automatically closed after the test.
    """
    Session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture(scope="function")
def client(test_db_path, test_db):
    """
    FastAPI test client with isolated database.
    
    Overrides the get_db dependency to use the test database.
    All API calls will use the test database.
    """
    from fastapi.testclient import TestClient
    
    # Force reimport of main with new database path
    if 'main' in sys.modules:
        del sys.modules['main']
    
    from main import app
    from models import get_db
    
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_bhajan(test_db):
    """
    Create a sample bhajan for tests.
    
    Returns the bhajan object after committing it to the test database.
    """
    # Force reimport to ensure we use test database
    if 'models' in sys.modules:
        del sys.modules['models']
    from models import Bhajan
    
    bhajan = Bhajan(
        title="Test Hanuman Chalisa",
        lyrics="Jai Hanuman gyan gun sagar, Jai Kapis tihun lok ujagar",
        tags='["Hanuman", "Chalisa"]',
        uploader_name="TestUser"
    )
    test_db.add(bhajan)
    test_db.commit()
    test_db.refresh(bhajan)
    
    return bhajan


@pytest.fixture
def sample_bhajans(test_db):
    """
    Create multiple sample bhajans for tests.
    
    Returns a list of bhajan objects.
    """
    if 'models' in sys.modules:
        del sys.modules['models']
    from models import Bhajan
    
    bhajans_data = [
        {
            "title": "Test Hanuman Chalisa",
            "lyrics": "Jai Hanuman gyan gun sagar, Jai Kapis tihun lok ujagar",
            "tags": '["Hanuman", "Chalisa"]',
            "uploader_name": "TestUser1"
        },
        {
            "title": "Test Krishna Bhajan",
            "lyrics": "Hare Krishna Hare Krishna, Krishna Krishna Hare Hare",
            "tags": '["Krishna", "Bhajan"]',
            "uploader_name": "TestUser2"
        },
        {
            "title": "Test Rama Stuti",
            "lyrics": "Sri Rama Rama Rameti, Rame Raame Manorame",
            "tags": '["Rama", "Stuti"]',
            "uploader_name": "TestUser3"
        }
    ]
    
    bhajans = []
    for data in bhajans_data:
        bhajan = Bhajan(**data)
        test_db.add(bhajan)
        bhajans.append(bhajan)
    
    test_db.commit()
    
    for bhajan in bhajans:
        test_db.refresh(bhajan)
    
    return bhajans


@pytest.fixture
def sample_tag_taxonomy(test_db):
    """
    Create sample tag taxonomy for tests.
    
    Creates a small hierarchy: Deity -> Vishnu -> Krishna, Rama
    """
    if 'models' in sys.modules:
        del sys.modules['models']
    from models import TagTaxonomy, TagTranslation, TagSynonym
    
    # Root category
    deity_root = TagTaxonomy(
        name="Deity",
        category="root",
        level=0
    )
    test_db.add(deity_root)
    test_db.flush()  # Get the ID
    
    # First level
    vishnu = TagTaxonomy(
        name="Vishnu",
        category="deity",
        level=1,
        parent_id=deity_root.id
    )
    test_db.add(vishnu)
    test_db.flush()
    
    shiva = TagTaxonomy(
        name="Shiva",
        category="deity",
        level=1,
        parent_id=deity_root.id
    )
    test_db.add(shiva)
    test_db.flush()
    
    # Second level
    krishna = TagTaxonomy(
        name="Krishna",
        category="deity",
        level=2,
        parent_id=vishnu.id
    )
    test_db.add(krishna)
    test_db.flush()
    
    rama = TagTaxonomy(
        name="Rama",
        category="deity",
        level=2,
        parent_id=vishnu.id
    )
    test_db.add(rama)
    test_db.flush()
    
    hanuman = TagTaxonomy(
        name="Hanuman",
        category="deity",
        level=2,
        parent_id=shiva.id
    )
    test_db.add(hanuman)
    test_db.flush()
    
    # Add translations for Hanuman
    hanuman_kn = TagTranslation(
        tag_id=hanuman.id,
        language="kn",
        translation="ಹನುಮಾನ್"
    )
    test_db.add(hanuman_kn)
    
    # Add synonyms for Hanuman
    anjaneya = TagSynonym(
        tag_id=hanuman.id,
        synonym="Anjaneya"
    )
    test_db.add(anjaneya)
    
    maruti = TagSynonym(
        tag_id=hanuman.id,
        synonym="Maruti"
    )
    test_db.add(maruti)
    
    test_db.commit()
    
    return {
        "deity_root": deity_root,
        "vishnu": vishnu,
        "shiva": shiva,
        "krishna": krishna,
        "rama": rama,
        "hanuman": hanuman
    }


@pytest.fixture
def sample_bhajan_with_tags(test_db, sample_tag_taxonomy):
    """
    Create a bhajan with taxonomy tags (bhajan_tags table).
    """
    if 'models' in sys.modules:
        del sys.modules['models']
    from models import Bhajan, BhajanTag
    
    bhajan = Bhajan(
        title="Test Hanuman Chalisa with Tags",
        lyrics="Jai Hanuman gyan gun sagar, Jai Kapis tihun lok ujagar",
        tags='["Hanuman"]',
        uploader_name="TestUser"
    )
    test_db.add(bhajan)
    test_db.flush()
    
    # Link to taxonomy
    bhajan_tag = BhajanTag(
        bhajan_id=bhajan.id,
        tag_id=sample_tag_taxonomy["hanuman"].id,
        source="manual",
        confidence=1.0
    )
    test_db.add(bhajan_tag)
    test_db.commit()
    
    return bhajan


@pytest.fixture
def test_mapping_csv(tmp_path):
    """
    Create a temporary tag migration mapping CSV for tests.
    
    Returns the path to the CSV file.
    """
    csv_content = """old_tag,canonical_tag,action,notes
Hanuman,Hanuman,KEEP,Primary deity tag
hanuman,Hanuman,MERGE,Case normalization
Anjaneya,Hanuman,MERGE,Synonym of Hanuman
Rama,Rama,KEEP,Primary deity tag
rama,Rama,MERGE,Case normalization
Krishna,Krishna,KEEP,Primary deity tag
Shiva,Shiva,KEEP,Primary deity tag
test,N/A,DELETE,Meta tag
"""
    csv_path = tmp_path / "tag-migration-mapping.csv"
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def test_frequency_csv(tmp_path):
    """
    Create a temporary tag frequency report CSV for tests.
    
    Returns the path to the CSV file.
    """
    csv_content = """tag,count,percentage
Hanuman,15,25.0
Krishna,12,20.0
Rama,10,16.7
Shiva,8,13.3
hanuman,5,8.3
rama,4,6.7
Anjaneya,3,5.0
krishna,2,3.3
test,1,1.7
"""
    csv_path = tmp_path / "tag-frequency-report.csv"
    csv_path.write_text(csv_content)
    return csv_path


def unique_name(base: str) -> str:
    """Generate unique name for test data to avoid conflicts."""
    import time
    return f"{base}_{int(time.time() * 1000) % 100000}"
