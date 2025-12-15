"""
Progress tracking and statistics for dataset generation.
"""

from collections import defaultdict
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import time


@dataclass
class GenerationStats:
    """Statistics tracking for puzzle generation."""
    total_attempts: int = 0
    successful: int = 0
    failed_timeout: int = 0
    failed_invalid: int = 0
    failed_duplicate: int = 0
    failed_exception: int = 0
    
    generator_stats: Dict[str, Dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {
        'attempts': 0,
        'success': 0,
        'timeout': 0,
        'invalid': 0,
        'duplicate': 0,
        'exception': 0
    }))
    
    difficulty_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    start_time: Optional[float] = None
    
    def start(self):
        """Start tracking."""
        self.start_time = time.time()
    
    def record_attempt(self, generator: str, success: bool = False, 
                      reason: Optional[str] = None):
        """Record an attempt."""
        self.total_attempts += 1
        self.generator_stats[generator]['attempts'] += 1
        
        if success:
            self.successful += 1
            self.generator_stats[generator]['success'] += 1
        else:
            if reason == 'timeout':
                self.failed_timeout += 1
                self.generator_stats[generator]['timeout'] += 1
            elif reason == 'invalid':
                self.failed_invalid += 1
                self.generator_stats[generator]['invalid'] += 1
            elif reason == 'duplicate':
                self.failed_duplicate += 1
                self.generator_stats[generator]['duplicate'] += 1
            elif reason == 'exception':
                self.failed_exception += 1
                self.generator_stats[generator]['exception'] += 1
    
    def record_success(self, generator: str, difficulty: str):
        """Record a successful generation."""
        self.difficulty_counts[difficulty] += 1
    
    def get_success_rate(self) -> float:
        """Get overall success rate."""
        if self.total_attempts == 0:
            return 0.0
        return (self.successful / self.total_attempts) * 100
    
    def get_generator_weights(self) -> Dict[str, float]:
        """Get weights for generators based on success rates."""
        weights = {}
        for gen, stats in self.generator_stats.items():
            if stats['attempts'] == 0:
                weights[gen] = 1.0  # Default weight
            else:
                success_rate = stats['success'] / stats['attempts']
                # Weight = success_rate + 0.1 (minimum weight)
                weights[gen] = max(0.1, success_rate + 0.1)
        return weights
    
    def print_progress(self, current_count: int, target_count: int):
        """Print progress information."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        success_rate = self.get_success_rate()
        
        if self.successful > 0:
            avg_time_per_puzzle = elapsed / self.successful
            remaining = target_count - current_count
            estimated_time = avg_time_per_puzzle * remaining
        else:
            estimated_time = 0
        
        print(f"\n📊 Progress: {current_count}/{target_count} puzzles "
              f"({current_count/target_count*100:.1f}%)")
        print(f"   Success rate: {success_rate:.2f}% "
              f"({self.successful}/{self.total_attempts} attempts)")
        print(f"   Failures: timeout={self.failed_timeout}, "
              f"invalid={self.failed_invalid}, duplicate={self.failed_duplicate}, "
              f"exception={self.failed_exception}")
        print(f"   Elapsed: {elapsed:.1f}s, Estimated remaining: {estimated_time:.1f}s")
        
        # Difficulty distribution
        if self.difficulty_counts:
            print(f"   Difficulty: ", end="")
            for level in ['easy', 'medium', 'hard', 'expert']:
                count = self.difficulty_counts[level]
                print(f"{level}={count} ", end="")
            print()
    
    def print_generator_stats(self):
        """Print statistics per generator."""
        print("\n📈 Generator Statistics:")
        print(f"{'Generator':<15} {'Attempts':<10} {'Success':<10} {'Rate':<10}")
        print("-" * 50)
        for gen, stats in sorted(self.generator_stats.items()):
            attempts = stats['attempts']
            success = stats['success']
            rate = (success / attempts * 100) if attempts > 0 else 0
            print(f"{gen:<15} {attempts:<10} {success:<10} {rate:>6.1f}%")

