# HGT_analysis
Documentation for reproducing analysis of the Quercus virginiana and Belonocnema kinseyi genomes for potential HGT to each other and from bacteria and fungi


# Software Requirements
## Conda Environment
The analysis requires several bioinformatics tools that are managed through a conda environment. To recreate the analysis environment:
conda env create -f environment.yml
conda activate genomics

# Data sources: 

Quercus virginiana (provided privately)

Belonocnema kinseyi (Build: GCF_010883055.1/B_treatae_v1)
1. Insect References:
   - Apis mellifera (Build: GCF_003254395.2/Amel_HAv3.1)
   - Nasonia vitripennis (Build: GCF_009193385.2/Nvit_psr_1.1)
2. Plant References:
   - Arabidopsis thaliana (Build: GCF_000001735.4/TAIR10.1)
   - Populus trichocarpa (Build: GCF_000002775.5/P.trichocarpa_v4.1)

3. Bacterial data:
- NCBI RefSeq bacterial protein sequences
- Source: ftp://ftp.ncbi.nlm.nih.gov/refseq/release/bacteria/
- Database created using makeblastdb with protein sequence type (-dbtype prot)


  
4. Fungi:
- NCBI RefSeq fungal protein sequences
- Source: ftp.ncbi.nlm.nih.gov/refseq/release/fungi/fungi.*.protein.faa.gz
- Database created using makeblastdb with protein sequence type (-dbtype prot)

# Analysis:

HGT Candidate Filtering Criteria:
- Minimum bacterial identity: 75%
- Maximum insect/plant identity: 50%
- Minimum difference: 20%
- Maximum identity: 90% (to exclude universally conserved proteins)

# Scripts: 

## Prep data:
Prep data file contains code to be run in the console to acquire, unzip, concatenate, and make BLAST dbs for each dataset

## Run BLASTP:

blastp_wasp_vs_bact.sh:
blasts the B kinseyi genome against N vitripennis, A mellifera, and the combined bacterial sequences

blastp_wasp_fungal.sh: 
blasts the B kinseyi genome against N vitripennis, A mellifera, and the combined fungal sequences

## Analyze results:

filter_fungal_hgt.py: 
Finds Q virginiana proteins for which identity to a fungal protein is significantly higher than to Populus or Arabidopsis

filter_wasp_fungal_hgt.py:
Finds B kinseyi proteins for which identity to a fungal protein is significantly higher than to Nasonia or Apis

filter_oak_bact_hgt.py:
Finds Q virginiana proteins for which identity to a fungal protein is significantly higher than to Populus or Arabidopsis

