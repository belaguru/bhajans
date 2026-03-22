#!/usr/bin/env python3
"""
Test auto-tagger on 20 real bhajans from the database
Generate accuracy report
"""
import sqlite3
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from auto_tag import auto_tag


def test_on_real_bhajans(db_path: str, limit: int = 20):
    """Test auto-tagger on real bhajans from database"""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get 20 diverse bhajans (prefer those with existing tags for comparison)
    query = """
    SELECT id, title, lyrics, tags, manual_tags
    FROM bhajans
    WHERE deleted_at IS NULL
    ORDER BY id
    LIMIT ?
    """
    
    cursor.execute(query, (limit,))
    bhajans = cursor.fetchall()
    
    results = []
    
    print(f"Testing auto-tagger on {len(bhajans)} bhajans...\n")
    
    for row in bhajans:
        bhajan_id = row['id']
        title = row['title']
        lyrics = row['lyrics']
        existing_tags = row['tags'] or '[]'
        manual_tags = row['manual_tags']
        
        # Parse existing tags
        try:
            existing_tags_list = json.loads(existing_tags) if existing_tags else []
        except:
            existing_tags_list = []
        
        # Auto-tag
        detected_tags = auto_tag({
            'title': title,
            'lyrics': lyrics
        })
        
        # Prepare result
        result = {
            'bhajan_id': bhajan_id,
            'title': title[:80] + '...' if len(title) > 80 else title,
            'existing_tags': existing_tags_list,
            'detected_tags': detected_tags,
            'manual_tags': manual_tags
        }
        
        results.append(result)
        
        # Print progress
        print(f"[{bhajan_id}] {result['title']}")
        print(f"  Detected: {list(detected_tags.keys())}")
        print(f"  Existing: {existing_tags_list}")
        print()
    
    conn.close()
    
    return results


def calculate_accuracy(results):
    """Calculate precision metrics"""
    
    total_bhajans = len(results)
    deity_detected = 0
    deity_matches = 0  # Correct deity detection
    type_detected = 0
    language_detected = 0
    
    # Deities and types
    deities = ['Hanuman', 'Krishna', 'Rama', 'Shiva', 'Vishnu', 'Ganesha', 'Devi']
    types = ['Chalisa', 'Stotra', 'Aarti', 'Bhajan', 'Kirtan', 'Mantra']
    languages = ['Kannada', 'Hindi', 'English']
    
    # Manual verification of correct detections (spot check)
    for result in results:
        detected = result['detected_tags']
        existing = result['existing_tags']
        
        # Check deity detection
        detected_deities = [d for d in deities if d in detected]
        existing_deities = [d for d in deities if any(d.lower() in str(e).lower() for e in existing)]
        
        if detected_deities:
            deity_detected += 1
            # Check if at least one detected deity matches existing tags
            if any(d in existing_deities or 
                   any(d.lower() in str(e).lower() for e in existing) 
                   for d in detected_deities):
                deity_matches += 1
        
        # Check type detection
        if any(t in detected for t in types):
            type_detected += 1
        
        # Check language detection
        if any(l in detected for l in languages):
            language_detected += 1
    
    # Calculate precision (correct / total detected)
    deity_precision = deity_matches / deity_detected if deity_detected > 0 else 0
    
    accuracy = {
        'total_bhajans': total_bhajans,
        'deity_detected_count': deity_detected,
        'deity_correct_count': deity_matches,
        'deity_precision': deity_precision,
        'deity_detection_rate': deity_detected / total_bhajans,
        'type_detection_rate': type_detected / total_bhajans,
        'language_detection_rate': language_detected / total_bhajans,
        'avg_tags_per_bhajan': sum(len(r['detected_tags']) for r in results) / total_bhajans,
        'avg_confidence': sum(
            sum(r['detected_tags'].values()) / len(r['detected_tags'])
            for r in results if r['detected_tags']
        ) / sum(1 for r in results if r['detected_tags'])
    }
    
    return accuracy


def main():
    db_path = Path(__file__).parent.parent / 'data' / 'portal.db'
    output_path = Path(__file__).parent.parent / 'data' / 'auto-tag-test-results.json'
    
    # Test on real data
    results = test_on_real_bhajans(str(db_path), limit=20)
    
    # Calculate accuracy
    accuracy = calculate_accuracy(results)
    
    # Prepare output
    output = {
        'test_date': '2026-03-22',
        'num_bhajans_tested': len(results),
        'accuracy_metrics': accuracy,
        'results': results
    }
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("AUTO-TAGGER ACCURACY REPORT")
    print("="*60)
    print(f"Total bhajans tested: {accuracy['total_bhajans']}")
    print(f"\nDEITY DETECTION:")
    print(f"  Detected: {accuracy['deity_detected_count']} bhajans")
    print(f"  Correct: {accuracy['deity_correct_count']} bhajans")
    print(f"  Precision: {accuracy['deity_precision']*100:.1f}%")
    print(f"  Coverage: {accuracy['deity_detection_rate']*100:.1f}%")
    print(f"\nOTHER METRICS:")
    print(f"  Type detection: {accuracy['type_detection_rate']*100:.1f}%")
    print(f"  Language detection: {accuracy['language_detection_rate']*100:.1f}%")
    print(f"  Avg tags/bhajan: {accuracy['avg_tags_per_bhajan']:.1f}")
    print(f"  Avg confidence: {accuracy['avg_confidence']:.2f}")
    print("\n✓ Results saved to:", output_path)
    
    # Precision assessment (focus on deity precision as primary metric)
    deity_precision = accuracy['deity_precision']
    print(f"\n{'='*60}")
    print(f"DEITY DETECTION PRECISION: {deity_precision*100:.1f}%")
    print(f"TARGET: >85%")
    if deity_precision >= 0.85:
        print("✓ TARGET MET!")
    else:
        print(f"✗ Gap: {(0.85 - deity_precision)*100:.1f}% below target")
    print("="*60)


if __name__ == "__main__":
    main()
