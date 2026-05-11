#!/usr/bin/env python3
"""
Mutation Engine — Phase 5
Convert approved mutation intent into parameter adjustments during spawn.
"""

from typing import Dict, Optional, Tuple


class MutationEngine:
    """Apply controlled mutations to baby DNA based on proposal intent."""
    
    # Mutation type keywords
    MUTATION_KEYWORDS = {
        'EXIT': ['exit', 'holding', 'inefficiency', 'slow', 'delay', 'extend'],
        'SELECTIVITY': ['overtrading', 'too many', 'flip rate', 'high churn', 'frequent'],
        'SIZE': ['execution', 'slippage', 'fragility', 'sizing', 'depth'],
    }
    
    # Parameter adjustments per mutation type
    ADJUSTMENTS = {
        'EXIT': {
            'exit_threshold_pct': ('multiply', 1.15),
            'target_move': ('multiply', 1.05),
            'stop_move': ('multiply', 1.05),
        },
        'SELECTIVITY': {
            'selectivity_percentile': ('multiply', 1.10),
            'pressure_level': ('multiply', 0.95),
        },
        'SIZE': {
            'trade_size': ('multiply', 0.85),
            'max_open_positions': ('multiply', 0.90),
        },
    }
    
    def __init__(self):
        pass
    
    def classify_mutation(self, mutation_summary: str) -> str:
        """
        Classify mutation intent into type.
        
        Args:
            mutation_summary: Text from proposal
        
        Returns:
            'EXIT', 'SELECTIVITY', 'SIZE', or 'NONE'
        """
        if not mutation_summary:
            return 'NONE'
        
        summary_lower = mutation_summary.lower()
        
        # Check each mutation type
        for mutation_type, keywords in self.MUTATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in summary_lower:
                    print(f"[MUTATION] Classified as {mutation_type} (keyword: {keyword})")
                    return mutation_type
        
        print("[MUTATION] No classification matched, returning NONE")
        return 'NONE'
    
    def apply_mutation(self, baby_dna: Dict, mutation_type: str) -> Dict:
        """
        Apply mutation adjustments to baby DNA.
        
        Args:
            baby_dna: Parent parameters
            mutation_type: 'EXIT', 'SELECTIVITY', 'SIZE', or 'NONE'
        
        Returns:
            Mutated baby DNA
        """
        if mutation_type == 'NONE' or mutation_type not in self.ADJUSTMENTS:
            # Return copy unchanged
            return baby_dna.copy()
        
        # Clone DNA
        mutated = baby_dna.copy()
        
        # Apply adjustments
        adjustments = self.ADJUSTMENTS[mutation_type]
        
        for param_name, (operation, value) in adjustments.items():
            if param_name in mutated:
                if operation == 'multiply':
                    original = mutated[param_name]
                    mutated[param_name] = original * value
                    print(f"[MUTATION] {param_name}: {original} → {mutated[param_name]}")
        
        return mutated
    
    def create_control_baby(self, parent_dna: Dict) -> Dict:
        """
        Create control baby with no mutations.
        
        Args:
            parent_dna: Parent parameters
        
        Returns:
            Unmodified copy of parent DNA
        """
        return parent_dna.copy()


def apply_mutation_to_spawn(
    parent_dna: Dict,
    mutation_intent: Optional[Dict],
    num_babies: int = 10
) -> Tuple[list, Dict]:
    """
    Apply mutation during spawn.
    
    Args:
        parent_dna: Parent bot parameters
        mutation_intent: Mutation intent or None
        num_babies: Total babies to spawn
    
    Returns:
        (baby_list, mutation_log)
        where baby_list has mutation info, mutation_log has summary
    """
    
    engine = MutationEngine()
    babies = []
    mutation_type = 'NONE'
    
    # Classify mutation if intent exists
    if mutation_intent and mutation_intent.get('has_pending_mutation'):
        summary = mutation_intent.get('mutation_summary', '')
        mutation_type = engine.classify_mutation(summary)
        print(f"[MUTATION] Spawn with mutation type: {mutation_type}")
    else:
        print("[MUTATION] Spawn with NO mutation (control only)")
    
    # Create at least one control baby
    control_baby = engine.create_control_baby(parent_dna)
    babies.append({
        'dna': control_baby,
        'mutation_applied': False,
        'mutation_type': 'NONE',
        'is_control': True,
    })
    print(f"[MUTATION] Created control baby (no mutation)")
    
    # Create mutated babies (if mutation type exists)
    if mutation_type != 'NONE':
        for i in range(num_babies - 1):  # -1 because we have one control
            mutated_dna = engine.apply_mutation(parent_dna.copy(), mutation_type)
            babies.append({
                'dna': mutated_dna,
                'mutation_applied': True,
                'mutation_type': mutation_type,
                'is_control': False,
            })
        print(f"[MUTATION] Created {num_babies - 1} mutated babies (type: {mutation_type})")
    else:
        # No mutation, fill with baseline babies
        for i in range(num_babies - 1):
            baseline_baby = parent_dna.copy()
            babies.append({
                'dna': baseline_baby,
                'mutation_applied': False,
                'mutation_type': 'NONE',
                'is_control': False,
            })
        print(f"[MUTATION] Created {num_babies - 1} baseline babies (no mutation)")
    
    # Create log entry
    mutation_log = {
        'mutation_applied': mutation_type != 'NONE',
        'mutation_type': mutation_type,
        'total_babies': len(babies),
        'control_babies': 1,
        'mutated_babies': len(babies) - 1 if mutation_type != 'NONE' else 0,
    }
    
    return babies, mutation_log
