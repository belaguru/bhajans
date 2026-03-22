"""
Tests for Tag Taxonomy SQLAlchemy Models
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Bhajan, TagTaxonomy, TagTranslation, TagSynonym, BhajanTag


@pytest.fixture
def db_session():
    """Create in-memory test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestTagTaxonomy:
    """Test TagTaxonomy model"""
    
    def test_create_tag_taxonomy(self, db_session):
        """Test creating a tag taxonomy entry"""
        tag = TagTaxonomy(
            name="hanuman",
            category="deity",
            level=0
        )
        db_session.add(tag)
        db_session.commit()
        
        assert tag.id is not None
        assert tag.name == "hanuman"
        assert tag.category == "deity"
        assert tag.level == 0
        assert tag.parent_id is None
        assert tag.created_at is not None
        assert tag.updated_at is not None
    
    def test_tag_hierarchy(self, db_session):
        """Test parent-child relationships"""
        # Create parent tag
        parent = TagTaxonomy(name="deity", category="root", level=0)
        db_session.add(parent)
        db_session.commit()
        
        # Create child tag
        child = TagTaxonomy(
            name="hanuman",
            category="deity",
            level=1,
            parent_id=parent.id
        )
        db_session.add(child)
        db_session.commit()
        
        # Test parent relationship
        assert child.parent.id == parent.id
        assert child.parent.name == "deity"
        
        # Test children relationship
        assert len(parent.children) == 1
        assert parent.children[0].id == child.id
        assert parent.children[0].name == "hanuman"
    
    def test_tag_translations(self, db_session):
        """Test tag translations relationship"""
        tag = TagTaxonomy(name="hanuman", category="deity", level=0)
        db_session.add(tag)
        db_session.commit()
        
        # Add translations
        trans_kn = TagTranslation(tag_id=tag.id, language="kn", translation="ಹನುಮಾನ್")
        trans_hi = TagTranslation(tag_id=tag.id, language="hi", translation="हनुमान")
        db_session.add_all([trans_kn, trans_hi])
        db_session.commit()
        
        # Test relationship
        assert len(tag.translations) == 2
        translations = {t.language: t.translation for t in tag.translations}
        assert translations["kn"] == "ಹನುಮಾನ್"
        assert translations["hi"] == "हनुमान"
    
    def test_tag_synonyms(self, db_session):
        """Test tag synonyms relationship"""
        tag = TagTaxonomy(name="hanuman", category="deity", level=0)
        db_session.add(tag)
        db_session.commit()
        
        # Add synonyms
        syn1 = TagSynonym(tag_id=tag.id, synonym="anjaneya")
        syn2 = TagSynonym(tag_id=tag.id, synonym="maruti")
        db_session.add_all([syn1, syn2])
        db_session.commit()
        
        # Test relationship
        assert len(tag.synonyms) == 2
        synonym_list = [s.synonym for s in tag.synonyms]
        assert "anjaneya" in synonym_list
        assert "maruti" in synonym_list


class TestTagTranslation:
    """Test TagTranslation model"""
    
    def test_create_translation(self, db_session):
        """Test creating a translation"""
        tag = TagTaxonomy(name="hanuman", category="deity", level=0)
        db_session.add(tag)
        db_session.commit()
        
        translation = TagTranslation(
            tag_id=tag.id,
            language="kn",
            translation="ಹನುಮಾನ್"
        )
        db_session.add(translation)
        db_session.commit()
        
        assert translation.id is not None
        assert translation.tag_id == tag.id
        assert translation.language == "kn"
        assert translation.translation == "ಹನುಮಾನ್"
    
    def test_translation_back_reference(self, db_session):
        """Test back reference to tag"""
        tag = TagTaxonomy(name="hanuman", category="deity", level=0)
        db_session.add(tag)
        db_session.commit()
        
        translation = TagTranslation(tag_id=tag.id, language="kn", translation="ಹನುಮಾನ್")
        db_session.add(translation)
        db_session.commit()
        
        assert translation.tag.id == tag.id
        assert translation.tag.name == "hanuman"


class TestTagSynonym:
    """Test TagSynonym model"""
    
    def test_create_synonym(self, db_session):
        """Test creating a synonym"""
        tag = TagTaxonomy(name="hanuman", category="deity", level=0)
        db_session.add(tag)
        db_session.commit()
        
        synonym = TagSynonym(tag_id=tag.id, synonym="anjaneya")
        db_session.add(synonym)
        db_session.commit()
        
        assert synonym.id is not None
        assert synonym.tag_id == tag.id
        assert synonym.synonym == "anjaneya"
    
    def test_synonym_back_reference(self, db_session):
        """Test back reference to tag"""
        tag = TagTaxonomy(name="hanuman", category="deity", level=0)
        db_session.add(tag)
        db_session.commit()
        
        synonym = TagSynonym(tag_id=tag.id, synonym="anjaneya")
        db_session.add(synonym)
        db_session.commit()
        
        assert synonym.tag.id == tag.id
        assert synonym.tag.name == "hanuman"


class TestBhajanTag:
    """Test BhajanTag model"""
    
    def test_create_bhajan_tag(self, db_session):
        """Test creating a bhajan-tag association"""
        # Create bhajan
        bhajan = Bhajan(title="Hanuman Chalisa", lyrics="Test lyrics")
        db_session.add(bhajan)
        db_session.commit()
        
        # Create tag
        tag = TagTaxonomy(name="hanuman", category="deity", level=0)
        db_session.add(tag)
        db_session.commit()
        
        # Create association
        bhajan_tag = BhajanTag(
            bhajan_id=bhajan.id,
            tag_id=tag.id,
            source="manual",
            confidence=1.0
        )
        db_session.add(bhajan_tag)
        db_session.commit()
        
        assert bhajan_tag.id is not None
        assert bhajan_tag.bhajan_id == bhajan.id
        assert bhajan_tag.tag_id == tag.id
        assert bhajan_tag.source == "manual"
        assert bhajan_tag.confidence == 1.0
        assert bhajan_tag.created_at is not None
    
    def test_bhajan_tag_relationships(self, db_session):
        """Test bhajan and tag relationships"""
        bhajan = Bhajan(title="Hanuman Chalisa", lyrics="Test lyrics")
        tag = TagTaxonomy(name="hanuman", category="deity", level=0)
        db_session.add_all([bhajan, tag])
        db_session.commit()
        
        bhajan_tag = BhajanTag(bhajan_id=bhajan.id, tag_id=tag.id)
        db_session.add(bhajan_tag)
        db_session.commit()
        
        # Test bhajan relationship
        assert bhajan_tag.bhajan.id == bhajan.id
        assert bhajan_tag.bhajan.title == "Hanuman Chalisa"
        
        # Test tag relationship
        assert bhajan_tag.tag.id == tag.id
        assert bhajan_tag.tag.name == "hanuman"


class TestBhajanModel:
    """Test Bhajan model updates"""
    
    def test_taxonomy_tags_relationship(self, db_session):
        """Test bhajan's taxonomy_tags relationship"""
        bhajan = Bhajan(title="Hanuman Chalisa", lyrics="Test lyrics")
        tag1 = TagTaxonomy(name="hanuman", category="deity", level=0)
        tag2 = TagTaxonomy(name="devotional", category="type", level=0)
        db_session.add_all([bhajan, tag1, tag2])
        db_session.commit()
        
        # Create associations
        bt1 = BhajanTag(bhajan_id=bhajan.id, tag_id=tag1.id, source="manual")
        bt2 = BhajanTag(bhajan_id=bhajan.id, tag_id=tag2.id, source="ai", confidence=0.95)
        db_session.add_all([bt1, bt2])
        db_session.commit()
        
        # Test relationship
        assert len(bhajan.taxonomy_tags) == 2
        tag_names = [bt.tag.name for bt in bhajan.taxonomy_tags]
        assert "hanuman" in tag_names
        assert "devotional" in tag_names
    
    def test_get_all_tags_method(self, db_session):
        """Test Bhajan.get_all_tags() method"""
        bhajan = Bhajan(
            title="Hanuman Chalisa",
            lyrics="Test lyrics",
            tags='["old-tag-1", "old-tag-2"]'  # Old JSON tags
        )
        tag1 = TagTaxonomy(name="hanuman", category="deity", level=0)
        tag2 = TagTaxonomy(name="devotional", category="type", level=0)
        db_session.add_all([bhajan, tag1, tag2])
        db_session.commit()
        
        # Add taxonomy tags
        bt1 = BhajanTag(bhajan_id=bhajan.id, tag_id=tag1.id)
        bt2 = BhajanTag(bhajan_id=bhajan.id, tag_id=tag2.id)
        db_session.add_all([bt1, bt2])
        db_session.commit()
        
        # Get all tags
        all_tags = bhajan.get_all_tags()
        
        assert "json_tags" in all_tags
        assert "taxonomy_tags" in all_tags
        
        # Check old JSON tags
        assert "old-tag-1" in all_tags["json_tags"]
        assert "old-tag-2" in all_tags["json_tags"]
        
        # Check new taxonomy tags
        assert len(all_tags["taxonomy_tags"]) == 2
        taxonomy_tag_names = [t["name"] for t in all_tags["taxonomy_tags"]]
        assert "hanuman" in taxonomy_tag_names
        assert "devotional" in taxonomy_tag_names
    
    def test_backward_compatibility(self, db_session):
        """Test that old tags field still works"""
        bhajan = Bhajan(
            title="Test Bhajan",
            lyrics="Test lyrics",
            tags='["tag1", "tag2"]'
        )
        db_session.add(bhajan)
        db_session.commit()
        
        # Old methods should still work
        assert bhajan.get_tags() == ["tag1", "tag2"]
        
        bhajan.set_tags(["tag3", "tag4"])
        db_session.commit()
        
        assert bhajan.get_tags() == ["tag3", "tag4"]
