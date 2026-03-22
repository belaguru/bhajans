"""
Test Tag Migration Mapping.

TDD Tests for tag migration process. These tests verify that:
1. All tags in CSV have correct mappings
2. Case duplicates are merged correctly
3. Semantic duplicates are identified
4. CSV format is valid

Uses test fixtures to create test data instead of relying on production database.
"""
import pytest
import csv
import json
from pathlib import Path
from collections import Counter


class TestMappingCSVFormat:
    """Test the CSV file structure and format requirements"""
    
    def test_mapping_csv_has_required_columns(self, test_mapping_csv):
        """Verify mapping CSV has correct columns"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Check required columns
            assert headers == ['old_tag', 'canonical_tag', 'action', 'notes'], \
                f"Expected columns [old_tag, canonical_tag, action, notes], got {headers}"
    
    def test_mapping_csv_action_values(self, test_mapping_csv):
        """Verify action values are valid"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # old_tag must be non-empty
                assert row['old_tag'].strip(), "Found empty old_tag"
                
                # action must be KEEP, MERGE, or DELETE
                assert row['action'] in ['KEEP', 'MERGE', 'DELETE'], \
                    f"Invalid action '{row['action']}' for tag '{row['old_tag']}'"
    
    def test_mapping_csv_merge_requirements(self, test_mapping_csv):
        """Verify MERGE actions have correct canonical_tag"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if row['action'] == 'MERGE':
                    assert row['canonical_tag'].strip(), \
                        f"MERGE action for '{row['old_tag']}' has empty canonical_tag"
                    assert row['canonical_tag'] != row['old_tag'], \
                        f"MERGE action for '{row['old_tag']}' has same canonical_tag"
    
    def test_mapping_csv_keep_requirements(self, test_mapping_csv):
        """Verify KEEP actions have matching canonical_tag"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if row['action'] == 'KEEP':
                    assert row['canonical_tag'] == row['old_tag'], \
                        f"KEEP action for '{row['old_tag']}' has different canonical_tag '{row['canonical_tag']}'"
    
    def test_mapping_csv_delete_requirements(self, test_mapping_csv):
        """Verify DELETE actions have empty/N/A canonical_tag"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if row['action'] == 'DELETE':
                    assert row['canonical_tag'] in ['', 'N/A'], \
                        f"DELETE action for '{row['old_tag']}' should have empty canonical_tag"


class TestFrequencyCSVFormat:
    """Test the frequency report CSV structure"""
    
    def test_frequency_csv_has_required_columns(self, test_frequency_csv):
        """Verify frequency CSV has correct columns"""
        with open(test_frequency_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Check required columns
            assert headers == ['tag', 'count', 'percentage'], \
                f"Expected columns [tag, count, percentage], got {headers}"
    
    def test_frequency_csv_valid_data(self, test_frequency_csv):
        """Verify frequency report has valid data"""
        with open(test_frequency_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # tag must be non-empty
                assert row['tag'].strip(), "Found empty tag"
                
                # count must be a positive integer
                count = int(row['count'])
                assert count > 0, f"Tag '{row['tag']}' has count {count} <= 0"
                
                # percentage must be a valid float
                percentage = float(row['percentage'])
                assert 0 < percentage <= 100, \
                    f"Tag '{row['tag']}' has invalid percentage {percentage}"


class TestMappingLogic:
    """Test the tag mapping logic"""
    
    def test_case_duplicates_are_merged(self, test_mapping_csv):
        """Verify case duplicates (hanuman -> Hanuman) are merged"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            mappings = {row['old_tag']: row for row in reader}
        
        # hanuman should merge to Hanuman
        if 'hanuman' in mappings:
            assert mappings['hanuman']['action'] == 'MERGE'
            assert mappings['hanuman']['canonical_tag'] == 'Hanuman'
    
    def test_synonym_resolution(self, test_mapping_csv):
        """Verify synonyms (Anjaneya -> Hanuman) are merged"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            mappings = {row['old_tag']: row for row in reader}
        
        # Anjaneya should merge to Hanuman
        if 'Anjaneya' in mappings:
            assert mappings['Anjaneya']['action'] == 'MERGE'
            assert mappings['Anjaneya']['canonical_tag'] == 'Hanuman'
    
    def test_primary_tags_are_kept(self, test_mapping_csv):
        """Verify primary tags are marked as KEEP"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            mappings = {row['old_tag']: row for row in reader}
        
        # Primary tags should have KEEP action
        primary_tags = ['Hanuman', 'Rama', 'Krishna', 'Shiva']
        for tag in primary_tags:
            if tag in mappings:
                assert mappings[tag]['action'] == 'KEEP', \
                    f"Primary tag '{tag}' should be KEEP, got {mappings[tag]['action']}"
    
    def test_meta_tags_are_deleted(self, test_mapping_csv):
        """Verify meta tags are marked for deletion"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            mappings = {row['old_tag']: row for row in reader}
        
        # Meta tags should have DELETE action
        if 'test' in mappings:
            assert mappings['test']['action'] == 'DELETE'
    
    def test_action_distribution(self, test_mapping_csv):
        """Verify reasonable distribution of actions"""
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            actions = Counter(row['action'] for row in reader)
        
        # Should have at least some KEEP actions
        assert actions['KEEP'] > 0, "No KEEP actions found"
        
        # Should have some MERGE actions (for duplicates)
        assert actions['MERGE'] > 0, "No MERGE actions found"


class TestMappingWithDatabase:
    """Test mapping against actual test data"""
    
    def test_create_tags_from_mapping(self, test_db, test_mapping_csv):
        """Test that we can create tags based on mapping"""
        from models import TagTaxonomy
        
        # Read mapping
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            mappings = list(reader)
        
        # Create canonical tags
        canonical_tags = set()
        for row in mappings:
            if row['action'] == 'KEEP':
                canonical_tags.add(row['canonical_tag'])
        
        # Add to database
        for tag_name in canonical_tags:
            tag = TagTaxonomy(
                name=tag_name,
                category="deity",
                level=0
            )
            test_db.add(tag)
        
        test_db.commit()
        
        # Verify
        all_tags = test_db.query(TagTaxonomy).all()
        tag_names = {t.name for t in all_tags}
        
        assert canonical_tags == tag_names
    
    def test_apply_merge_mappings(self, test_db, test_mapping_csv):
        """Test applying merge mappings to bhajan tags"""
        from models import Bhajan
        
        # Read mapping
        with open(test_mapping_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            merge_map = {
                row['old_tag']: row['canonical_tag']
                for row in reader
                if row['action'] == 'MERGE'
            }
        
        # Create bhajan with old tags
        old_tags = ['hanuman', 'Anjaneya', 'Rama']
        bhajan = Bhajan(
            title="Test Bhajan",
            lyrics="Test lyrics at least 20 characters",
            tags=json.dumps(old_tags)
        )
        test_db.add(bhajan)
        test_db.commit()
        
        # Apply mapping
        current_tags = json.loads(bhajan.tags)
        new_tags = []
        for tag in current_tags:
            if tag in merge_map:
                canonical = merge_map[tag]
                if canonical not in new_tags:
                    new_tags.append(canonical)
            else:
                if tag not in new_tags:
                    new_tags.append(tag)
        
        # Verify - hanuman and Anjaneya should both map to Hanuman
        assert 'Hanuman' in new_tags
        assert 'Rama' in new_tags
        # Should have exactly 2 tags after deduplication
        assert len(new_tags) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
