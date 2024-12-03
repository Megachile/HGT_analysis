#!/usr/bin/env python3
import argparse
from collections import defaultdict

def parse_blast_results(blast_file):
    """Parse combined BLAST results and categorize hits by type"""
    hits = defaultdict(lambda: {'bacterial': [], 'insect': []})

    with open(blast_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            if len(fields) < 12:
                continue

            query_id = fields[0]
            subject_id = fields[1]
            identity = float(fields[2])
            aln_length = int(fields[3])
            evalue = float(fields[10])
            bit_score = float(fields[11])

            # Categorize hit
            if subject_id.startswith('Am_|') or subject_id.startswith('Nv_|'):
                category = 'insect'
            else:
                category = 'bacterial'

            hits[query_id][category].append({
                'subject': subject_id,
                'identity': identity,
                'length': aln_length,
                'evalue': evalue,
                'bit_score': bit_score
            })

    return hits

def find_hgt_candidates(hits, min_difference=20, max_conserved=90, min_bact=75, max_insect=50):
    """Find proteins where best bacterial hit has higher identity than best insect hit"""
    candidates = {}

    for query_id, categories in hits.items():
        # Skip if no hits in either category
        if not categories['bacterial'] or not categories['insect']:
            continue

        # Get best hits for each category
        best_bacterial = max(categories['bacterial'], key=lambda x: x['identity'])
        best_insect = max(categories['insect'], key=lambda x: x['identity'])

        bact_id = best_bacterial['identity']
        insect_id = best_insect['identity']
        difference = bact_id - insect_id

               # Apply filters
        if (difference >= min_difference and
            bact_id <= max_conserved and
            bact_id >= min_bact and
            insect_id <= max_insect):

            candidates[query_id] = {
                'bacterial_hit': best_bacterial,
                'insect_hit': best_insect,
                'difference': difference
            }

    return candidates

def main():
    parser = argparse.ArgumentParser(description='Filter for wasp HGT candidates')
    parser.add_argument('blast_file', help='Combined BLAST results file')
    parser.add_argument('--min-difference', type=float, default=20,
                       help='Minimum difference between bacterial and insect identity (default: 20)')
    parser.add_argument('--max-conserved', type=float, default=90,
                       help='Maximum identity to filter out conserved proteins (default: 90)')
    parser.add_argument('--min-bact', type=float, default=75,
                       help='Minimum bacterial identity required (default: 75)')
    parser.add_argument('--max-insect', type=float, default=50,
                       help='Maximum insect identity allowed (default: 50)')
    parser.add_argument('--output', help='Output file (default: stdout)')

    args = parser.parse_args()

    print("Parsing BLAST results...")
    hits = parse_blast_results(args.blast_file)
    print(f"Found hits for {len(hits)} query proteins")

    print("\nFinding HGT candidates...")
    candidates = find_hgt_candidates(
        hits,
        args.min_difference,
        args.max_conserved,
        args.min_bact,
        args.max_insect
    )

    # Sort by difference in identity
    sorted_candidates = sorted(
        candidates.items(),
        key=lambda x: x[1]['difference'],
        reverse=True
    )

     # Prepare output
    output_lines = ["Wasp_protein\tBacterial_hit\tBacterial_identity\tInsect_hit\tInsect_identity\tDifference"]
    for query_id, data in sorted_candidates:
        output_lines.append(
            f"{query_id}\t{data['bacterial_hit']['subject']}\t{data['bacterial_hit']['identity']:.1f}\t"
            f"{data['insect_hit']['subject']}\t{data['insect_hit']['identity']:.1f}\t{data['difference']:.1f}"
        )

    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write('\n'.join(output_lines))
    else:
        print('\n'.join(output_lines))

    print(f"\nFound {len(candidates)} potential HGT candidates", file=sys.stderr)

if __name__ == '__main__':
    import sys
    main()
