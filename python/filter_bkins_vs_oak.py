#!/usr/bin/env python3
import sys
from collections import defaultdict

def parse_blast_results(blast_file):
    hits = defaultdict(lambda: {'oak': [], 'insect': []})
    print("Parsing BLAST results...")
    with open(blast_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            query_id = fields[0]
            subject_id = fields[1]
            identity = float(fields[2])
            if subject_id.startswith(('Nv_', 'Am_')):  # Adjust for actual Nasonia and Apis prefixes
                category = 'insect'
            elif subject_id.startswith('Oak_'):  # Adjust for oak prefixes
                category = 'oak'
            else:
                continue
            hits[query_id][category].append({
                'subject': subject_id,
                'identity': identity
            })
    print("Found hits for {} query proteins".format(len(hits)))
    return hits

def find_candidates(hits, min_difference=5):  # Adjust min_difference as needed
    print("Finding candidates with higher similarity to oak than to Nasonia or Apis...")
    candidates = []
    for query_id, categories in hits.items():
        if not categories['oak'] or not categories['insect']:
            continue
        best_oak = max(categories['oak'], key=lambda x: x['identity'])
        best_insect = max(categories['insect'], key=lambda x: x['identity'])
        oak_id = best_oak['identity']
        insect_id = best_insect['identity']
        difference = oak_id - insect_id
        if difference >= min_difference:
            candidates.append({
                'query': query_id,
                'oak_hit': best_oak['subject'],
                'oak_identity': oak_id,
                'insect_hit': best_insect['subject'],
                'insect_identity': insect_id,
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
            "Best_oak_hit",
            "Oak_identity",
            "Best_insect_hit",
            "Insect_identity",
            "Difference"
        ))
        for c in candidates:
            print("{}\t{}\t{:.1f}\t{}\t{:.1f}\t{:.1f}".format(
                c['query'],
                c['oak_hit'],
                c['oak_identity'],
                c['insect_hit'],
                c['insect_identity'],
                c['difference']
            ))
        print("Found {} potential candidates".format(len(candidates)))
    else:
        print("No candidates found matching criteria")

if __name__ == "__main__":
    main()
