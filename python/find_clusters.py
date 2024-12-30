#!/usr/bin/env python3

import pysam
import numpy as np
from collections import defaultdict
import argparse
from pathlib import Path

def find_kmer_clusters(bam_file, min_kmers=3, min_length=100, max_gap=50, min_density=0.1):
    """
    Find clusters of k-mer matches in BAM file.
    
    Parameters:
    - min_kmers: Minimum number of k-mers in a cluster
    - min_length: Minimum length of a cluster (bp)
    - max_gap: Maximum gap between k-mers to be considered same cluster
    - min_density: Minimum k-mers per base pair in cluster
    """
    clusters = []
    bam = pysam.AlignmentFile(bam_file, "rb")
    
    # Process each chromosome/contig
    for ref in bam.references:
        print(f"Processing {ref}...")
        current_cluster = {
            'ref': ref,
            'start': None,
            'end': None,
            'kmers': [],
            'coverage': defaultdict(int)
        }
        
        # Get all k-mer alignments for this reference
        for read in bam.fetch(ref):
            pos = read.reference_start
            end = read.reference_end
            
            # If this is far from current cluster, close current and start new
            if (current_cluster['start'] is not None and 
                pos - current_cluster['end'] > max_gap):
                
                # Process completed cluster
                if len(current_cluster['kmers']) >= min_kmers:
                    cluster_length = current_cluster['end'] - current_cluster['start']
                    if cluster_length >= min_length:
                        # Calculate coverage density
                        coverage_points = len([v for v in current_cluster['coverage'].values() if v > 0])
                        density = coverage_points / cluster_length
                        if density >= min_density:
                            current_cluster['density'] = density
                            current_cluster['n_kmers'] = len(current_cluster['kmers'])
                            clusters.append(current_cluster.copy())
                
                # Start new cluster
                current_cluster = {
                    'ref': ref,
                    'start': pos,
                    'end': end,
                    'kmers': [read.query_name],
                    'coverage': defaultdict(int)
                }
            else:
                # Add to current cluster
                if current_cluster['start'] is None:
                    current_cluster['start'] = pos
                current_cluster['end'] = max(current_cluster['end'] if current_cluster['end'] else pos, end)
                current_cluster['kmers'].append(read.query_name)
            
            # Update coverage
            for p in range(pos, end):
                current_cluster['coverage'][p] += 1
    
    bam.close()
    return clusters

def write_clusters_to_bed(clusters, output_file):
    """Write clusters to BED format"""
    with open(output_file, 'w') as f:
        for i, cluster in enumerate(clusters):
            # BED format: chrom start end name score strand extra
            score = int(cluster['density'] * 1000)  # Scale density to integer score
            f.write(f"{cluster['ref']}\t{cluster['start']}\t{cluster['end']}\t"
                   f"cluster_{i}\t{score}\t+\t{cluster['n_kmers']}\n")

def write_detailed_output(clusters, output_file):
    """Write detailed information about each cluster"""
    with open(output_file, 'w') as f:
        f.write("ref\tstart\tend\tlength\tn_kmers\tdensity\tavg_coverage\n")
        for cluster in clusters:
            length = cluster['end'] - cluster['start']
            avg_cov = sum(cluster['coverage'].values()) / length
            f.write(f"{cluster['ref']}\t{cluster['start']}\t{cluster['end']}\t"
                   f"{length}\t{cluster['n_kmers']}\t{cluster['density']:.3f}\t"
                   f"{avg_cov:.2f}\n")

def main():
    parser = argparse.ArgumentParser(description='Find clusters of shared k-mers in BAM file')
    parser.add_argument('bam_file', help='Input BAM file')
    parser.add_argument('output_prefix', help='Prefix for output files')
    parser.add_argument('--min-kmers', type=int, default=3,
                       help='Minimum number of k-mers in cluster')
    parser.add_argument('--min-length', type=int, default=100,
                       help='Minimum length of cluster in bp')
    parser.add_argument('--max-gap', type=int, default=50,
                       help='Maximum gap between k-mers in cluster')
    parser.add_argument('--min-density', type=float, default=0.1,
                       help='Minimum density of k-mers per bp')
    
    args = parser.parse_args()
    
    # Find clusters
    print(f"Finding clusters with parameters:")
    print(f"  Minimum k-mers: {args.min_kmers}")
    print(f"  Minimum length: {args.min_length}")
    print(f"  Maximum gap: {args.max_gap}")
    print(f"  Minimum density: {args.min_density}")
    
    clusters = find_kmer_clusters(
        args.bam_file,
        min_kmers=args.min_kmers,
        min_length=args.min_length,
        max_gap=args.max_gap,
        min_density=args.min_density
    )
    
    # Write outputs
    bed_file = f"{args.output_prefix}.bed"
    write_clusters_to_bed(clusters, bed_file)
    
    detailed_file = f"{args.output_prefix}.detailed.txt"
    write_detailed_output(clusters, detailed_file)
    
    # Write summary statistics
    stats_file = f"{args.output_prefix}.stats.txt"
    with open(stats_file, 'w') as f:
        f.write(f"Total clusters found: {len(clusters)}\n\n")
        if clusters:
            lengths = [c['end'] - c['start'] for c in clusters]
            kmer_counts = [c['n_kmers'] for c in clusters]
            densities = [c['density'] for c in clusters]
            
            f.write("Cluster length statistics:\n")
            f.write(f"  Mean: {np.mean(lengths):.1f}\n")
            f.write(f"  Median: {np.median(lengths):.1f}\n")
            f.write(f"  Min: {min(lengths)}\n")
            f.write(f"  Max: {max(lengths)}\n\n")
            
            f.write("K-mer count statistics:\n")
            f.write(f"  Mean: {np.mean(kmer_counts):.1f}\n")
            f.write(f"  Median: {np.median(kmer_counts):.1f}\n")
            f.write(f"  Min: {min(kmer_counts)}\n")
            f.write(f"  Max: {max(kmer_counts)}\n\n")
            
            f.write("Density statistics:\n")
            f.write(f"  Mean: {np.mean(densities):.3f}\n")
            f.write(f"  Median: {np.median(densities):.3f}\n")
            f.write(f"  Min: {min(densities):.3f}\n")
            f.write(f"  Max: {max(densities):.3f}\n")

if __name__ == "__main__":
    main()
