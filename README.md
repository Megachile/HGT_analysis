# HGT_analysis
Documentation for reproducing analysis of the Quercus virginiana and Belonocnema kinseyi genomes for potential HGT to each other and from bacteria and fungi


# Software Requirements
## Conda Environment
The analysis requires several bioinformatics tools that are managed through a conda environment. To recreate the analysis environment:
conda env create -f environment.yml
conda activate genomics

# Data sources: 

Quercus virginiana (HAP1; Q_virginiana_protein_prefixed.faa; provided privately)

Belonocnema kinseyi (Build: GCF_010883055.1/B_treatae_v1)
1. Insect References:
   - Apis mellifera (Build: GCF_003254395.2/Amel_HAv3.1)
   - Nasonia vitripennis (Build: GCF_009193385.2/Nvit_psr_1.1)
2. Plant References:
   - Arabidopsis thaliana (Build: GCF_000001735.4/TAIR10.1)
   - Populus trichocarpa (Build: GCF_000002775.5/P.trichocarpa_v4.1)

3. Bacterial data:
- NCBI RefSeq bacterial protein sequences
- Source: ftp://ftp.ncbi.nlm.nih.gov/refseq/release/bacteria/ (sourced on September 12, 2024)
- Database created using makeblastdb with protein sequence type (-dbtype prot)


  
4. Fungi:
- NCBI RefSeq fungal protein sequences
- Source: ftp.ncbi.nlm.nih.gov/refseq/release/fungi/fungi.*.protein.faa.gz (sourced on September 12, 2024)
- Database created using makeblastdb with protein sequence type (-dbtype prot)

# Scripts: 

## Prep data:
Prep data file contains code to be run in the console to acquire, unzip, concatenate, and make BLAST dbs for each dataset

## Run BLASTP:
wasp_to_reference.sh:
blasts the B kinseyi proteins against Q virginiana, N vitripennis, and A mellifera sequences

oak_to_reference.sh:
blasts the Q virginiana proteins against B kinseyi, P trichocarpa, and A thaliana sequences

blastp_wasp_vs_bact.sh:
blasts the B kinseyi proteins against N vitripennis, A mellifera, and the combined bacterial sequences

blastp_oak_bact.sh:
blasts the Q virginiana proteins against P trichocarpa, A thaliana, and the combined bacterial sequences

blastp_wasp_fungal.sh: 
blasts the B kinseyi proteins against N vitripennis, A mellifera, and the combined fungal sequences

blastp_fungal.sh:
blasts the Q virginiana proteins against P trichocarpa, A thaliana, and the combined fungal sequences

# Analysis:

HGT Candidate Filtering Criteria:
- Minimum identity: 75% (eliminate low-similarity matches likely to be spurious)
- Maximum own-lineage identity: 50% (remove matches that are highly similar to phylogenetic neighbors)
- Minimum difference: 20% (eliminate proteins that are very similar to both potential donor and to neighbors)
- Maximum identity: 90% (to exclude universally conserved proteins)

## Analyze Results

### filter_bkins_v_oak.py
**Description**: Finds *B. kinseyi* proteins for which identity to an oak protein is significantly higher than to *Nasonia* or *Apis*.

- **Result**: No candidates.

---

### filter_qvirg_v_bkins.py
**Description**: Finds *Q. virginiana* proteins for which identity to a *B. kinseyi* protein is significantly higher than to *Populus* or *Arabidopsis*.

- **Result**: No candidates.

---

### filter_fungal_hgt.py
**Description**: Finds *Q. virginiana* proteins for which identity to a fungal protein is significantly higher than to *Populus* or *Arabidopsis*.

- **Result**: 1 potential HGT candidate:

| Oak_protein                            | Best_fungal_hit      | Fungal_identity | Best_plant_hit           | Plant_identity | Difference |
|----------------------------------------|----------------------|-----------------|--------------------------|----------------|------------|
| Qv_Qvirginiana.HAP1.v1.g2518.t1       | XP_024712885.1       | 76.5            | Pt_XP_052308549.1        | 42.2           | 34.2       |

This is [protoheme IX farnesyltransferase, mitochondrial [Candidozyma pseudohaemuli]](https://www.ncbi.nlm.nih.gov/protein/XP_024712885.1/).

- **Assessment**: Not a likely candidate for genuine HGT.

---

### filter_wasp_fungal_hgt.py
**Description**: Finds *B. kinseyi* proteins for which identity to a fungal protein is significantly higher than to *Nasonia* or *Apis*.

- **Result**: 1 potential HGT candidate:

| Query_protein           | Best_fungal_hit      | Fungal_identity | Best_insect_hit       | Insect_identity | Difference |
|--------------------------|----------------------|-----------------|-----------------------|-----------------|------------|
| Bk_XP_033211786.1       | XP_003671371.2       | 77.8            | Nv_XP_031779649.1     | 48.1            | 29.7       |

This is [hypothetical protein NDAI_0G03510 [Naumovozyma dairenensis CBS 421]](https://www.ncbi.nlm.nih.gov/protein/XP_003671371.2/).

- **Assessment**: Not a likely candidate for genuine HGT.

---

### filter_oak_bact_hgt.py
**Description**: Finds *Q. virginiana* proteins for which identity to a bacterial protein is significantly higher than to *Populus* or *Arabidopsis*.

- **Result**: (BLAST outputs were deleted but there were no candidates.)

---

### filter_wasp_hgt.py
**Description**: Finds *B. kinseyi* proteins for which identity to a bacterial protein is significantly higher than to *Nasonia* or *Apis*.

- **Result**: (BLAST outputs were deleted but there were no candidates.)
- 

# kmer analysis

check_fasta_format.py - look for issues in the formatting of the genomes that will be an obstacle to kmerizing them
conda install -n genomics biopython - install biopython
clean_genome.py - write cleanup script
clean_genomes.slurm - run cleanup script
conda install -c bioconda kmc bwa samtools - install kmc and bwa and samtools

# Create directories for k-mer analysis
mkdir -p /export/martinsons/adam/kmer_analysis/{kmers,shared,mapped}
mkdir -p /export/martinsons/adam/kmer_analysis/temp  # KMC needs a temp directory

using a kmer length of 31
run_kmer_analysis.slurm - reciprocally checks for kmer matches

This found: 
Q. virginiana coverage:
Average coverage: 0.000951613
Regions with coverage: 597155

B. kinseyi coverage:
Average coverage: 0.000481438
Regions with coverage: 470286

conda install -c bioconda pysam - install pysam

find_clusters.py - write script to find overlapping matches 
find_clusters.slurm - run script to find overlapping matches

conda install -c bioconda bedtools - install bedtools

extract_and_blast.py - script to pull out the nucleotide sequences associated with the top matches

Results: 
Lots of highly repetitive sequences in both directions, which can't be BLASTed and are not likely to be HGT. One high match density region in the B kinseyi genome turns out to be an insect LSU rRNA sequence. Also not likely to be HGT.
