#!/usr/bin/env python3
"""
Restore 5 chants from git history to database
"""
from models import init_db, SessionLocal, Bhajan
import json

# Chant data
chants = [
    {
        "title": "Om Namah Shivaya",
        "lyrics": """ॐ नमः शिवाय
Om Namah Shivaya

ಓಂ ನಮಃ ಶಿವಾಯ

I bow to Lord Shiva, the auspicious one.
This five-syllable mantra is one of the most powerful and popular mantras in Hinduism.""",
        "tags": ["chant", "mantra", "shiva"],
        "mp3_file": "om-namah-shivaya.mp3",
        "uploader_name": "Belaguru Temple"
    },
    {
        "title": "Gayatri Mantra",
        "lyrics": """ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात्
Om Bhur Bhuvah Svah Tat Savitur Varenyam Bhargo Devasya Dhimahi Dhiyo Yo Nah Prachodayat

ಓಂ ಭೂರ್ಭುವಃ ಸ್ವಃ ತತ್ಸವಿತುರ್ವರೇಣ್ಯಂ ಭರ್ಗೋ ದೇವಸ್ಯ ಧೀಮಹಿ ಧಿಯೋ ಯೋ ನಃ ಪ್ರಚೋದಯಾತ್

May we meditate on the glory of the Creator who has created the Universe, who is worthy of worship, who is the embodiment of knowledge and light, and who removes all sins and ignorance. May He enlighten our intellect.""",
        "tags": ["chant", "mantra", "gayatri"],
        "mp3_file": "gayatri-mantra.mp3",
        "uploader_name": "Belaguru Temple"
    },
    {
        "title": "Hare Krishna Mahamantra",
        "lyrics": """हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे
हरे राम हरे राम राम राम हरे हरे

Hare Krishna Hare Krishna Krishna Krishna Hare Hare
Hare Rama Hare Rama Rama Rama Hare Hare

ಹರೇ ಕೃಷ್ಣ ಹರೇ ಕೃಷ್ಣ ಕೃಷ್ಣ ಕೃಷ್ಣ ಹರೇ ಹರೇ
ಹರೇ ರಾಮ ಹರೇ ರಾಮ ರಾಮ ರಾಮ ಹರೇ ಹರೇ

The great mantra for deliverance, chanted to invoke the divine energy of Krishna and Rama.""",
        "tags": ["chant", "mantra", "krishna", "rama"],
        "mp3_file": "hare-rama-krishna.mp3",
        "uploader_name": "Belaguru Temple"
    },
    {
        "title": "Om Namo Narayanaya",
        "lyrics": """ॐ नमो नारायणाय
Om Namo Narayanaya

ಓಂ ನಮೋ ನಾರಾಯಣಾಯ

I bow to Lord Narayana (Vishnu), the supreme being who pervades all of creation.
This eight-syllable mantra is sacred to Vaishnavas.""",
        "tags": ["chant", "mantra", "vishnu", "narayana"],
        "mp3_file": "om-namo-narayanaya.mp3",
        "uploader_name": "Belaguru Temple"
    },
    {
        "title": "Mahamrityunjaya Mantra",
        "lyrics": """ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्
उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय माऽमृतात्

Om Tryambakam Yajamahe Sugandhim Pushtivardhanam
Urvarukamiva Bandhanan Mrityormukshiya Mamritat

ಓಂ ತ್ರ್ಯಂಬಕಂ ಯಜಾಮಹೇ ಸುಗಂಧಿಂ ಪುಷ್ಟಿವರ್ಧನಮ್
ಉರ್ವಾರುಕಮಿವ ಬಂಧನಾನ್ಮೃತ್ಯೋರ್ಮುಕ್ಷೀಯ ಮಾಽಮೃತಾತ್

We worship the three-eyed Lord Shiva who is fragrant and nourishes all beings.
May He liberate us from death for the sake of immortality, just as a ripe cucumber is severed from its bondage to the creeper.""",
        "tags": ["chant", "mantra", "shiva", "healing"],
        "mp3_file": "mahamrityunjaya.mp3",
        "uploader_name": "Belaguru Temple"
    }
]

def main():
    """Add chants to database"""
    print("Initializing database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check current count
        initial_count = db.query(Bhajan).count()
        print(f"Current bhajan count: {initial_count}")
        
        # Add each chant
        added = 0
        for chant_data in chants:
            # Check if already exists
            existing = db.query(Bhajan).filter(Bhajan.title == chant_data["title"]).first()
            if existing:
                print(f"⚠️  Chant already exists: {chant_data['title']} (ID: {existing.id})")
                continue
            
            # Create new bhajan entry
            bhajan = Bhajan(
                title=chant_data["title"],
                lyrics=chant_data["lyrics"],
                tags=json.dumps(chant_data["tags"]),
                mp3_file=chant_data["mp3_file"],
                uploader_name=chant_data["uploader_name"]
            )
            
            db.add(bhajan)
            db.commit()
            db.refresh(bhajan)
            
            print(f"✓ Added: {bhajan.title} (ID: {bhajan.id})")
            added += 1
        
        # Final count
        final_count = db.query(Bhajan).count()
        print(f"\n{'='*60}")
        print(f"Initial count: {initial_count}")
        print(f"Added: {added}")
        print(f"Final count: {final_count}")
        print(f"Expected: {initial_count + added}")
        print(f"{'='*60}")
        
        if final_count == initial_count + added:
            print("✓ SUCCESS: Count matches expected value")
        else:
            print("⚠️  WARNING: Count mismatch!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
