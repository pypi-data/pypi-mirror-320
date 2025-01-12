# codexgen/utils.py
import hashlib
from typing import Optional
from cryptography.fernet import Fernet

class CodexUtils:
    """
    A utility class for operations related to DNA sequence validation, checksum generation,
    and encryption key management.
    """

    def checksum(self, data: str) -> str:
        """
        Calculate checksum for the given data.

        :param data: Input data to calculate checksum
        :return: MD5 checksum as a string
        """
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def validate_dna_sequence(self, dna_sequence: str) -> bool:
        """
        Validate if a given DNA sequence contains only valid nucleotides (A, T, C, G).

        :param dna_sequence: DNA sequence to validate
        :return: True if valid, False otherwise
        """
        valid_nucleotides = {'A', 'T', 'C', 'G'}
        return all(nucleotide in valid_nucleotides for nucleotide in dna_sequence)

    def generate_key(self, output_path: Optional[str] = None) -> str:
        """
        Generate a new encryption key for securing DNA data.

        :param output_path: Optional path to save the key to a file
        :return: The generated key as a string
        """
        key = Fernet.generate_key().decode('utf-8')

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(key)
            print(f"Encryption key saved to: {output_path}")

        return key

    def load_key(self, file_path: str) -> str:
        """
        Load an encryption key from a file.

        :param file_path: Path to the file containing the encryption key
        :return: The encryption key as a string
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
