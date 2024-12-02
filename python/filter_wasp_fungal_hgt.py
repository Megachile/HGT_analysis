#!/usr/bin/env python
import sys
from collections import defaultdict

def parse_blast_results(blast_file, min_difference=20, max_conserved=90, min_fungal=75, max_insect=50):
    hits = defaultdict(lambda: {'fungal': [], 'insect': []})

    with open(blast_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')

            query_id = fields[0]
            subject_id = fields[1]
            identity = float(fields[2])
            aln_length = int(fields[3])
            evalue = float(fields[10])

            if subject_id.startswith(('Am_|', 'Nv_|')):
                category = 'insect'
            else:
                category = 'fungal'

            hits[query_id][category].append({
                'subject': subject_id,
                'identity': identity,
                'length': aln_length,
                'evalue': evalue
            })

    return hits

def find_hgt_candidates(hits, min_difference=20, max_conserved=90, min_fungal=75, max_insect=50):
    candidates = {}

    total_proteins = len(hits)
    sys.stderr.write(f"Processing {total_proteins} proteins\n")

    for query_id, categories in hits.items():
        if not categories['fungal'] or not categories['insect']:
            continue

        best_fungal = max(categories['fungal'], key=lambda x: x['identity'])
        best_insect = max(categories['insect'], key=lambda x: x['identity'])

        fungal_id = best_fungal['identity']
        insect_id = best_insect['identity']
        difference = fungal_id - insect_id

        if (difference >= min_difference and
            fungal_id <= max_conserved and
            fungal_id >= min_fungal and
            insect_id <= max_insect):

            candidates[query_id] = {
                'fungal_hit': best_fungal,
                'insect_hit': best_insect,
                'difference': difference
