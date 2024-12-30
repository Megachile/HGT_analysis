#!/usr/bin/env python3

import sys
from pathlib import Path
import re
from collections import defaultdict

def check_fasta(filepath):
    """
    Check a FASTA file for potential formatting issues
    """
    print(f"\nChecking {filepath}...")
    
    stats = {
        'total_seqs': 0,
        'total_bases': 0,
        'line_lengths': set(),
        'header_lengths': [],
        'unusual_chars': defaultdict(int),
        'lowercase_count': 0,
        'uppercase_count': 0
    }
    
    current_header = None
    sequence_lines = 0
    
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n')
                
                # Empty lines
                if not line:
                    print(f"Warning: Empty line at line {line_num}")
                    continue
                
                # Header lines
                if line.startswith('>'):
                    stats['total_seqs'] += 1
                    stats['header_lengths'].append(len(line))
                    current_header = line[1:]
                    sequence_lines = 0
                    
                    # Check for unusual characters in header
                    unusual = re.findall(r'[^A-Za-z0-9._|-]', current_header)
                    for char in unusual:
                        stats['unusual_chars'][char] += 1
                
                # Sequence lines
                else:
                    sequence_lines += 1
                    stats['line_lengths'].add(len(line))
                    stats['total_bases'] += len(line)
                    
                    # Check case
                    stats['lowercase_count'] += sum(1 for c in line if c.islower())
                    stats['uppercase_count'] += sum(1 for c in line if c.isupper())
                    
                    # Check for non-standard characters
                    if re.search(r'[^ACGTNacgtn\s]', line):
                        unusual = re.findall(r'[^ACGTNacgtn\s]', line)
                        for char in unusual:
                            stats['unusual_chars'][char] += 1
    
    except UnicodeDecodeError:
        print(f"Error: File contains non-UTF-8 characters")
        return None
        
    return stats

def print_stats(stats):
    """Print formatted statistics"""
    if not stats:
        return
        
    print("\nSummary:")
    print(f"Total sequences: {stats['total_seqs']:,}")
    print(f"Total bases: {stats['total_bases']:,}")
    print(f"Line lengths: {sorted(stats['line_lengths'])}")
    print(f"Header length range: {min(stats['header_lengths'])} - {max(stats['header_lengths'])}")
    
    if stats['unusual_chars']:
        print("\nUnusual characters found:")
        for char, count in stats['unusual_chars'].items():
            print(f"'{char}': {count} occurrences")
    
    print(f"\nCase statistics:")
    print(f"Uppercase bases: {stats['uppercase_count']:,}")
    print(f"Lowercase bases: {stats['lowercase_count']:,}")
    
    # Additional warnings
    if len(stats['line_lengths']) > 1:
        print("\nWarning: Inconsistent line lengths detected")
    if stats['lowercase_count'] > 0 and stats['uppercase_count'] > 0:
        print("\nWarning: Mixed case detected")

def main():
    genome_files = [
        "B_kinseyi_genome.fna",
        "Q_virginiana_genome.genome.fa",
        "D_quercuslanigerum_genome.fna"
    ]
    
    for genome in genome_files:
        filepath = Path("/export/martinsons/adam/input_sequences") / genome
        if filepath.exists():
            stats = check_fasta(filepath)
            if stats:
                print_stats(stats)
        else:
            print(f"\nError: Could not find {genome}")

if __name__ == "__main__":
    main()
