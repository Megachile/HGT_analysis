#!/usr/bin/env python3
import argparse
import sys
from collections import defaultdict

def parse_blast_results(blast_file, min_difference=20, max_conserved=90, min_bacterial=75, max_plant=50):
    """Parse BLAST results and categorize hits by bacterial vs plant"""
    hits = defaultdict(lambda: {'bacterial': [], 'plant': []})
    with open(blast_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            query_id = fields[0]
            subject_id = fields[1]
            identity = float(fields[2])
            # Categorize based on subject ID prefixes
            if subject_id.startswith(('At_|', 'Pt_|')):
                category = 'plant'
            else:
                category = 'bacterial'
            hits[query_id][category].append({
                'subject': subject_id,
                'identity': identity
            })
    return hits

def find_hgt_candidates(hits, min_difference=20, max_conserved=90, min_bacterial=75, max_plant=50):
    """Find proteins where bacterial identity is significantly higher than plant identity"""
    candidates = {}
    for query_id, categories in hits.items():
        # Skip if missing either category
        if not categories['bacterial'] or not categories['plant']:
            continue
        # Get best hits
        best_bacterial = max(categories['bacterial'], key=lambda x: x['identity'])
        best_plant = max(categories['plant'], key=lambda x: x['identity'])
        bacterial_id = best_bacterial['identity']
        plant_id = best_plant['identity']
        difference = bacterial_id - plant_id
        # Apply filters
        if (difference >= min_difference and
            bacterial_id <= max_conserved and
            bacterial_id >= min_bacterial and
            plant_id <= max_plant):
            candidates[query_id] = {
                'bacterial_hit': best_bacterial,
                'plant_hit': best_plant,
                'difference': difference
            }
    return candidates
