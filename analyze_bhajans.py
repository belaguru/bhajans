#!/usr/bin/env python3
"""
Comprehensive Bhajan Tag Analysis
Analyzes all bhajans and creates multi-category tag associations
"""

import sqlite3
import json
import re
from datetime import datetime
from typing import List, Dict, Set

# Existing tag structure
EXISTING_TAGS = {
    'deity': {
        2: {'name': 'Shiva', 'keywords': ['shiva', 'ಶಿವ', 'rudra', 'ರುದ್ರ', 'shankar', 'ಶಂಕರ', 'maheshwara']},
        3: {'name': 'Vishnu', 'keywords': ['vishnu', 'ವಿಷ್ಣು', 'narayana', 'ನಾರಾಯಣ', 'hari', 'ಹರಿ']},
        4: {'name': 'Devi', 'keywords': ['devi', 'ದೇವಿ', 'sharade', 'ಶಾರದೆ', 'saraswati', 'ಸರಸ್ವತಿ', 'lakshmi', 'ಲಕ್ಷ್ಮಿ', 'parvati', 'ಪಾರ್ವತಿ', 'durga', 'ದುರ್ಗಾ']},
        5: {'name': 'Ganesha', 'keywords': ['ganesha', 'ಗಣೇಶ', 'ganapati', 'ಗಣಪತಿ', 'vinayaka', 'ವಿನಾಯಕ']},
        6: {'name': 'Hanuman', 'keywords': ['hanuman', 'ಹನುಮಾನ್', 'anjaneya', 'ಆಂಜನೇಯ', 'maruti', 'ಮಾರುತಿ', 'pavana', 'ಪವನ', 'vayu putra', 'ವಾಯುಪುತ್ರ']},
        7: {'name': 'Krishna', 'keywords': ['krishna', 'ಕೃಷ್ಣ', 'gopala', 'ಗೋಪಾಲ', 'govinda', 'ಗೋವಿಂದ', 'madhava', 'ಮಾಧವ']},
        8: {'name': 'Rama', 'keywords': ['rama', 'ರಾಮ', 'raghuvara', 'ರಘುವರ', 'raghu', 'ರಘು', 'sita', 'ಸೀತಾ']},
        146: {'name': 'Narasimha', 'keywords': ['narasimha', 'ನರಸಿಂಹ', 'nrusimha', 'ugra', 'ಉಗ್ರ']},
    },
    'type': {
        9: {'name': 'Bhajan', 'keywords': ['bhajan', 'keertane', 'pada', 'ಪದ']},
        10: {'name': 'Stotra', 'keywords': ['stotra', 'stuti', 'ಸ್ತುತಿ', 'ಸ್ತೋತ್ರ', 'ashtaka', 'ashtak']},
        11: {'name': 'Aarti', 'keywords': ['aarti', 'arati', 'ಆರತಿ']},
        12: {'name': 'Chalisa', 'keywords': ['chalisa', 'ಚಾಲೀಸಾ']},
        13: {'name': 'Gurustuti', 'keywords': ['guru', 'ಗುರು', 'bindu madhava', 'ಬಿಂದು ಮಾಧವ']},
        14: {'name': 'Mantra', 'keywords': ['mantra', 'ಮಂತ್ರ', 'namavali', 'ashtottara', 'sahasranama']},
    },
    'theme': {
        18: {'name': 'Kannada', 'detect': 'script'},  # Detect by Kannada script
        20: {'name': 'Sanskrit', 'detect': 'script'},  # Detect by Devanagari/transliteration
        21: {'name': 'Chants', 'keywords': ['om', 'ॐ', 'ಓಂ', 'namah', 'ನಮಃ', 'svaha', 'ಸ್ವಾಹಾ']},
        22: {'name': 'Namasmarane', 'keywords': ['nama', 'ನಾಮ', 'namavali', 'ನಾಮಾವಲಿ']},
        23: {'name': 'Mangala', 'keywords': ['mangala', 'ಮಂಗಳ', 'shubha', 'ಶುಭ']},
        19: {'name': 'Tatva pada', 'keywords': ['tatva', 'ತತ್ವ', 'jnana', 'ಜ್ಞಾನ', 'advaita', 'ಅದ್ವೈತ']},
    },
    'composer': {
        15: {'name': 'Purandara Dasa', 'keywords': ['purandara', 'ಪುರಂದರ']},
        16: {'name': 'Belaguru', 'keywords': ['belaguru', 'ಬೆಲಗೂರು', 'belaguuru']},
        17: {'name': 'Daasapada', 'keywords': ['dasa', 'ದಾಸ', 'vittala', 'ವಿಠಲ']},
    },
    'occasion': {
        24: {'name': 'Morning', 'keywords': ['pratha', 'ಪ್ರಾತಃ', 'suprabhat', 'ಸುಪ್ರಭಾತ', 'suprabhata']},
        26: {'name': 'Festival', 'keywords': ['utsava', 'ಉತ್ಸವ', 'festival', 'habba', 'ಹಬ್ಬ']},
        27: {'name': 'Bindu Madhava', 'keywords': ['bindu madhava', 'ಬಿಂದು ಮಾಧವ']},
    }
}

def detect_language(text: str) -> str:
    """Detect primary language by script"""
    kannada_chars = len(re.findall(r'[\u0C80-\u0CFF]', text))
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    total_chars = len(text)
    
    if kannada_chars > total_chars * 0.3:
        return 'kannada'
    elif devanagari_chars > total_chars * 0.2:
        return 'sanskrit'
    return 'unknown'

def analyze_bhajan(bhajan_id: int, title: str, lyrics: str) -> Dict:
    """Analyze a single bhajan and return tag associations"""
    combined_text = f"{title.lower()} {lyrics.lower()}"
    tags = set()
    analysis = {
        'id': bhajan_id,
        'title': title,
        'tags': [],
        'reasoning': []
    }
    
    # 1. DETECT DEITY (Priority 1)
    for tag_id, info in EXISTING_TAGS['deity'].items():
        for keyword in info['keywords']:
            if keyword.lower() in combined_text:
                tags.add(tag_id)
                analysis['reasoning'].append(f"Deity: {info['name']} (found '{keyword}')")
                break
    
    # 2. DETECT TYPE (Priority 2)
    type_found = False
    for tag_id, info in EXISTING_TAGS['type'].items():
        for keyword in info['keywords']:
            if keyword.lower() in combined_text:
                tags.add(tag_id)
                analysis['reasoning'].append(f"Type: {info['name']} (found '{keyword}')")
                type_found = True
                break
        if type_found:
            break
    
    # Default to Bhajan if no type found
    if not type_found:
        tags.add(9)  # Bhajan
        analysis['reasoning'].append("Type: Bhajan (default)")
    
    # 3. DETECT LANGUAGE/THEME (Priority 3)
    lang = detect_language(combined_text)
    if lang == 'kannada':
        tags.add(18)  # Kannada
        analysis['reasoning'].append("Theme: Kannada (script detection)")
    elif lang == 'sanskrit':
        tags.add(20)  # Sanskrit
        analysis['reasoning'].append("Theme: Sanskrit (script detection)")
    
    # 4. DETECT OTHER THEMES
    for tag_id, info in EXISTING_TAGS['theme'].items():
        if tag_id in [18, 20]:  # Skip language tags (already handled)
            continue
        if 'keywords' in info:
            for keyword in info['keywords']:
                if keyword.lower() in combined_text:
                    tags.add(tag_id)
                    analysis['reasoning'].append(f"Theme: {info['name']} (found '{keyword}')")
                    break
    
    # 5. DETECT COMPOSER (Priority 5)
    for tag_id, info in EXISTING_TAGS['composer'].items():
        for keyword in info['keywords']:
            if keyword.lower() in combined_text:
                tags.add(tag_id)
                analysis['reasoning'].append(f"Composer: {info['name']} (found '{keyword}')")
                break
    
    # 6. DETECT OCCASION (Priority 6)
    for tag_id, info in EXISTING_TAGS['occasion'].items():
        for keyword in info['keywords']:
            if keyword.lower() in combined_text:
                tags.add(tag_id)
                analysis['reasoning'].append(f"Occasion: {info['name']} (found '{keyword}')")
                break
    
    analysis['tags'] = sorted(list(tags))
    return analysis

def main():
    print("=" * 80)
    print("COMPREHENSIVE BHAJAN TAG ANALYSIS")
    print("=" * 80)
    print()
    
    # Connect to database
    conn = sqlite3.connect('data/portal.db')
    cursor = conn.cursor()
    
    # Get all bhajans
    bhajans = cursor.execute('SELECT id, title, lyrics FROM bhajans ORDER BY id').fetchall()
    print(f"Total bhajans to analyze: {len(bhajans)}\n")
    
    # Analyze all bhajans
    results = []
    for b in bhajans:
        analysis = analyze_bhajan(b[0], b[1], b[2])
        results.append(analysis)
    
    # Statistics
    tag_counts = {}
    for result in results:
        for tag_id in result['tags']:
            tag_counts[tag_id] = tag_counts.get(tag_id, 0) + 1
    
    # Display sample results
    print("\n" + "=" * 80)
    print("SAMPLE TAGGING RESULTS (First 10 bhajans)")
    print("=" * 80)
    for result in results[:10]:
        print(f"\n[{result['id']}] {result['title']}")
        print(f"  Tags: {result['tags']}")
        for reason in result['reasoning']:
            print(f"    - {reason}")
    
    # Display statistics
    print("\n" + "=" * 80)
    print("TAG USAGE STATISTICS")
    print("=" * 80)
    print(f"{'Tag ID':7} | {'Tag Name':20} | {'Count':5} | {'%':5}")
    print("-" * 50)
    
    # Get tag names
    tag_names = {}
    for category in EXISTING_TAGS.values():
        for tag_id, info in category.items():
            tag_names[tag_id] = info['name']
    
    for tag_id in sorted(tag_counts.keys()):
        count = tag_counts[tag_id]
        pct = (count / len(bhajans)) * 100
        name = tag_names.get(tag_id, 'Unknown')
        print(f"{tag_id:7} | {name:20} | {count:5} | {pct:5.1f}%")
    
    # Save results to JSON
    with open('tag_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Analysis saved to tag_analysis_results.json")
    
    # Generate SQL migration
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sql_file = f'tag_migration_{timestamp}.sql'
    
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write("-- Comprehensive Bhajan Tag Association Migration\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Total bhajans: {len(bhajans)}\n")
        f.write(f"-- Total associations: {sum(len(r['tags']) for r in results)}\n\n")
        
        # Backup existing
        f.write("-- Backup existing associations\n")
        f.write("CREATE TABLE IF NOT EXISTS bhajan_tags_backup_" + timestamp + " AS SELECT * FROM bhajan_tags;\n\n")
        
        # Clear existing associations
        f.write("-- Clear existing associations\n")
        f.write("DELETE FROM bhajan_tags;\n\n")
        
        # Insert new associations
        f.write("-- Insert new tag associations\n")
        f.write("BEGIN TRANSACTION;\n\n")
        
        for result in results:
            bhajan_id = result['id']
            for tag_id in result['tags']:
                f.write(f"INSERT INTO bhajan_tags (bhajan_id, tag_id, source, confidence) ")
                f.write(f"VALUES ({bhajan_id}, {tag_id}, 'AI_ANALYSIS', 0.9);\n")
        
        f.write("\nCOMMIT;\n\n")
        
        # Verification queries
        f.write("-- Verification queries\n")
        f.write("SELECT 'Total associations:', COUNT(*) FROM bhajan_tags;\n")
        f.write("SELECT 'Bhajans with tags:', COUNT(DISTINCT bhajan_id) FROM bhajan_tags;\n")
        f.write("SELECT 'Tags in use:', COUNT(DISTINCT tag_id) FROM bhajan_tags;\n")
    
    print(f"✓ SQL migration saved to {sql_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Bhajans analyzed: {len(bhajans)}")
    print(f"Total tag associations: {sum(len(r['tags']) for r in results)}")
    print(f"Average tags per bhajan: {sum(len(r['tags']) for r in results) / len(bhajans):.1f}")
    print(f"Bhajans with 2+ tags: {sum(1 for r in results if len(r['tags']) >= 2)}")
    print(f"Bhajans with 3+ tags: {sum(1 for r in results if len(r['tags']) >= 3)}")
    
    conn.close()

if __name__ == '__main__':
    main()
