"""
Main script to generate and curate SED puzzle dataset.
"""

import sys
import json
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable
from collections import defaultdict

# Add sed-solver to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "sed-solver" / "src"))
from schema import Problem, Solution

from generators import (
    generate_concatenation_puzzle,
    generate_palindrome_puzzle,
    generate_sorting_puzzle,
    generate_backward_puzzle,
    generate_multiphase_puzzle,
    generate_expansion_puzzle
)
from solver import solve_bfs, verify_solution, clear_cache
from metrics import (
    analyze_difficulty, 
    DifficultyMetrics,
    check_solution_uniqueness,
    is_trivial_puzzle
)
from tracking import GenerationStats


class DatasetGenerator:
    """Main class for generating and curating the dataset."""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.puzzles: List[Problem] = []
        self.solutions: List[Solution] = []
        self.metadata: List[Dict] = []
        self.stats = GenerationStats()
        
        # Define generators optimized for LLM reasoning evaluation
        # Focus on generators that test reasoning (sequential, algorithmic, multi-phase)
        # and benefit from CoT prompting, not just pattern matching
        self.generators = [
            # Easy - Simple pattern matching (baseline/sanity check)
            ('concat_2', lambda pid: generate_concatenation_puzzle(pid, 2), 'easy'),
            # Medium - Sequential reasoning
            ('backward_3', lambda pid: generate_backward_puzzle(pid, 3), 'medium'),
            # Medium - Algorithmic reasoning
            ('sort_3', lambda pid: generate_sorting_puzzle(pid, 3), 'medium'),
            # Hard - Sequential reasoning (longer)
            ('backward_5', lambda pid: generate_backward_puzzle(pid, 5), 'hard'),
            # Hard - Algorithmic reasoning (longer)
            ('sort_4', lambda pid: generate_sorting_puzzle(pid, 4), 'hard'),
            # Hard - Multi-phase reasoning (excellent for CoT)
            ('multiphase', generate_multiphase_puzzle, 'hard'),
            # Expert - Complex sequential reasoning
            ('backward_7', lambda pid: generate_backward_puzzle(pid, 7), 'expert'),
            # Optional - Pattern recognition (if working)
            ('palin_3', lambda pid: generate_palindrome_puzzle(pid, 3), 'hard'),
        ]
    
    def _normalize_string(self, s: str) -> str:
        """Normalize string for duplicate detection."""
        return s.strip().upper()
    
    def _is_duplicate(self, problem: Problem) -> bool:
        """Check if puzzle is a duplicate (improved detection)."""
        normalized_new = self._normalize_string(problem.initial_string)
        
        for existing in self.puzzles:
            # Check exact match (normalized)
            if self._normalize_string(existing.initial_string) == normalized_new:
                return True
            
            # Check semantic similarity (same transitions structure)
            if len(existing.transitions) == len(problem.transitions):
                existing_trans = sorted([(t.src, t.tgt) for t in existing.transitions])
                new_trans = sorted([(t.src, t.tgt) for t in problem.transitions])
                if existing_trans == new_trans and normalized_new == self._normalize_string(existing.initial_string):
                    return True
        
        return False
    
    def _select_generator_weighted(self, difficulty_buckets: Dict[str, int], 
                                   target_distribution: Dict[str, int]) -> Tuple[str, Callable]:
        """Select generator with weighted probability based on success rates and difficulty needs."""
        weights = self.stats.get_generator_weights()
        
        # Adjust weights based on difficulty needs
        available_generators = []
        generator_weights = []
        
        for gen_name, gen_func, expected_difficulty in self.generators:
            # Check if we need more of this difficulty
            current_count = difficulty_buckets.get(expected_difficulty, 0)
            target_count = target_distribution.get(expected_difficulty, 0)
            
            # If we have enough of this difficulty, reduce weight
            if current_count >= target_count:
                weight = weights.get(gen_name, 1.0) * 0.3  # Reduce probability
            else:
                # Increase weight if we need more
                need_ratio = 1.0 - (current_count / max(1, target_count))
                weight = weights.get(gen_name, 1.0) * (1.0 + need_ratio)
            
            available_generators.append((gen_name, gen_func))
            generator_weights.append(weight)
        
        # Normalize weights
        total_weight = sum(generator_weights)
        if total_weight > 0:
            generator_weights = [w / total_weight for w in generator_weights]
        
        # Select based on weights
        return random.choices(available_generators, weights=generator_weights, k=1)[0]
    
    def generate_pool(self, target_pool_size: int = 250, 
                     min_per_difficulty: Optional[Dict[str, int]] = None) -> None:
        """Generate a large pool of puzzles with improved success rate.
        
        Args:
            target_pool_size: Target number of puzzles to generate
            min_per_difficulty: Minimum puzzles per difficulty level
        """
        if min_per_difficulty is None:
            min_per_difficulty = {
                'easy': int(target_pool_size * 0.10),
                'medium': int(target_pool_size * 0.30),
                'hard': int(target_pool_size * 0.40),
                'expert': int(target_pool_size * 0.20)
            }
        
        target_distribution = {
            'easy': int(target_pool_size * 0.10),
            'medium': int(target_pool_size * 0.30),
            'hard': int(target_pool_size * 0.40),
            'expert': int(target_pool_size * 0.20)
        }
        
        puzzle_id = 0
        attempts = 0
        max_attempts = target_pool_size * 20  # Increased from 5 to 20
        
        # Track difficulty buckets
        difficulty_buckets = defaultdict(int)
        
        self.stats.start()
        print(f"Generating pool of {target_pool_size} puzzles...")
        print(f"Max attempts: {max_attempts}")
        
        while attempts < max_attempts:
            attempts += 1
            
            # Check if we've reached target and minimums
            if len(self.puzzles) >= target_pool_size:
                # Check if we have minimums for each difficulty
                all_minimums_met = all(
                    difficulty_buckets[level] >= min_per_difficulty.get(level, 0)
                    for level in ['easy', 'medium', 'hard', 'expert']
                )
                if all_minimums_met:
                    break
            
            # Select generator (weighted)
            gen_name, gen_func = self._select_generator_weighted(difficulty_buckets, target_distribution)
            pid = f"{puzzle_id:03d}"
            
            try:
                problem, solution = gen_func(pid)
                
                # If solution not provided, solve it
                if solution is None:
                    solution = solve_bfs(problem, time_limit=30.0, use_cache=True)  # Increased timeout
                    if solution is None:
                        self.stats.record_attempt(gen_name, success=False, reason='timeout')
                        continue
                
                # Verify solution
                is_valid, final_string = verify_solution(problem, solution)
                if not is_valid:
                    self.stats.record_attempt(gen_name, success=False, reason='invalid')
                    continue
                
                # Check for duplicates (improved)
                if self._is_duplicate(problem):
                    self.stats.record_attempt(gen_name, success=False, reason='duplicate')
                    continue
                
                # Analyze difficulty
                metrics = analyze_difficulty(problem, solution)
                difficulty_level = metrics.difficulty_level()
                
                # Quality checks
                if is_trivial_puzzle(problem, solution):
                    self.stats.record_attempt(gen_name, success=False, reason='trivial')
                    continue
                
                # Check solution uniqueness (optional, can be slow)
                # if not check_solution_uniqueness(problem, solution, max_attempts=3):
                #     continue  # Skip if multiple solutions
                
                # Compute quality score
                quality_score = metrics.compute_quality_score()
                
                # Record success
                self.stats.record_attempt(gen_name, success=True)
                self.stats.record_success(gen_name, difficulty_level)
                difficulty_buckets[difficulty_level] += 1
                
                # Store puzzle
                self.puzzles.append(problem)
                self.solutions.append(Solution(problem_id=pid, solution=solution))
                self.metadata.append({
                    'problem_id': pid,
                    'generator': gen_name,
                    'difficulty_score': metrics.compute_difficulty_score(),
                    'difficulty_level': difficulty_level,
                    'solution_length': metrics.solution_length,
                    'string_length': metrics.initial_string_length,
                    'branching_factor': round(metrics.branching_factor, 2),
                    'num_distractors': metrics.num_distractors,
                    'has_expansion': metrics.has_expansion,
                    'quality_score': round(quality_score, 2),
                })
                puzzle_id += 1
                
                # Progress updates
                if puzzle_id % 25 == 0 or puzzle_id == len(self.puzzles):
                    self.stats.print_progress(puzzle_id, target_pool_size)
                    
            except Exception as e:
                self.stats.record_attempt(gen_name, success=False, reason='exception')
                continue
        
        print(f"\n✅ Generated {len(self.puzzles)} puzzles in pool")
        self.stats.print_generator_stats()
        print(f"\nFinal difficulty distribution:")
        for level in ['easy', 'medium', 'hard', 'expert']:
            count = difficulty_buckets[level]
            print(f"  {level}: {count}")
    
    def select_representative(self, target_count: int = 100) -> None:
        """Select representative puzzles with improved curation."""
        if len(self.puzzles) == 0:
            print("No puzzles to select from!")
            return
        
        # Bucket by difficulty
        difficulty_buckets = defaultdict(list)
        for i, meta in enumerate(self.metadata):
            level = meta['difficulty_level']
            difficulty_buckets[level].append(i)
        
        # Target distribution (optimized for LLM reasoning evaluation)
        target_distribution = {
            'easy': int(target_count * 0.10),    # concat_2 (baseline)
            'medium': int(target_count * 0.30),  # backward_3, sort_3
            'hard': int(target_count * 0.40),    # backward_5, sort_4, multiphase, palin_3
            'expert': int(target_count * 0.20)   # backward_7
        }
        
        # Check if expert level is missing and redistribute slots
        if 'expert' not in difficulty_buckets or len(difficulty_buckets['expert']) == 0:
            expert_slots = target_distribution['expert']
            print(f"⚠️  No expert puzzles found. Redistributing {expert_slots} slots...")
            # Redistribute: 50% to hard, 30% to medium, 20% to easy
            target_distribution['hard'] += int(expert_slots * 0.5)
            target_distribution['medium'] += int(expert_slots * 0.3)
            target_distribution['easy'] += expert_slots - int(expert_slots * 0.5) - int(expert_slots * 0.3)
            target_distribution['expert'] = 0
        
        # Balanced selection with generator-specific targets
        # Ensures all reasoning types are represented while controlling distribution
        all_available_generators = set(meta['generator'] for meta in self.metadata)
        
        # Generator-specific target distribution (out of 100)
        # Reduced backward_7, increased palin/sort/multiphase for better diversity
        generator_targets = {
            'concat_2': 10,      # Easy baseline
            'backward_3': 15,    # Medium sequential
            'backward_5': 10,    # Hard sequential
            'backward_7': 32,    # Expert sequential (reduced from 50 to 30-40 range)
            'sort_3': 10,        # Medium algorithmic (increased from ~5)
            'sort_4': 10,        # Hard algorithmic (increased from ~5)
            'multiphase': 8,     # Hard multi-phase (increased from ~2)
            'palin_3': 5,        # Hard pattern recognition (increased from ~2)
        }
        
        # Normalize targets to match available generators
        available_targets = {gen: generator_targets.get(gen, 0) 
                           for gen in all_available_generators if gen in generator_targets}
        total_target = sum(available_targets.values())
        
        # Scale targets to match target_count
        if total_target > 0:
            scale_factor = target_count / total_target
            generator_targets = {gen: int(count * scale_factor) 
                               for gen, count in available_targets.items()}
        else:
            # Fallback: equal distribution
            per_gen = target_count // len(all_available_generators)
            generator_targets = {gen: per_gen for gen in all_available_generators}
        
        min_pool_size = 2  # Generator must have at least 2 puzzles to be included
        
        print(f"\nGenerator-specific selection targets:")
        for gen, target in sorted(generator_targets.items()):
            print(f"  {gen:15s}: {target:3d} puzzles")
        
        # Build generator buckets across all difficulties
        generator_buckets = defaultdict(list)
        for i, meta in enumerate(self.metadata):
            generator_buckets[meta['generator']].append(i)
        
        # First pass: Select target amount from each generator
        selected_indices = []
        generator_selected = defaultdict(int)
        
        for gen, target in generator_targets.items():
            if gen not in generator_buckets:
                continue
            candidates = generator_buckets[gen]
            
            # Only include if generator has enough puzzles in pool
            if len(candidates) < min_pool_size:
                print(f"  ⚠️  Skipping {gen}: only {len(candidates)} puzzles in pool (< {min_pool_size})")
                continue
            
            # Sort by quality score (best first)
            candidates.sort(key=lambda i: -self.metadata[i].get('quality_score', 50))
            
            # Select target amount (but use all if fewer available)
            needed = min(target, len(candidates))
            selected_indices.extend(candidates[:needed])
            generator_selected[gen] = needed
        
        print(f"Selected {len(selected_indices)} puzzles from generator targets")
        
        # Second pass: Fill remaining slots, respecting generator limits
        remaining_slots = target_count - len(selected_indices)
        if remaining_slots > 0:
            # Get already selected indices as set for fast lookup
            selected_set = set(selected_indices)
            
            # Fill remaining slots, but don't exceed generator targets
            # Prioritize generators that are below their target
            for gen, target in sorted(generator_targets.items(), key=lambda x: -x[1]):
                if remaining_slots <= 0:
                    break
                
                current_count = generator_selected.get(gen, 0)
                if current_count >= target:
                    continue  # Already at or above target
                
                if gen not in generator_buckets:
                    continue
                
                # Get candidates that aren't already selected
                candidates = [i for i in generator_buckets[gen] if i not in selected_set]
                if len(candidates) == 0:
                    continue
                
                # Sort by quality score
                candidates.sort(key=lambda i: -self.metadata[i].get('quality_score', 50))
                
                # Add up to target (or remaining slots, whichever is smaller)
                needed = min(target - current_count, len(candidates), remaining_slots)
                selected_indices.extend(candidates[:needed])
                generator_selected[gen] += needed
                remaining_slots -= needed
            
            # If still have slots, fill by difficulty distribution
            if remaining_slots > 0:
                selected_set = set(selected_indices)
                for level, count in target_distribution.items():
                    if count == 0 or remaining_slots <= 0:
                        continue
                    
                    # Count how many we already have from this difficulty
                    already_in_level = sum(1 for i in selected_indices 
                                         if self.metadata[i]['difficulty_level'] == level)
                    needed = max(0, count - already_in_level)
                    
                    if needed == 0:
                        continue
                    
                    # Get candidates from this difficulty that aren't already selected
                    candidates = [i for i in difficulty_buckets[level] if i not in selected_set]
                    if len(candidates) == 0:
                        continue
                    
                    # Sort by quality score
                    candidates.sort(key=lambda i: -self.metadata[i].get('quality_score', 50))
                    
                    # Add up to needed
                    to_add = min(needed, len(candidates), remaining_slots)
                    selected_indices.extend(candidates[:to_add])
                    remaining_slots -= to_add
        
        # If still have slots, fill with best remaining puzzles
        if remaining_slots > 0:
            selected_set = set(selected_indices)
            remaining = [i for i in range(len(self.metadata)) if i not in selected_set]
            remaining.sort(key=lambda i: -self.metadata[i].get('quality_score', 50))
            selected_indices.extend(remaining[:remaining_slots])
        
        # Trim to exact target_count if needed
        selected_indices = selected_indices[:target_count]
        
        # Update lists with selected puzzles
        self.puzzles = [self.puzzles[i] for i in selected_indices]
        self.solutions = [self.solutions[i] for i in selected_indices]
        self.metadata = [self.metadata[i] for i in selected_indices]
        
        # Renumber problem IDs
        for i, (puzzle, solution, meta) in enumerate(zip(self.puzzles, self.solutions, self.metadata)):
            new_id = f"{i:03d}"
            puzzle.problem_id = new_id
            solution.problem_id = new_id
            meta['problem_id'] = new_id
        
        print(f"✅ Selected {len(self.puzzles)} representative puzzles")
        
        # Print generator distribution
        gen_counts = defaultdict(int)
        for meta in self.metadata:
            gen_counts[meta['generator']] += 1
        print(f"\nGenerator distribution in selected dataset:")
        for gen, count in sorted(gen_counts.items()):
            print(f"  {gen:15s}: {count:3d} puzzles")
    
    def _balance_strategies(self, indices: List[int], target_count: int) -> List[int]:
        """Ensure strategy diversity in selection with minimum per generator."""
        if len(indices) <= target_count:
            return indices
        
        # Count strategies in current selection
        strategy_counts = defaultdict(int)
        for i in indices:
            strategy_counts[self.metadata[i]['generator']] += 1
        
        # Calculate minimum puzzles per generator (ensure diversity)
        all_generators = set(self.metadata[i]['generator'] for i in indices)
        min_per_generator = max(1, target_count // (len(all_generators) * 2))  # At least 1-2 per generator
        
        # First pass: ensure minimum per generator
        selected = []
        generator_selected = defaultdict(int)
        
        # Sort by strategy diversity (prefer less common strategies)
        indices_sorted = sorted(indices, key=lambda i: strategy_counts[self.metadata[i]['generator']])
        
        for i in indices_sorted:
            gen = self.metadata[i]['generator']
            if generator_selected[gen] < min_per_generator:
                selected.append(i)
                generator_selected[gen] += 1
                if len(selected) >= target_count:
                    break
        
        # Second pass: fill remaining slots with best quality puzzles
        remaining = [i for i in indices_sorted if i not in selected]
        remaining.sort(key=lambda i: -self.metadata[i].get('quality_score', 50))
        selected.extend(remaining[:target_count - len(selected)])
        
        return selected[:target_count]
    
    def _ensure_diversity(self, indices: List[int], target_count: int) -> List[int]:
        """Ensure diversity in string lengths and solution lengths."""
        if len(indices) <= target_count:
            return indices
        
        # Group by similar characteristics
        seen_combos = set()
        diverse_indices = []
        
        for i in indices:
            meta = self.metadata[i]
            # Create signature based on string length and solution length ranges
            str_len_bucket = (meta['string_length'] // 5) * 5  # Bucket by 5
            sol_len_bucket = meta['solution_length']  # Exact match
            combo = (str_len_bucket, sol_len_bucket, meta['generator'])
            
            if combo not in seen_combos or len(diverse_indices) < target_count:
                seen_combos.add(combo)
                diverse_indices.append(i)
                if len(diverse_indices) >= target_count:
                    break
        
        # Fill remaining slots if needed
        if len(diverse_indices) < target_count:
            remaining = [i for i in indices if i not in diverse_indices]
            diverse_indices.extend(remaining[:target_count - len(diverse_indices)])
        
        return diverse_indices[:target_count]
    
    def save_dataset(self, output_dir: Path) -> None:
        """Save puzzles, solutions, and metadata to files."""
        puzzles_dir = output_dir / "puzzles"
        solutions_dir = output_dir / "solutions"
        puzzles_dir.mkdir(parents=True, exist_ok=True)
        solutions_dir.mkdir(parents=True, exist_ok=True)
        
        # Save puzzles
        for puzzle in self.puzzles:
            puzzle_path = puzzles_dir / f"{puzzle.problem_id}.json"
            with open(puzzle_path, 'w') as f:
                json.dump({
                    'problem_id': puzzle.problem_id,
                    'initial_string': puzzle.initial_string,
                    'transitions': [
                        {'src': t.src, 'tgt': t.tgt}
                        for t in puzzle.transitions
                    ]
                }, f, indent=2)
        
        # Save solutions
        for solution in self.solutions:
            solution_path = solutions_dir / f"{solution.problem_id}.json"
            with open(solution_path, 'w') as f:
                json.dump({
                    'problem_id': solution.problem_id,
                    'solution': solution.solution
                }, f, indent=2)
        
        # Save metadata
        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        print(f"✅ Saved dataset to {output_dir}")
    
    def print_statistics(self) -> None:
        """Print dataset statistics."""
        if not self.metadata:
            print("No metadata available")
            return
        
        difficulty_counts = defaultdict(int)
        strategy_counts = defaultdict(int)
        quality_scores = []
        
        for meta in self.metadata:
            difficulty_counts[meta['difficulty_level']] += 1
            strategy_counts[meta['generator']] += 1
            quality_scores.append(meta.get('quality_score', 50))
        
        print("\n" + "="*50)
        print("Dataset Statistics")
        print("="*50)
        print(f"Total puzzles: {len(self.puzzles)}")
        print(f"\nDifficulty distribution:")
        for level in ['easy', 'medium', 'hard', 'expert']:
            count = difficulty_counts[level]
            pct = (count / len(self.puzzles)) * 100 if self.puzzles else 0
            print(f"  {level:8s}: {count:3d} ({pct:5.1f}%)")
        
        print(f"\nStrategy distribution:")
        for strategy, count in sorted(strategy_counts.items()):
            print(f"  {strategy:15s}: {count:3d}")
        
        if quality_scores:
            print(f"\nQuality scores: min={min(quality_scores):.1f}, "
                  f"max={max(quality_scores):.1f}, "
                  f"avg={sum(quality_scores)/len(quality_scores):.1f}")
        
        print(f"\nSolution length range: {min(m['solution_length'] for m in self.metadata)} - {max(m['solution_length'] for m in self.metadata)}")
        print(f"String length range: {min(m['string_length'] for m in self.metadata)} - {max(m['string_length'] for m in self.metadata)}")
        print("="*50)
    
    def validate_dataset(self) -> bool:
        """Validate all puzzles in the dataset."""
        print("\n🔍 Validating dataset...")
        all_valid = True
        
        for puzzle, solution in zip(self.puzzles, self.solutions):
            is_valid, final_string = verify_solution(puzzle, solution.solution)
            if not is_valid:
                print(f"❌ Invalid solution for puzzle {puzzle.problem_id}: final_string='{final_string}'")
                all_valid = False
        
        if all_valid:
            print("✅ All puzzles validated successfully!")
        else:
            print("❌ Some puzzles failed validation!")
        
        return all_valid


def main():
    """Main entry point."""
    # Setup paths
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "data"
    
    print("🧩 SED Puzzle Dataset Generation (Improved)")
    print("="*50)
    
    # Clear cache
    clear_cache()
    
    # Generate dataset
    generator = DatasetGenerator(seed=42)
    
    # Step 1: Generate large pool
    generator.generate_pool(target_pool_size=250)
    
    # Step 2: Validate pool
    generator.validate_dataset()
    
    # Step 3: Select representative 100
    generator.select_representative(target_count=100)
    
    # Step 4: Validate final dataset
    generator.validate_dataset()
    
    # Step 5: Print statistics
    generator.print_statistics()
    
    # Step 6: Save dataset
    generator.save_dataset(output_dir)
    
    print("\n✅ Dataset generation complete!")


if __name__ == "__main__":
    main()
