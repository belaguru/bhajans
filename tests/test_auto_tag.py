"""
Auto-Tagging Test Suite
Tests for deity/type/language detection with >85% precision target
"""
import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from auto_tag import (
    detect_deities,
    detect_types,
    detect_language,
    auto_tag
)


class TestDeityDetection:
    """Test deity detection with keyword matching"""
    
    def test_hanuman_variations(self):
        """Hanuman should be detected from multiple names"""
        test_cases = [
            ("Hanuman Chalisa", "हनुमान की जय", ["Hanuman"]),
            ("Anjaneya Dandakam", "Anjaneya stotra", ["Hanuman"]),
            ("Pavansuta stuti", "Maruti bhajan", ["Hanuman"]),
        ]
        
        for title, lyrics, expected in test_cases:
            result = detect_deities(title, lyrics)
            assert "Hanuman" in result, f"Failed for title: {title}"
    
    def test_krishna_variations(self):
        """Krishna should be detected from multiple names"""
        test_cases = [
            ("Krishna Bhajan", "Govinda Gopala", ["Krishna"]),
            ("Madhava stotra", "Hare Krishna", ["Krishna"]),
            ("Gopala Krishna", "Govinda naam", ["Krishna"]),
        ]
        
        for title, lyrics, expected in test_cases:
            result = detect_deities(title, lyrics)
            assert "Krishna" in result, f"Failed for title: {title}"
    
    def test_rama_variations(self):
        """Rama should be detected from multiple names"""
        test_cases = [
            ("Rama Bhajan", "Raghava", ["Rama"]),
            ("Raghu stotra", "Rama naam", ["Rama"]),
            ("Raghava stuti", "Sri Rama", ["Rama"]),
        ]
        
        for title, lyrics, expected in test_cases:
            result = detect_deities(title, lyrics)
            assert "Rama" in result, f"Failed for title: {title}"
    
    def test_shiva_variations(self):
        """Shiva should be detected from multiple names"""
        test_cases = [
            ("Shiva Tandava", "Shankara", ["Shiva"]),
            ("Mahadeva stotra", "Om Namah Shivaya", ["Shiva"]),
            ("Shankara bhajan", "Shiva Shambho", ["Shiva"]),
        ]
        
        for title, lyrics, expected in test_cases:
            result = detect_deities(title, lyrics)
            assert "Shiva" in result, f"Failed for title: {title}"
    
    def test_ganesha_variations(self):
        """Ganesha should be detected from multiple names"""
        test_cases = [
            ("Ganesha Pancharatna", "Ganapati", ["Ganesha"]),
            ("Vinayaka Chavithi", "Vighnaharta", ["Ganesha"]),
            ("Ganapati stotra", "Ganesha mantra", ["Ganesha"]),
        ]
        
        for title, lyrics, expected in test_cases:
            result = detect_deities(title, lyrics)
            assert "Ganesha" in result, f"Failed for title: {title}"
    
    def test_devi_variations(self):
        """Devi should be detected from multiple names"""
        test_cases = [
            ("Durga Stotra", "Devi bhajan", ["Devi"]),
            ("Lakshmi aarti", "Mahalakshmi", ["Devi"]),
            ("Saraswati stotra", "Sharade", ["Devi"]),
        ]
        
        for title, lyrics, expected in test_cases:
            result = detect_deities(title, lyrics)
            assert "Devi" in result, f"Failed for title: {title}"
    
    def test_multiple_deities(self):
        """Should detect multiple deities in same bhajan"""
        title = "Rama Krishna Hari"
        lyrics = "Rama Krishna Govinda Shiva"
        result = detect_deities(title, lyrics)
        
        assert "Rama" in result
        assert "Krishna" in result
        assert "Shiva" in result
    
    def test_case_insensitive(self):
        """Detection should be case-insensitive"""
        test_cases = [
            ("hanuman chalisa", "HANUMAN bhajan"),
            ("KRISHNA BHAJAN", "krishna govinda"),
            ("Rama Nama", "RAMA jayam"),
        ]
        
        for title, lyrics in test_cases:
            result = detect_deities(title, lyrics)
            assert len(result) > 0, f"Failed case-insensitive test: {title}"
    
    def test_no_deity_found(self):
        """Should return empty list when no deity found"""
        result = detect_deities("Test Song", "Random lyrics")
        assert result == []


class TestTypeDetection:
    """Test bhajan type detection"""
    
    def test_chalisa_detection(self):
        """Should detect Chalisa type"""
        assert "Chalisa" in detect_types("Hanuman Chalisa")
        assert "Chalisa" in detect_types("Shiva Chalisa")
    
    def test_stotra_detection(self):
        """Should detect Stotra/Stotram type"""
        assert "Stotra" in detect_types("Ganesha Stotra")
        assert "Stotra" in detect_types("Vishnu Stotram")
    
    def test_aarti_detection(self):
        """Should detect Aarti/Aarati type"""
        assert "Aarti" in detect_types("Ganesha Aarti")
        assert "Aarti" in detect_types("Om Jai Aarati")
    
    def test_bhajan_detection(self):
        """Should detect Bhajan type"""
        assert "Bhajan" in detect_types("Krishna Bhajan")
        assert "Bhajan" in detect_types("Daily Bhajan")
    
    def test_kirtan_detection(self):
        """Should detect Kirtan type"""
        assert "Kirtan" in detect_types("Hare Krishna Kirtan")
        assert "Kirtan" in detect_types("Naam Kirtan")
    
    def test_mantra_detection(self):
        """Should detect Mantra type"""
        assert "Mantra" in detect_types("Gayatri Mantra")
        assert "Mantra" in detect_types("Om Mantra")
    
    def test_multiple_types(self):
        """Should detect multiple types if present"""
        result = detect_types("Hanuman Chalisa Stotra Bhajan")
        assert len(result) >= 2
    
    def test_case_insensitive_types(self):
        """Type detection should be case-insensitive"""
        assert "Chalisa" in detect_types("hanuman chalisa")
        assert "Stotra" in detect_types("GANESHA STOTRA")


class TestLanguageDetection:
    """Test language detection from script"""
    
    def test_kannada_script(self):
        """Should detect Kannada from script"""
        kannada_text = "ವಂದಿಪೆ ನಿನಗೆ ಗಣನಾಥಾ"
        assert detect_language(kannada_text) == "Kannada"
    
    def test_devanagari_script(self):
        """Should detect Hindi from Devanagari script"""
        hindi_text = "जय हनुमान ज्ञान गुण सागर"
        assert detect_language(hindi_text) == "Hindi"
    
    def test_english_only(self):
        """Should detect English when only Latin script"""
        english_text = "Hanuman Chalisa in English"
        assert detect_language(english_text) == "English"
    
    def test_mixed_script_kannada_dominant(self):
        """Should detect Kannada when it's dominant"""
        mixed_text = "Hanuman ಹನುಮಾನ್ ಚಾಲೀಸಾ Chalisa"
        result = detect_language(mixed_text)
        assert result == "Kannada"
    
    def test_mixed_script_hindi_dominant(self):
        """Should detect Hindi when Devanagari is dominant"""
        mixed_text = "Hanuman हनुमान चालीसा Chalisa"
        result = detect_language(mixed_text)
        assert result == "Hindi"
    
    def test_empty_lyrics(self):
        """Should handle empty lyrics gracefully"""
        assert detect_language("") == "Unknown"
        assert detect_language(None) == "Unknown"


class TestConfidenceScoring:
    """Test confidence scoring (0.0-1.0)"""
    
    def test_high_confidence_single_match(self):
        """Single strong match should give high confidence"""
        title = "Hanuman Chalisa"
        lyrics = "Jai Hanuman gyan gun sagar"
        result = auto_tag({"title": title, "lyrics": lyrics})
        
        assert result["Hanuman"] >= 0.8, "High confidence expected for strong match"
    
    def test_medium_confidence_title_only(self):
        """Match only in title should give medium confidence"""
        title = "Hanuman song"
        lyrics = "Random text without deity name"
        result = auto_tag({"title": title, "lyrics": lyrics})
        
        if "Hanuman" in result:
            assert 0.3 <= result["Hanuman"] <= 0.7, "Medium confidence expected"
    
    def test_low_confidence_single_occurrence(self):
        """Single occurrence in long text should give lower confidence"""
        title = "Song collection"
        lyrics = "This mentions Hanuman once in thousand words " + ("random " * 200)
        result = auto_tag({"title": title, "lyrics": lyrics})
        
        if "Hanuman" in result:
            assert result["Hanuman"] < 0.6, "Lower confidence for rare occurrence"
    
    def test_confidence_range(self):
        """All confidence scores should be between 0.0 and 1.0"""
        title = "Hanuman Krishna Rama Stotra Chalisa"
        lyrics = "Hanuman Krishna Rama bhajan"
        result = auto_tag({"title": title, "lyrics": lyrics})
        
        for tag, confidence in result.items():
            assert 0.0 <= confidence <= 1.0, f"Invalid confidence for {tag}: {confidence}"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_title_and_lyrics(self):
        """Should handle empty inputs gracefully"""
        result = auto_tag({"title": "", "lyrics": ""})
        assert isinstance(result, dict)
    
    def test_none_values(self):
        """Should handle None values gracefully"""
        result = auto_tag({"title": None, "lyrics": None})
        assert isinstance(result, dict)
    
    def test_special_characters(self):
        """Should handle special characters"""
        title = "Hanuman @#$% Chalisa!!!"
        lyrics = "*** Krishna *** Rama ***"
        result = auto_tag({"title": title, "lyrics": lyrics})
        
        assert len(result) > 0
    
    def test_very_long_lyrics(self):
        """Should handle very long lyrics efficiently"""
        title = "Hanuman Chalisa"
        lyrics = "Hanuman bhajan " * 1000  # Very long text
        result = auto_tag({"title": title, "lyrics": lyrics})
        
        assert "Hanuman" in result
    
    def test_mixed_languages(self):
        """Should handle mixed language content"""
        title = "Hanuman ಹನುಮಾನ್ हनुमान"
        lyrics = "Mixed ಕನ್ನಡ हिंदी English content"
        result = auto_tag({"title": title, "lyrics": lyrics})
        
        assert "Hanuman" in result
        assert isinstance(result, dict)


class TestIntegration:
    """Integration tests with auto_tag function"""
    
    def test_hanuman_chalisa_full(self):
        """Test complete Hanuman Chalisa tagging"""
        bhajan = {
            "title": "ಹನುಮಾನ್ ಚಾಲೀಸಾ Hanuman Chalisa",
            "lyrics": "ಜಯ ಹನುಮಾನ ಜ್ಞಾನ ಗುಣ ಸಾಗರ। ಜಯ ಕಪೀಶ ತಿಹು ಲೋಕ ಉಜಾಗರ॥"
        }
        
        result = auto_tag(bhajan)
        
        assert "Hanuman" in result
        assert "Chalisa" in result
        assert result["Hanuman"] > 0.7  # High confidence
        assert result["Chalisa"] > 0.8  # Very high confidence for type
    
    def test_ganesha_bhajan_full(self):
        """Test Ganesha bhajan tagging"""
        bhajan = {
            "title": "ವಂದಿಪೆ ನಿನಗೆ ಗಣನಾಥಾ Vandipe ninage Gananaatha",
            "lyrics": "ವಂದಿಪೆ ನಿನಗೆ ಗಣನಾಥಾ | ಮೊದಲೊಂದಿಪೆ ನಿಮಗೆ ಗಣನಾಥಾ"
        }
        
        result = auto_tag(bhajan)
        
        assert "Ganesha" in result
        assert "Kannada" in result
    
    def test_auto_tag_returns_dict(self):
        """auto_tag should always return a dictionary"""
        bhajan = {"title": "Test", "lyrics": "Test lyrics"}
        result = auto_tag(bhajan)
        
        assert isinstance(result, dict)
        assert all(isinstance(v, (int, float)) for v in result.values())


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
