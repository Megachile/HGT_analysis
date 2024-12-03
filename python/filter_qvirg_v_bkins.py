#!/usr/bin/env python3
import sys
from collections import defaultdict

def parse_blast_results(blast_file):
    hits = defaultdict(lambda: {'wasp': [], 'other': []})
    print("Parsing BLAST results...")
    with open(blast_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            query_id = fields[0]
            subject_id = fields[1]
            identity = float(fields[2])
            if subject_id.startswith(('Bk_', 'Dq_')):  # Adjust prefixes for wasp proteins
                category = 'wasp'
            else:
                category = 'other'
            hits[query_id][category].append({
                'subject': subject_id,
                'identity': identity
            })
    print("Found hits for {} query proteins".format(len(hits)))
    return hits

def find_candidates(hits, min_difference=20, min_wasp=75, max_other=50, max_identity=90):
    print("Finding HGT candidates with updated criteria...")
    candidates = []
    for query_id, categories in hits.items():
        if not categories['wasp'] or not categories['other']:
            continue
        
        best_wasp = max(categories['wasp'], key=lambda x: x['identity'])
        best_other = max(categories['other'], key=lambda x: x['identity'])
        
        wasp_id = best_wasp['identity']
        other_id = best_other['identity']
        difference = wasp_id - other_id
        
        # Apply the filtering criteria
        if (
            wasp_id >= min_wasp and
            other_id <= max_other and
            difference >= min_difference and
            wasp_id <= max_identity
        ):
            candidates.append({
                'query': query_id,
                'wasp_hit': best_wasp['subject'],
                'wasp_identity': wasp_id,
                'other_hit': best_other['subject'],
                'other_identity': other_id,
                'difference': difference
            })
    return candidates

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: {} <blast_output>".format(sys.argv[0]))
    
    blast_file = sys.argv[1]
    hits = parse_blast_results(blast_file)
    candidates = find_candidates(hits)
    
    if candidates:
        print("{}\t{}\t{}\t{}\t{}\t{}".format(
            "Query_protein",
            "Best_wasp_hit",
            "Wasp_identity",
            "Best_other_hit",
            "Other_identity",
            "Difference"
        ))
        for c in candidates:
            print("{}\t{}\t{:.1f}\t{}\t{:.1f}\t{:.1f}".format(
                c['query'],
                c['wasp_hit'],
                c['wasp_identity'],
                c['other_hit'],
                c['other_identity'],
                c['difference']
            ))
        print("Found {} potential candidates".format(len(candidates)))
    else:
        print("No candidates found matching criteria")

if __name__ == "__main__":
    main()
