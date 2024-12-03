# filter_oak_bact_hgt.py
#!/usr/bin/env python3
import sys
from collections import defaultdict

def parse_blast_results(blast_file):
    hits = defaultdict(lambda: {'bacterial': [], 'plant': []})
    print("Parsing BLAST results...")
    with open(blast_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            query_id = fields[0]
            subject_id = fields[1]
            identity = float(fields[2])
            if subject_id.startswith(('At_|', 'Pt_|')):
                category = 'plant'
            else:
                category = 'bacterial'
            hits[query_id][category].append({
                'subject': subject_id,
                'identity': identity
            })
    print("Found hits for {} query proteins".format(len(hits)))
    return hits

def find_hgt_candidates(hits, min_difference=20, max_conserved=90, min_bacterial=75, max_plant=50):
    print("Finding HGT candidates...")
    candidates = []
    for query_id, categories in hits.items():
        if not categories['bacterial'] or not categories['plant']:
            continue
        best_bacterial = max(categories['bacterial'], key=lambda x: x['identity'])
        best_plant = max(categories['plant'], key=lambda x: x['identity'])
        bacterial_id = best_bacterial['identity']
        plant_id = best_plant['identity']
        difference = bacterial_id - plant_id
        if (difference >= min_difference and
            bacterial_id <= max_conserved and
            bacterial_id >= min_bacterial and
            plant_id <= max_plant):
            candidates.append({
                'query': query_id,
                'bacterial_hit': best_bacterial['subject'],
                'bacterial_identity': bacterial_id,
                'plant_hit': best_plant['subject'],
                'plant_identity': plant_id,
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
            "Best_bacterial_hit",
            "Bacterial_identity",
            "Best_plant_hit",
            "Plant_identity",
            "Difference"
        ))
        for c in candidates:
            print("{}\t{}\t{:.1f}\t{}\t{:.1f}\t{:.1f}".format(
                c['query'],
                c['bacterial_hit'],
                c['bacterial_identity'],
                c['plant_hit'],
                c['plant_identity'],
                c['difference']
            ))
        print("Found {} potential HGT candidates".format(len(candidates)))
    else:
        print("No HGT candidates found matching criteria")

if __name__ == "__main__":
    main()
