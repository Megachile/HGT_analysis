#!/usr/bin/env python3

import sys
from pathlib import Path
import argparse
from Bio import SeqIO
from Bio.SeqIO import FastaIO
from Bio.Seq import Seq
import logging
from datetime import datetime

def setup_logging(output_dir):
    """Setup logging to both file and console"""
    log_file = output_dir / f"genome_cleaner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def clean_header(header, aggressive=True):
    """Clean FASTA header to remove problematic characters
    
    Args:
        header: The FASTA header string
        aggressive: If True, clean all special characters. If False, only clean spaces.
    """
    if aggressive:
        # Full cleaning for B. kinseyi and D. quercuslanigerum
        cleaned = header.split()[0]  # Take only the first part before space
        cleaned = cleaned.replace(',', '_').replace(';', '_').replace('=', '_').replace(':', '_')
    else:
        # Minimal cleaning for Q. virginiana
        cleaned = header.strip()
    return cleaned

def process_genome(input_file, output_file, line_length=80):
    """Process genome file and clean up formatting issues"""
    total_sequences = 0
    total_bases = 0
    
    logging.info(f"Processing {input_file}")
    
    try:
        with open(output_file, 'w') as out_handle:
            fasta_writer = FastaIO.FastaWriter(out_handle, wrap=line_length)
            fasta_writer.write_header()
            
            for record in SeqIO.parse(input_file, "fasta"):
                total_sequences += 1
                total_bases += len(record.seq)
                
                # Clean header
                record.id = clean_header(record.id)
                record.description = record.id
                
                # Convert sequence to uppercase
                record.seq = record.seq.upper()
                
                # Write the record
                fasta_writer.write_record(record)
                
                if total_sequences % 1000 == 0:
                    logging.info(f"Processed {total_sequences:,} sequences")
            
            fasta_writer.write_footer()
    
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        raise
    
    logging.info(f"Completed processing {total_sequences:,} sequences with {total_bases:,} bases")
    return total_sequences, total_bases

def main():
    parser = argparse.ArgumentParser(description='Clean and standardize genome FASTA files')
    parser.add_argument('input', type=str, help='Input FASTA file')
    parser.add_argument('--output', type=str, help='Output FASTA file (default: input.cleaned.fa)')
    parser.add_argument('--line-length', type=int, default=80, help='Line length for output sequences (default: 80)')
    parser.add_argument('--aggressive-clean', action='store_true', help='Aggressively clean headers (remove all special characters)')
    parser.add_argument('--standardize-case', action='store_true', help='Convert all sequences to uppercase')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not args.output:
        output_path = input_path.parent / f"{input_path.stem}.cleaned{input_path.suffix}"
    else:
        output_path = Path(args.output)
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    setup_logging(output_path.parent)
    
    logging.info(f"Starting genome cleaning process")
    logging.info(f"Input file: {input_path}")
    logging.info(f"Output file: {output_path}")
    
    try:
        total_seqs, total_bases = process_genome(input_path, output_path, args.line_length)
        logging.info(f"Successfully cleaned genome file:")
        logging.info(f"Total sequences processed: {total_seqs:,}")
        logging.info(f"Total bases processed: {total_bases:,}")
    except Exception as e:
        logging.error(f"Failed to process genome: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
