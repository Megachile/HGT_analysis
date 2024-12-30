import os
from subprocess import run

def extract_sequences(genome_file, cluster_file, output_fasta):
    """
    Extract sequences from a genome based on cluster coordinates.
    """
    # Create a BED file from the cluster file
    bed_file = cluster_file.replace(".txt", ".bed")
    with open(cluster_file, 'r') as infile, open(bed_file, 'w') as outfile:
        for line_number, line in enumerate(infile):
            # Skip header
            if line_number == 0:
                continue
            # Extract ref, start, and end fields
            fields = line.strip().split()
            if len(fields) >= 3:
                ref, start, end = fields[0], fields[1], fields[2]
                outfile.write(f"{ref}\t{start}\t{end}\n")

    # Use bedtools to extract the sequences
    fasta_output = output_fasta
    run([
        "bedtools", "getfasta", 
        "-fi", genome_file, 
        "-bed", bed_file, 
        "-fo", fasta_output
    ])

    print(f"Sequences extracted to {fasta_output}")


def run_blast(fasta_file, db, output_file):
    """
    Run BLAST on the extracted sequences against a specified database.
    """
    run([
        "blastn", 
        "-query", fasta_file, 
        "-db", db, 
        "-out", output_file, 
        "-outfmt", "6",  # Tabular output format
        "-evalue", "1e-5", 
        "-max_target_seqs", "10"
    ])
    print(f"BLAST results saved to {output_file}")


# Main workflow
if __name__ == "__main__":
    # Define paths
    genomes = {
        "bk": "/export/martinsons/adam/input_sequences/B_kinseyi_genome.fna",
        "qv": "/export/martinsons/adam/input_sequences/Q_virginiana_genome.genome.fa"
    }
    cluster_files = {
        "bk": "/export/martinsons/adam/kmer_analysis/clusters/bk_clusters.detailed.txt",
        "qv": "/export/martinsons/adam/kmer_analysis/clusters/qv_clusters.detailed.txt"
    }
    output_fastas = {
        "bk": "/export/martinsons/adam/kmer_analysis/clusters/bk_sequences.fasta",
        "qv": "/export/martinsons/adam/kmer_analysis/clusters/qv_sequences.fasta"
    }

    # Extract sequences for each genome
    for key in genomes:
        extract_sequences(genomes[key], cluster_files[key], output_fastas[key])

    # Optionally, run BLAST (uncomment the following lines if needed)
    # blast_db = "/path/to/blast/db/nt"  # Update with your BLAST database path
    # for key in output_fastas:
    #     output_blast = output_fastas[key].replace(".fasta", "_blast_results.txt")
    #     run_blast(output_fastas[key], blast_db, output_blast)
