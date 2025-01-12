# codexgen/transformers.py
from .config import RNA_CODON_TABLE
class CodexTransformers:
    """
    This class provides transformations for DNA sequences, including RNA transcription
    and protein translation.
    """
    def __init__(self):
        self.codon_table = RNA_CODON_TABLE
        self.reverse_codon_table = {value: key for key, value in RNA_CODON_TABLE.items()}
        

    def dna_to_rna(self, dna_sequence: str) -> str:
        """
        Transcribe a DNA sequence into RNA by replacing 'T' with 'U'.

        :param dna_sequence: DNA sequence as a string
        :return: Transcribed RNA sequence
        """
        if not dna_sequence:
            raise ValueError("DNA sequence cannot be empty.")

        if any(nucleotide not in {'A', 'T', 'C', 'G'} for nucleotide in dna_sequence):
            raise ValueError("Invalid nucleotides found in DNA sequence.")

        return dna_sequence.replace('T', 'U')

    def dna_to_protein(self, dna_sequence: str) -> str:
        """
        Translate a DNA sequence into a protein sequence using standard codon tables.

        :param dna_sequence: DNA sequence as a string
        :return: Protein sequence as a string
        """

        if not dna_sequence:
            raise ValueError("DNA sequence cannot be empty.")

        if len(dna_sequence) % 3 != 0:
            raise ValueError("DNA sequence length must be a multiple of 3.")

        protein_sequence = ""
        for i in range(0, len(dna_sequence), 3):
            codon = dna_sequence[i:i+3]
            protein_sequence += self.codon_table.get(codon, '?')  # '?' for unknown codons

        return protein_sequence

    def reverse_complement(self, dna_sequence: str) -> str:
        """
        Generate the reverse complement of a DNA sequence.

        :param dna_sequence: DNA sequence as a string
        :return: Reverse complement DNA sequence
        """
        complement = {
            'A': 'T',
            'T': 'A',
            'C': 'G',
            'G': 'C'
        }

        if not dna_sequence:
            raise ValueError("DNA sequence cannot be empty.")

        if any(nucleotide not in complement for nucleotide in dna_sequence):
            raise ValueError("Invalid nucleotides found in DNA sequence.")

        reversed_sequence = reversed(dna_sequence)
        return ''.join(complement[nucleotide] for nucleotide in reversed_sequence)

    
    def rna_to_dna(self, rna_sequence: str) -> str:
        """
        Transcribe an RNA sequence into DNA by replacing 'U' with 'T'.

        :param rna_sequence: RNA sequence as a string
        :return: Transcribed DNA sequence
        """
        if not rna_sequence:
            raise ValueError("RNA sequence cannot be empty.")

        if any(nucleotide not in {'A', 'U', 'C', 'G'} for nucleotide in rna_sequence):
            raise ValueError("Invalid nucleotides found in RNA sequence.")

        return rna_sequence.replace('U', 'T')


    def rna_to_protein(self, rna_sequence: str) -> str:
        """
        Translate an RNA sequence into a protein sequence using standard codon tables.

        :param rna_sequence: RNA sequence as a string
        :return: Protein sequence as a string
        """
        return self.dna_to_protein(self.rna_to_dna(rna_sequence))


    def protein_to_dna(self, protein_sequence: str) -> str:
        """
        Translate a protein sequence into a DNA sequence by using reverse codon table.
        
        :param protein_sequence: Protein sequence as a string
        :return: DNA sequence as a string
        """
        rna_sequence = self.protein_to_rna(protein_sequence)  # Convert protein to RNA first
        return self.rna_to_dna(rna_sequence)  # Then convert RNA to DNA


    def protein_to_rna(self, protein_sequence: str) -> str:
        """
        Translate a protein sequence into an RNA sequence by using reverse codon table.
        
        :param protein_sequence: Protein sequence as a string
        :return: RNA sequence as a string
        """
        rna_sequence = ""
        for amino_acid in protein_sequence:
            codon = self.reverse_codon_table.get(amino_acid, '')
            if codon:
                rna_sequence += codon
            else:
                rna_sequence += '???'  # Handle unknown amino acids
        return rna_sequence



