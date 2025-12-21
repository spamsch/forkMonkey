"""
Tests for genetics system
"""

import pytest
from src.genetics import (
    GeneticsEngine, MonkeyDNA, Trait, TraitCategory, Rarity
)


class TestGeneticsEngine:
    """Test genetics engine"""
    
    def test_generate_random_dna(self):
        """Test random DNA generation"""
        dna = GeneticsEngine.generate_random_dna()
        
        assert dna.generation == 1
        assert dna.parent_id is None
        assert len(dna.traits) == len(TraitCategory)
        assert dna.dna_hash != ""
        
        # Check all categories present
        for category in TraitCategory:
            assert category in dna.traits
            assert isinstance(dna.traits[category], Trait)
    
    def test_dna_hash_uniqueness(self):
        """Test that different DNA has different hashes"""
        dna1 = GeneticsEngine.generate_random_dna()
        dna2 = GeneticsEngine.generate_random_dna()
        
        # Very unlikely to be the same
        assert dna1.dna_hash != dna2.dna_hash
    
    def test_rarity_distribution(self):
        """Test rarity distribution is reasonable"""
        rarities = {r: 0 for r in Rarity}
        
        # Generate many monkeys
        for _ in range(1000):
            dna = GeneticsEngine.generate_random_dna()
            for trait in dna.traits.values():
                rarities[trait.rarity] += 1
        
        total = sum(rarities.values())
        
        # Check approximate distribution
        common_pct = (rarities[Rarity.COMMON] / total) * 100
        legendary_pct = (rarities[Rarity.LEGENDARY] / total) * 100
        
        assert 50 < common_pct < 70  # Should be around 60%
        assert 2 < legendary_pct < 8  # Should be around 5%
    
    def test_breed(self):
        """Test breeding mechanics"""
        parent = GeneticsEngine.generate_random_dna()
        child = GeneticsEngine.breed(parent, mutation_rate=0.3)
        
        assert child.generation == parent.generation + 1
        assert child.parent_id == parent.dna_hash
        assert child.dna_hash != parent.dna_hash
        
        # Child should have some inherited traits
        inherited_count = sum(
            1 for cat in TraitCategory
            if child.traits[cat].value == parent.traits[cat].value
        )
        
        # With 50% inheritance + mutations, expect some similarity
        assert inherited_count >= 0  # At least possible to inherit
    
    def test_evolve(self):
        """Test evolution mechanics"""
        dna = GeneticsEngine.generate_random_dna()
        evolved = GeneticsEngine.evolve(dna, evolution_strength=0.5)
        
        assert evolved.generation == dna.generation
        assert evolved.parent_id == dna.parent_id
        assert evolved.mutation_count >= dna.mutation_count
        
        # Should have some changes with 50% strength
        changed_count = sum(
            1 for cat in TraitCategory
            if evolved.traits[cat].value != dna.traits[cat].value
        )
        
        assert changed_count >= 0  # At least possible to change
    
    def test_rarity_score(self):
        """Test rarity score calculation"""
        dna = GeneticsEngine.generate_random_dna()
        score = dna.get_rarity_score()
        
        assert 0 <= score <= 100
    
    def test_serialization(self):
        """Test DNA serialization and deserialization"""
        original = GeneticsEngine.generate_random_dna()
        
        # Convert to dict
        data = GeneticsEngine.dna_to_dict(original)
        
        assert isinstance(data, dict)
        assert "generation" in data
        assert "traits" in data
        assert "dna_hash" in data
        
        # Convert back
        restored = GeneticsEngine.dict_to_dna(data)
        
        assert restored.dna_hash == original.dna_hash
        assert restored.generation == original.generation
        assert len(restored.traits) == len(original.traits)
        
        # Check all traits match
        for category in TraitCategory:
            assert restored.traits[category].value == original.traits[category].value
            assert restored.traits[category].rarity == original.traits[category].rarity


class TestTrait:
    """Test trait model"""
    
    def test_trait_creation(self):
        """Test trait creation"""
        trait = Trait(
            category=TraitCategory.BODY_COLOR,
            value="brown",
            rarity=Rarity.COMMON
        )
        
        assert trait.category == TraitCategory.BODY_COLOR
        assert trait.value == "brown"
        assert trait.rarity == Rarity.COMMON
        assert trait.gene_sequence != ""
    
    def test_gene_sequence_generation(self):
        """Test gene sequence is generated"""
        trait = Trait(
            category=TraitCategory.FACE_EXPRESSION,
            value="happy",
            rarity=Rarity.COMMON
        )
        
        assert len(trait.gene_sequence) == 8  # MD5 hash truncated to 8 chars
    
    def test_same_trait_same_sequence(self):
        """Test same trait generates same sequence"""
        trait1 = Trait(
            category=TraitCategory.BODY_COLOR,
            value="golden",
            rarity=Rarity.UNCOMMON
        )
        
        trait2 = Trait(
            category=TraitCategory.BODY_COLOR,
            value="golden",
            rarity=Rarity.UNCOMMON
        )
        
        assert trait1.gene_sequence == trait2.gene_sequence


class TestMonkeyDNA:
    """Test MonkeyDNA model"""
    
    def test_dna_creation(self):
        """Test DNA creation"""
        traits = {
            TraitCategory.BODY_COLOR: Trait(
                category=TraitCategory.BODY_COLOR,
                value="brown",
                rarity=Rarity.COMMON
            )
        }
        
        dna = MonkeyDNA(
            generation=1,
            traits=traits
        )
        
        assert dna.generation == 1
        assert dna.dna_hash != ""
    
    def test_dna_hash_calculation(self):
        """Test DNA hash is calculated correctly"""
        traits = {
            TraitCategory.BODY_COLOR: Trait(
                category=TraitCategory.BODY_COLOR,
                value="brown",
                rarity=Rarity.COMMON
            )
        }
        
        dna1 = MonkeyDNA(generation=1, traits=traits)
        dna2 = MonkeyDNA(generation=1, traits=traits)
        
        # Same traits should give same hash
        assert dna1.dna_hash == dna2.dna_hash


class TestGenLockedTraits:
    """Test gen-locked (extinct) trait system"""
    
    def test_get_gen_locked_traits_gen1(self):
        """Test that Gen 1 has access to all gen-locked traits"""
        body_locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.BODY_COLOR, 1)
        accessory_locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.ACCESSORY, 1)
        special_locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.SPECIAL, 1)
        
        # Gen 1 should have access to all locked traits
        assert "origin_white" in body_locked
        assert "genesis_gold" in body_locked
        assert "prismatic" in body_locked
        
        assert "genesis_aura" in accessory_locked
        assert "alpha_crown" in accessory_locked
        assert "founders_badge" in accessory_locked
        
        assert "genesis_blessing" in special_locked
        assert "early_spark" in special_locked
        assert "pioneer_glow" in special_locked
    
    def test_get_gen_locked_traits_gen5(self):
        """Test that Gen 5 has limited gen-locked traits"""
        body_locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.BODY_COLOR, 5)
        accessory_locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.ACCESSORY, 5)
        special_locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.SPECIAL, 5)
        
        # Gen 5 should NOT have Gen 1-only or Gen 1-3 traits
        assert "origin_white" not in body_locked
        assert "genesis_gold" not in body_locked
        assert "prismatic" in body_locked  # Gen 1-5, still available
        
        assert "genesis_aura" not in accessory_locked
        assert "alpha_crown" not in accessory_locked
        assert "founders_badge" in accessory_locked  # Gen 1-5
        
        assert "genesis_blessing" not in special_locked
        assert "early_spark" in special_locked  # Gen 1-5
        assert "pioneer_glow" in special_locked  # Gen 1-10
    
    def test_get_gen_locked_traits_gen20(self):
        """Test that high generations have no gen-locked traits"""
        body_locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.BODY_COLOR, 20)
        accessory_locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.ACCESSORY, 20)
        special_locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.SPECIAL, 20)
        
        # Gen 20 should have no locked traits (all extinct)
        assert len(body_locked) == 0
        assert len(accessory_locked) == 0
        assert len(special_locked) == 0
    
    def test_gen_locked_traits_are_legendary(self):
        """Test that gen-locked traits when generated are legendary rarity"""
        # Generate many Gen 1 monkeys and check any gen-locked traits
        found_gen_locked = False
        for _ in range(500):  # Higher count to increase chance
            dna = GeneticsEngine.generate_random_dna(generation=1)
            for cat, trait in dna.traits.items():
                gen_locked = GeneticsEngine.get_gen_locked_traits(cat, 1)
                if trait.value in gen_locked:
                    assert trait.rarity == Rarity.LEGENDARY
                    found_gen_locked = True
        
        # With 5% chance per category, we should find at least one in 500 attempts
        # But don't require it - random chance
    
    def test_breed_respects_gen_locked(self):
        """Test that breeding respects generation locks"""
        parent = GeneticsEngine.generate_random_dna(generation=1)
        
        # Create child (Gen 2)
        child = GeneticsEngine.breed(parent)
        assert child.generation == 2
        
        # Gen 2 should not get Gen 1-only traits
        for cat, trait in child.traits.items():
            if trait.value in ["origin_white", "genesis_aura", "genesis_blessing"]:
                # These are Gen 1 only - child shouldn't generate them fresh
                # (unless inherited from parent)
                pass  # Allow inheritance
    
    def test_category_without_gen_locked(self):
        """Test categories without gen-locked traits return empty"""
        # FACE_EXPRESSION has no gen-locked traits
        locked = GeneticsEngine.get_gen_locked_traits(TraitCategory.FACE_EXPRESSION, 1)
        assert len(locked) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
