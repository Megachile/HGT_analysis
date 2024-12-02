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

mkdir -p input_sequences

Download reference genomes
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/003/254/395/GCF_003254395.2_Amel_HAv3.1/GCF_003254395.2_Amel_HAv3.1_protein.faa.gz
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/193/385/GCF_009193385.2_Nvit_psr_1.1/GCF_009193385.2_Nvit_psr_1.1_protein.faa.gz
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/735/GCF_000001735.4_TAIR10.1/GCF_000001735.4_TAIR10.1_protein.faa.gz
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/002/775/GCF_000002775.5_P.trichocarpa_v4.1/GCF_000002775.5_P.trichocarpa_v4.1_protein.faa.gz

Unzip files
gunzip *.faa.gz

Move to input directory
mv *.faa input_sequences/
download_bacterial_proteins.sh:
download, unzip, combine, and clean up the bacterial protein reference db from NCBI

prep_fungal_db.sh:
download, unzip, combine, and clean up the fungal protein reference db from NCBI

For oak reference
cat GCF_000001735.4_TAIR10.1_protein.faa GCF_000002775.5_P.trichocarpa_v4.1_protein.faa > combined_plant_insect_proteins.faa

For wasp reference
cat GCF_003254395.2_Amel_HAv3.1_protein.faa GCF_009193385.2_Nvit_psr_1.1_protein.faa > combined_insect_plant_proteins.faa

cat combined_plant_insect_proteins.faa bacterial_proteins.faa > oak_reference_proteins.faa
cat combined_insect_plant_proteins.faa bacterial_proteins.faa > wasp_reference_proteins.faa

makeblastdb -in oak_reference_proteins.faa -dbtype prot -out blast_dbs/oak_reference_db
makeblastdb -in wasp_reference_proteins.faa -dbtype prot -out blast_dbs/wasp_reference_db

Combined fungal + references for wasp:
cat combined_insect_plant_proteins.faa fungal_data/combined_fungal.faa > wasp_fungal_reference.faa

Create BLAST database:
makeblastdb -in wasp_fungal_reference.faa -dbtype prot -out blast_dbs/fungal_wasp_db

## Run BLASTP:

blastp_wasp_vs_bact.sh:
blasts the B kinseyi genome against N vitripennis, A mellifera, and the combined bacterial sequences

blastp_wasp_fungal.sh: 
blasts the B kinseyi genome against N vitripennis, A mellifera, and the combined fungal sequences

# Analyze results:

filter_fungal_hgt.py: 
Finds Q virginiana proteins for which identity to a fungal protein is significantly higher than to Populus or Arabidopsis

filter_wasp_fungal_hgt.py:
Finds B kinseyi proteins for which identity to a fungal protein is significantly higher than to Nasonia or Apis

filter_oak_bact_hgt.py:
Finds Q virginiana proteins for which identity to a fungal protein is significantly higher than to Populus or Arabidopsis

