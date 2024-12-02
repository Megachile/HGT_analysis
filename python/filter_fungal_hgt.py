#!/usr/bin/env python3
import argparse
import sys
from collections import defaultdict

def parse_blast_results(blast_file, min_difference=20, max_conserved=90, min_fungal=75, max_plant=50):
    """Parse BLAST results and categorize hits by fungal vs plant"""
    hits = defaultdict(lambda: {'fungal': [], 'plant': []})

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
                category = 'fungal'

            hits[query_id][category].append({
                'subject': subject_id,
                'identity': identity
            })

    return hits

def find_hgt_candidates(hits, min_difference=20, max_conserved=90, min_fungal=75, max_plant=50):
    """Find proteins where fungal identity is significantly higher than plant identity"""
    candidates = {}

    for query_id, categories in hits.items():
        # Skip if missing either category
        if not categories['fungal'] or not categories['plant']:
            continue

        # Get best hits
        best_fungal = max(categories['fungal'], key=lambda x: x['identity'])
        best_plant = max(categories['plant'], key=lambda x: x['identity'])

        fungal_id = best_fungal['identity']
        plant_id = best_plant['identity']
        difference = fungal_id - plant_id

        # Apply filters
        if (difference >= min_difference and
            fungal_id <= max_conserved and
            fungal_id >= min_fungal and
            plant_id <= max_plant):

            candidates[query_id] = {
                'fungal_hit': best_fungal,
                'plant_hit': best_plant,
                'difference': difference
