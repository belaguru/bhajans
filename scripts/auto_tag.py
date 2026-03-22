#!/usr/bin/env python3
"""
Auto-Tagger for Belaguru Bhajans
Detects deities, types, and languages with confidence scoring
Target: >85% precision on deity/type detection
"""
import re
import unicodedata
from typing import Dict, List, Optional, Tuple


# Deity keyword mappings (case-insensitive)
DEITY_KEYWORDS = {
    "Hanuman": [
        "hanuman", "anjaneya", "maruti", "pavansuta", "pavana", 
        "mahaavira", "bajrangbali", "bajrang", "kesari", "anjani",
        "hanumān", "हनुमान", "ಹನುಮಾನ", "ಆಂಜನೇಯ", "anjana",
        "maaruti", "veeramalla", "hanuma", "ಮಾರುತಿ"
    ],
    "Krishna": [
        "krishna", "govinda", "gopala", "madhava", "keshava",
        "hari", "murari", "gopal", "giridhari", "vasudeva",
        "कृष्ण", "ಕೃಷ್ಣ", "bindu madhava"
    ],
    "Rama": [
        "rama", "raghava", "raghu", "raghupati", "raghunatha",
        "ayodhya", "dasharatha", "kosala", "राम", "ರಾಮ"
    ],
    "Shiva": [
        "shiva", "shankara", "mahadeva", "sambho", "shambho",
        "rudra", "neelakantha", "nataraja", "shambhu", "mahesh",
        "शिव", "ಶಿವ", "gangadhara", "gangādhara", "chandrashekhar",
        "umashankara", "sadashiva", "linga", "lingam", "parashiva",
        "shivāya", "jagadeeshana", "jagadeesha", "शंकर", "ಶಂಕರ",
        "bhayahara", "sumanohara", "shivane", "ಶಿವನೇ", "ಸದಾಶಿವ",
        "jagadeesh", "ಜಗದೀಶ", "sadaashivana", "ಸದಾಶಿವನಾ",
        "ಪರಶಿವ", "parashiva", "jagadeesha", "ಜಗದೀಶನಾ"
    ],
    "Vishnu": [
        "vishnu", "narayana", "hari", "venkateshwara", "venkatesha",
        "narasimha", "varaaha", "vamana", "balaji", "विष्णु", "ವಿಷ್ಣು"
    ],
    "Ganesha": [
        "ganesha", "ganapati", "vinayaka", "vighneshwara", "vighnaharta",
        "gajanana", "lambodara", "ekadanta", "gananatha", "gananaatha",
        "गणेश", "ಗಣೇಶ", "गणपति", "ಗಣಪತಿ"
    ],
    "Devi": [
        "devi", "durga", "lakshmi", "saraswati", "parvati",
        "kali", "amba", "ambika", "jagadamba", "sharade",
        "chamundi", "mahalakshmi", "देवी", "ದೇವಿ", "शारदे", "ಶಾರದೆ"
    ]
}

# Type keyword mappings (case-insensitive)
TYPE_KEYWORDS = {
    "Chalisa": ["chalisa", "चालीसा"],
    "Stotra": ["stotra", "stotram", "स्तोत्र", "स्तोत्रं"],
    "Aarti": ["aarti", "aarati", "arti", "आरती", "आरति"],
    "Bhajan": ["bhajan", "भजन"],
    "Kirtan": ["kirtan", "keertan", "कीर्तन"],
    "Mantra": ["mantra", "मंत्र"]
}

# Unicode ranges for language detection
KANNADA_RANGE = (0x0C80, 0x0CFF)
DEVANAGARI_RANGE = (0x0900, 0x097F)


def normalize_text(text: str) -> str:
    """Normalize text for matching (lowercase, strip, NFD)"""
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFD', text)
    # Lowercase
    text = text.lower()
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def count_script_chars(text: str, char_range: Tuple[int, int]) -> int:
    """Count characters in a specific Unicode range"""
    if not text:
        return 0
    
    count = 0
    for char in text:
        code_point = ord(char)
        if char_range[0] <= code_point <= char_range[1]:
            count += 1
    
    return count


def detect_language(lyrics: Optional[str]) -> str:
    """
    Detect language from script used in lyrics
    Returns: "Kannada", "Hindi", "English", or "Unknown"
    """
    if not lyrics:
        return "Unknown"
    
    # Count characters in different scripts
    kannada_chars = count_script_chars(lyrics, KANNADA_RANGE)
    devanagari_chars = count_script_chars(lyrics, DEVANAGARI_RANGE)
    
    # Total non-whitespace chars
    total_chars = len([c for c in lyrics if not c.isspace()])
    
    if total_chars == 0:
        return "Unknown"
    
    # Calculate percentages
    kannada_pct = kannada_chars / total_chars
    devanagari_pct = devanagari_chars / total_chars
    
    # Threshold: >10% presence of script
    if kannada_pct > 0.1:
        return "Kannada"
    elif devanagari_pct > 0.1:
        return "Hindi"
    elif total_chars > 0:
        return "English"
    
    return "Unknown"


def detect_deities(title: str, lyrics: str) -> List[str]:
    """
    Detect deity names from title and lyrics
    Returns: List of detected deity tags
    """
    if not title:
        title = ""
    if not lyrics:
        lyrics = ""
    
    # Normalize
    norm_title = normalize_text(title)
    norm_lyrics = normalize_text(lyrics)
    
    # Combine for searching
    combined_text = f"{norm_title} {norm_lyrics}"
    
    detected = []
    
    for deity, keywords in DEITY_KEYWORDS.items():
        # Check if any keyword matches
        for keyword in keywords:
            # Use word boundary matching
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, combined_text):
                detected.append(deity)
                break  # Found this deity, move to next
    
    return detected


def detect_types(title: str) -> List[str]:
    """
    Detect bhajan type from title
    Returns: List of detected type tags
    """
    if not title:
        return []
    
    norm_title = normalize_text(title)
    
    detected = []
    
    for bhajan_type, keywords in TYPE_KEYWORDS.items():
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, norm_title):
                detected.append(bhajan_type)
                break  # Found this type, move to next
    
    return detected


def calculate_confidence(
    tag: str,
    title: str,
    lyrics: str,
    is_type: bool = False
) -> float:
    """
    Calculate confidence score (0.0 - 1.0) for a tag
    
    Factors:
    - Presence in title vs lyrics (title = higher weight)
    - Frequency of occurrence
    - Length of text (more occurrences in short text = higher confidence)
    - Context penalties (if title suggests different deity)
    """
    if not title:
        title = ""
    if not lyrics:
        lyrics = ""
    
    norm_title = normalize_text(title)
    norm_lyrics = normalize_text(lyrics)
    
    # Get keywords for this tag
    if is_type:
        keywords = TYPE_KEYWORDS.get(tag, [])
    else:
        keywords = DEITY_KEYWORDS.get(tag, [])
    
    if not keywords:
        return 0.0
    
    # Count occurrences
    title_count = 0
    lyrics_count = 0
    
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        title_count += len(re.findall(pattern, norm_title))
        lyrics_count += len(re.findall(pattern, norm_lyrics))
    
    # Base confidence
    confidence = 0.0
    
    # Title presence = high weight
    if title_count > 0:
        confidence += 0.6
        # Multiple occurrences in title
        if title_count > 1:
            confidence += 0.1
    
    # Lyrics presence
    if lyrics_count > 0:
        # Calculate relative frequency
        lyrics_words = len(norm_lyrics.split())
        if lyrics_words > 0:
            frequency = lyrics_count / lyrics_words
            # Scale to 0.5 max (increased from 0.4)
            confidence += min(0.5, frequency * 150)
        else:
            confidence += 0.3
    
    # For types (Chalisa, Stotra), title match is very strong signal
    if is_type and title_count > 0:
        confidence = max(confidence, 0.85)
    
    # Context penalty: If deity only appears in title but lyrics strongly suggest another deity
    # (e.g., "Brahma Murari" in title of Shiva Linga bhajan)
    if not is_type and title_count > 0 and lyrics_count == 0:
        # Check if lyrics have strong indicators of OTHER deities
        for other_deity, other_keywords in DEITY_KEYWORDS.items():
            if other_deity != tag:
                other_lyrics_count = sum(
                    len(re.findall(r'\b' + re.escape(kw) + r'\b', norm_lyrics))
                    for kw in other_keywords
                )
                # If other deity appears >3 times in lyrics, reduce confidence
                if other_lyrics_count > 3:
                    confidence *= 0.7
                    break
    
    # Cap at 1.0
    return min(1.0, confidence)


def auto_tag(bhajan: Dict[str, Optional[str]], confidence_threshold: float = 0.55) -> Dict[str, float]:
    """
    Auto-tag a bhajan with deities, types, and language
    
    Args:
        bhajan: Dict with 'title' and 'lyrics' keys
        confidence_threshold: Minimum confidence to include tag (default 0.55)
    
    Returns:
        Dict of {tag: confidence_score}
    """
    title = bhajan.get("title", "") or ""
    lyrics = bhajan.get("lyrics", "") or ""
    
    result = {}
    
    # Detect deities
    deities = detect_deities(title, lyrics)
    for deity in deities:
        confidence = calculate_confidence(deity, title, lyrics, is_type=False)
        # Only include if confidence above threshold (reduces false positives)
        if confidence >= confidence_threshold:
            result[deity] = confidence
    
    # Detect types
    types = detect_types(title)
    for bhajan_type in types:
        confidence = calculate_confidence(bhajan_type, title, lyrics, is_type=True)
        result[bhajan_type] = confidence
    
    # Detect language
    language = detect_language(lyrics)
    if language != "Unknown":
        # Language detection is high confidence when detected
        result[language] = 0.95
    
    return result


def main():
    """CLI entry point for testing"""
    import sys
    import json
    
    if len(sys.argv) < 3:
        print("Usage: auto_tag.py <title> <lyrics>")
        sys.exit(1)
    
    title = sys.argv[1]
    lyrics = sys.argv[2]
    
    bhajan = {"title": title, "lyrics": lyrics}
    tags = auto_tag(bhajan)
    
    print(json.dumps(tags, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
