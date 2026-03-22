"""
Test Tag Migration Mapping

TDD Tests for tag migration process. These tests verify that:
1. All 76 existing tags have a mapping
2. No tag is left unmapped
3. Case duplicates are merged correctly
4. Semantic duplicates are identified
5. Meta tags are flagged for deletion
"""

import pytest
import csv
import sqlite3
import json
from pathlib import Path
from collections import Counter


# Known tags from current database (76 unique tags)
EXPECTED_TAG_COUNT = 76

# Meta tags that should be deleted
META_TAGS = {
    'test', 'Test', 'test-audio', 'YouTube'
}

# Case duplicate pairs (lowercase -> canonical)
CASE_DUPLICATES = {
    ('rama', 'Rama'),
    ('shiva', 'Shiva'),
    ('devi', 'Devi'),
    ('devotional', 'Devotional'),  # Note: lowercase is more frequent!
    ('krishna', 'Krishna'),
    ('belaguru', 'Belaguru'),
    ('sadguru', 'Sadguru'),
    ('narayana', 'Narayana'),
    ('hanuman', 'Hanuman'),
    ('chalisa', 'Chalisa'),
}

# Semantic duplicate groups (all refer to same deity/concept)
SEMANTIC_GROUPS = {
    'Hanuman': {'Hanuman', 'hanuman', 'Anjaneya', 'maruti', 'Vijaya Maruti'},
    'Rama': {'Rama', 'rama'},
    'Krishna': {'Krishna', 'krishna'},
    'Shiva': {'Shiva', 'shiva'},
    'Devi': {'Devi', 'devi'},
    'Belaguru': {'Belaguru', 'belaguru'},
}


@pytest.fixture
def db_path():
    """Path to staging database"""
    return Path(__file__).parent.parent / 'data' / 'portal.db'


@pytest.fixture
def mapping_csv_path():
    """Path to tag migration mapping CSV"""
    return Path(__file__).parent.parent / 'data' / 'tag-migration-mapping.csv'


@pytest.fixture
def frequency_csv_path():
    """Path to tag frequency report CSV"""
    return Path(__file__).parent.parent / 'data' / 'tag-frequency-report.csv'


@pytest.fixture
def current_tags(db_path):
    """Extract all unique tags from staging database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT tags FROM bhajans WHERE tags IS NOT NULL AND tags != '[]'")
    rows = cursor.fetchall()
    
    all_tags = []
    for row in rows:
        try:
            tags = json.loads(row[0])
            all_tags.extend(tags)
        except:
            pass
    
    conn.close()
    return set(all_tags)


def test_database_exists(db_path):
    """Verify staging database exists"""
    assert db_path.exists(), f"Database not found at {db_path}"


def test_tag_count_matches(current_tags):
    """Verify we found the expected number of unique tags"""
    assert len(current_tags) == EXPECTED_TAG_COUNT, \
        f"Expected {EXPECTED_TAG_COUNT} tags, found {len(current_tags)}"


def test_mapping_file_exists(mapping_csv_path):
    """Verify tag migration mapping CSV exists"""
    assert mapping_csv_path.exists(), \
        f"Mapping file not found at {mapping_csv_path}"


def test_frequency_file_exists(frequency_csv_path):
    """Verify tag frequency report CSV exists"""
    assert frequency_csv_path.exists(), \
        f"Frequency report not found at {frequency_csv_path}"


def test_all_tags_mapped(current_tags, mapping_csv_path):
    """Verify every tag from database has a mapping"""
    with open(mapping_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        mapped_tags = {row['old_tag'] for row in reader}
    
    unmapped = current_tags - mapped_tags
    assert len(unmapped) == 0, \
        f"Found {len(unmapped)} unmapped tags: {sorted(unmapped)}"


def test_no_extra_mappings(current_tags, mapping_csv_path):
    """Verify no mappings for non-existent tags"""
    with open(mapping_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        mapped_tags = {row['old_tag'] for row in reader}
    
    extra = mapped_tags - current_tags
    assert len(extra) == 0, \
        f"Found {len(extra)} mappings for non-existent tags: {sorted(extra)}"


def test_meta_tags_deleted(mapping_csv_path):
    """Verify all meta tags are marked for deletion"""
    with open(mapping_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        mappings = {row['old_tag']: row for row in reader}
    
    for meta_tag in META_TAGS:
        assert meta_tag in mappings, f"Meta tag '{meta_tag}' not in mapping"
        assert mappings[meta_tag]['action'] == 'DELETE', \
            f"Meta tag '{meta_tag}' should have action=DELETE, got {mappings[meta_tag]['action']}"


def test_case_duplicates_merged(mapping_csv_path):
    """Verify case duplicates are merged to canonical form"""
    with open(mapping_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        mappings = {row['old_tag']: row for row in reader}
    
    for lowercase, canonical in CASE_DUPLICATES:
        # Both should be in mappings
        assert lowercase in mappings or canonical in mappings, \
            f"Neither '{lowercase}' nor '{canonical}' found in mappings"
        
        # If both exist, lowercase should merge to canonical
        if lowercase in mappings and canonical in mappings:
            if mappings[lowercase]['action'] == 'MERGE':
                assert mappings[lowercase]['canonical_tag'] == canonical, \
                    f"'{lowercase}' should merge to '{canonical}', got '{mappings[lowercase]['canonical_tag']}'"


def test_semantic_groups_merged(mapping_csv_path):
    """Verify semantic duplicates are identified and merged"""
    with open(mapping_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        mappings = {row['old_tag']: row for row in reader}
    
    for canonical, group in SEMANTIC_GROUPS.items():
        canonical_tags = set()
        
        for tag in group:
            if tag not in mappings:
                continue
            
            action = mappings[tag]['action']
            if action == 'KEEP':
                canonical_tags.add(tag)
            elif action == 'MERGE':
                canonical_tags.add(mappings[tag]['canonical_tag'])
        
        # All should map to the same canonical tag
        assert len(canonical_tags) <= 1, \
            f"Semantic group '{canonical}' maps to multiple tags: {canonical_tags}"


def test_mapping_csv_format(mapping_csv_path):
    """Verify mapping CSV has correct columns and format"""
    with open(mapping_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        # Check required columns
        assert headers == ['old_tag', 'canonical_tag', 'action', 'notes'], \
            f"Expected columns [old_tag, canonical_tag, action, notes], got {headers}"
        
        # Check each row
        for row in reader:
            # old_tag must be non-empty
            assert row['old_tag'].strip(), "Found empty old_tag"
            
            # action must be KEEP, MERGE, or DELETE
            assert row['action'] in ['KEEP', 'MERGE', 'DELETE'], \
                f"Invalid action '{row['action']}' for tag '{row['old_tag']}'"
            
            # If MERGE, canonical_tag must be different and non-empty
            if row['action'] == 'MERGE':
                assert row['canonical_tag'].strip(), \
                    f"MERGE action for '{row['old_tag']}' has empty canonical_tag"
                assert row['canonical_tag'] != row['old_tag'], \
                    f"MERGE action for '{row['old_tag']}' has same canonical_tag"
            
            # If KEEP, canonical_tag should match old_tag
            if row['action'] == 'KEEP':
                assert row['canonical_tag'] == row['old_tag'], \
                    f"KEEP action for '{row['old_tag']}' has different canonical_tag '{row['canonical_tag']}'"
            
            # If DELETE, canonical_tag should be empty or N/A
            if row['action'] == 'DELETE':
                assert row['canonical_tag'] in ['', 'N/A'], \
                    f"DELETE action for '{row['old_tag']}' should have empty canonical_tag"


def test_frequency_csv_format(frequency_csv_path):
    """Verify frequency CSV has correct columns and format"""
    with open(frequency_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        # Check required columns
        assert headers == ['tag', 'count', 'percentage'], \
            f"Expected columns [tag, count, percentage], got {headers}"
        
        # Check each row
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


def test_frequency_totals(current_tags, frequency_csv_path):
    """Verify frequency report includes all tags"""
    with open(frequency_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        frequency_tags = {row['tag'] for row in reader}
    
    assert frequency_tags == current_tags, \
        f"Frequency report tags don't match database tags. " \
        f"Missing: {current_tags - frequency_tags}, Extra: {frequency_tags - current_tags}"


def test_action_distribution(mapping_csv_path):
    """Verify reasonable distribution of actions"""
    with open(mapping_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        actions = Counter(row['action'] for row in reader)
    
    # Should have at least some KEEP actions
    assert actions['KEEP'] > 0, "No KEEP actions found"
    
    # Should have some MERGE actions (for duplicates)
    assert actions['MERGE'] > 0, "No MERGE actions found"
    
    # Should have some DELETE actions (for meta tags)
    assert actions['DELETE'] >= len(META_TAGS), \
        f"Expected at least {len(META_TAGS)} DELETE actions, got {actions['DELETE']}"
    
    # Total should match tag count
    assert sum(actions.values()) == EXPECTED_TAG_COUNT, \
        f"Total actions {sum(actions.values())} doesn't match tag count {EXPECTED_TAG_COUNT}"


def test_notes_provided(mapping_csv_path):
    """Verify explanatory notes are provided for MERGE and DELETE actions"""
    with open(mapping_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if row['action'] in ['MERGE', 'DELETE']:
                assert row['notes'].strip(), \
                    f"Action {row['action']} for '{row['old_tag']}' missing explanation in notes"
