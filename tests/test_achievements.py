"""
Tests for achievements system
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.achievements import (
    ACHIEVEMENTS,
    check_achievements,
    get_achievement_progress,
    save_achievements,
    load_achievements,
    format_achievements_display,
    _has_rarity
)


class TestAchievements:
    """Test achievement checking"""
    
    def test_first_hatch_achievement(self):
        """Test First Hatch achievement"""
        stats = {"created_at": "2024-01-01"}
        dna = {}
        
        unlocked = check_achievements(stats, dna)
        keys = [a["key"] for a in unlocked]
        
        assert "first_hatch" in keys
    
    def test_week_warrior_achievement(self):
        """Test Week Warrior achievement (7 day streak)"""
        stats = {"age_days": 7}
        dna = {}
        
        unlocked = check_achievements(stats, dna)
        keys = [a["key"] for a in unlocked]
        
        assert "week_streak" in keys
    
    def test_week_warrior_not_unlocked(self):
        """Test Week Warrior not unlocked before 7 days"""
        stats = {"age_days": 6}
        dna = {}
        
        unlocked = check_achievements(stats, dna)
        keys = [a["key"] for a in unlocked]
        
        assert "week_streak" not in keys
    
    def test_diamond_hands_achievement(self):
        """Test Diamond Hands (30 days)"""
        stats = {"age_days": 30}
        dna = {}
        
        unlocked = check_achievements(stats, dna)
        keys = [a["key"] for a in unlocked]
        
        assert "month_keeper" in keys
    
    def test_century_club_achievement(self):
        """Test Century Club (100 days)"""
        stats = {"age_days": 100}
        dna = {}
        
        unlocked = check_achievements(stats, dna)
        keys = [a["key"] for a in unlocked]
        
        assert "century_club" in keys
    
    def test_mutation_achievements(self):
        """Test mutation-based achievements"""
        # Test first mutation
        stats_1 = {"total_mutations": 1}
        unlocked_1 = check_achievements(stats_1, {})
        assert "first_mutation" in [a["key"] for a in unlocked_1]
        
        # Test mutant (10 mutations)
        stats_10 = {"total_mutations": 10}
        unlocked_10 = check_achievements(stats_10, {})
        assert "mutant" in [a["key"] for a in unlocked_10]
        
        # Test evolved (50 mutations)
        stats_50 = {"total_mutations": 50}
        unlocked_50 = check_achievements(stats_50, {})
        assert "evolved" in [a["key"] for a in unlocked_50]
    
    def test_rarity_achievements(self):
        """Test rarity-based achievements"""
        # High rarity (50+)
        stats_50 = {"rarity_score": 50}
        unlocked_50 = check_achievements(stats_50, {})
        assert "high_rarity" in [a["key"] for a in unlocked_50]
        
        # Elite rarity (75+)
        stats_75 = {"rarity_score": 75}
        unlocked_75 = check_achievements(stats_75, {})
        assert "elite_rarity" in [a["key"] for a in unlocked_75]
    
    def test_social_achievements(self):
        """Test social/fork-based achievements"""
        # Proud parent (1+ children)
        stats_1 = {"children_count": 1}
        unlocked_1 = check_achievements(stats_1, {})
        assert "parent" in [a["key"] for a in unlocked_1]
        
        # Dynasty founder (5+ children)
        stats_5 = {"children_count": 5}
        unlocked_5 = check_achievements(stats_5, {})
        assert "dynasty" in [a["key"] for a in unlocked_5]
        
        # Influencer (10+ children)
        stats_10 = {"children_count": 10}
        unlocked_10 = check_achievements(stats_10, {})
        assert "influencer" in [a["key"] for a in unlocked_10]
    
    def test_generation_achievements(self):
        """Test generation-based achievements"""
        # Gen 2
        stats_gen2 = {"generation": 2}
        unlocked_2 = check_achievements(stats_gen2, {})
        assert "gen_2" in [a["key"] for a in unlocked_2]
        
        # Gen 5
        stats_gen5 = {"generation": 5}
        unlocked_5 = check_achievements(stats_gen5, {})
        assert "gen_5" in [a["key"] for a in unlocked_5]
    
    def test_trait_achievements(self):
        """Test trait-based achievements"""
        dna_accessory = {"accessory": "Crown"}
        unlocked_acc = check_achievements({}, dna_accessory)
        assert "accessorized" in [a["key"] for a in unlocked_acc]
        
        dna_pattern = {"pattern": "Stars"}
        unlocked_pat = check_achievements({}, dna_pattern)
        assert "patterned" in [a["key"] for a in unlocked_pat]
        
        dna_special = {"special": "Glow"}
        unlocked_spec = check_achievements({}, dna_special)
        assert "special_one" in [a["key"] for a in unlocked_spec]
    
    def test_leaderboard_achievements(self):
        """Test leaderboard ranking achievements"""
        # Top 100
        stats_100 = {"leaderboard_rank": 100}
        unlocked_100 = check_achievements(stats_100, {})
        assert "top_100" in [a["key"] for a in unlocked_100]
        
        # Top 10
        stats_10 = {"leaderboard_rank": 10}
        unlocked_10 = check_achievements(stats_10, {})
        assert "top_10" in [a["key"] for a in unlocked_10]
        
        # Champion
        stats_1 = {"leaderboard_rank": 1}
        unlocked_1 = check_achievements(stats_1, {})
        assert "champion" in [a["key"] for a in unlocked_1]


class TestAchievementProgress:
    """Test achievement progress tracking"""
    
    def test_progress_calculation(self):
        """Test progress percentage calculation"""
        stats = {
            "age_days": 7,
            "created_at": "2024-01-01",
            "total_mutations": 1
        }
        
        progress = get_achievement_progress(stats, {})
        
        assert progress["unlocked_count"] > 0
        assert progress["total_count"] == len(ACHIEVEMENTS)
        assert 0 <= progress["percentage"] <= 100
    
    def test_progress_by_category(self):
        """Test achievements grouped by category"""
        stats = {"age_days": 7, "created_at": "2024-01-01"}
        
        progress = get_achievement_progress(stats, {})
        
        assert "by_category" in progress
        # Should have at least one category
        assert len(progress["by_category"]) > 0


class TestAchievementPersistence:
    """Test saving and loading achievements"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temp directory for testing"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    def test_save_achievements(self, temp_dir):
        """Test saving achievements to file"""
        achievements = [
            {"key": "first_hatch", "icon": "🥚", "title": "First Hatch"}
        ]
        
        path = str(temp_dir / "achievements.json")
        save_achievements(achievements, path)
        
        assert Path(path).exists()
    
    def test_load_achievements(self, temp_dir):
        """Test loading achievements from file"""
        achievements = [
            {"key": "week_streak", "icon": "🔥", "title": "Week Warrior"}
        ]
        
        path = str(temp_dir / "achievements.json")
        save_achievements(achievements, path)
        
        loaded = load_achievements(path)
        assert len(loaded) == 1
        assert loaded[0]["key"] == "week_streak"
    
    def test_load_nonexistent_achievements(self, temp_dir):
        """Test loading from nonexistent file returns empty list"""
        path = str(temp_dir / "nonexistent.json")
        loaded = load_achievements(path)
        assert loaded == []


class TestAchievementDisplay:
    """Test achievement formatting"""
    
    def test_format_empty_achievements(self):
        """Test formatting with no achievements"""
        result = format_achievements_display([])
        assert "No achievements" in result
    
    def test_format_with_achievements(self):
        """Test formatting with achievements"""
        achievements = [
            {"key": "first_hatch", "icon": "🥚", "title": "First Hatch", "category": "milestone"},
            {"key": "week_streak", "icon": "🔥", "title": "Week Warrior", "category": "streak"}
        ]
        
        result = format_achievements_display(achievements)
        
        assert "🥚" in result
        assert "🔥" in result
        assert "2/" in result  # Shows count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

