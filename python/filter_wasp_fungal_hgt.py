# filter_wasp_fungal_hgt.py
#!/usr/bin/env python3
import sys
from collections import defaultdict

def parse_blast_results(blast_file):
    hits = defaultdict(lambda: {'fungal': [], 'insect': []})
    print("Parsing BLAST results...")
    with open(blast_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            query_id = fields[0]
            subject_id = fields[1]
            identity = float(fields[2])
            if subject_id.startswith(('Am_|', 'Nv_|')):
                category = 'insect'
            else:
                category = 'fungal'
            hits[query_id][category].append({
                'subject': subject_id,
                'identity': identity
            })
    print("Found hits for {} query proteins".format(len(hits)))
    return hits

def find_hgt_candidates(hits, min_difference=20, max_conserved=90, min_fungal=75, max_insect=50):
    print("Finding HGT candidates...")
    candidates = []
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
            candidates.append({
                'query': query_id,
                'fungal_hit': best_fungal['subject'],
                'fungal_identity': fungal_id,
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
    candidates = find_hgt_candidates(hits)
    
    if candidates:
        print("{}\t{}\t{}\t{}\t{}\t{}".format(
            "Query_protein",
            "Best_fungal_hit",
            "Fungal_identity",
            "Best_insect_hit",
            "Insect_identity",
            "Difference"
        ))
        for c in candidates:
            print("{}\t{}\t{:.1f}\t{}\t{:.1f}\t{:.1f}".format(
                c['query'],
                c['fungal_hit'],
                c['fungal_identity'],
                c['insect_hit'],
                c['insect_identity'],
                c['difference']
            ))
        print("Found {} potential HGT candidates".format(len(candidates)))
    else:
        print("No HGT candidates found matching criteria")

if __name__ == "__main__":
    main()
