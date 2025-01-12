# codexgen/code.py

import base64
import json
import os
from typing import Any
from cryptography.fernet import Fernet

class CodexGen:
    def __init__(self, encryption_key: str = None):
        """
        Initialize the CodexGen instance with an optional encryption key.

        :param encryption_key: Optional encryption key for encryption/decryption
        """
        self.mapping = {
            "00": "A",
            "01": "T",
            "10": "C",
            "11": "G"
        }
        self.reverse_mapping = {v: k for k, v in self.mapping.items()}

        # Setup encryption
        if encryption_key:
            self.fernet = Fernet(encryption_key)
        else:
            self.fernet = None

    def to_dna(self, data: Any = None) -> str:
        """
        Convert input data into a DNA sequence.

        :param data: The data to convert into a DNA sequence. Can be a string, dict, list, int, or bool.
        :return: A string representing the DNA sequence
        :raises ValueError: If no data is provided
        """
        if data is not None:
            if isinstance(data, (str, dict, list, int, bool)):
                json_data = json.dumps(data)
            else:
                json_data = str(data)

            binary_data = ''.join(format(byte, '08b') for byte in json_data.encode('utf-8'))
            dna_sequence = ''.join(self.mapping[binary_data[i:i+2]] for i in range(0, len(binary_data), 2))

            return dna_sequence
        else:
            raise ValueError("Data must be provided for conversion to DNA.")

    def to_binary(self, dna_sequence: str) -> Any:
        """
        Convert a DNA sequence back into its original data format (e.g., string, dict, list, etc.).

        :param dna_sequence: The DNA sequence to convert
        :return: The original data in its native format
        :raises ValueError: If the DNA sequence contains invalid nucleotides
        """
        valid_nucleotides = {'A', 'T', 'C', 'G'}
        if any(nucleotide not in valid_nucleotides for nucleotide in dna_sequence):
            raise ValueError(f"Invalid nucleotide found in DNA sequence: {dna_sequence}")

        binary_data = ''.join(self.reverse_mapping[nucleotide] for nucleotide in dna_sequence)
        byte_data = int(binary_data, 2).to_bytes((len(binary_data) + 7) // 8, byteorder='big')
        json_data = byte_data.decode('utf-8')

        return json.loads(json_data)

    def encrypt(self, dna_sequence: str) -> str:
        """
        Encrypt a DNA sequence using the provided encryption key.

        :param dna_sequence: The DNA sequence to encrypt
        :return: The encrypted DNA sequence as a string
        :raises ValueError: If the encryption key is not set
        """
        if not self.fernet:
            raise ValueError("Encryption key is not set.")
        encrypted_data = self.fernet.encrypt(dna_sequence.encode('utf-8'))
        return encrypted_data.decode('utf-8')

    def decrypt(self, encrypted_dna: str) -> str:
        """
        Decrypt an encrypted DNA sequence using the provided encryption key.

        :param encrypted_dna: The encrypted DNA sequence to decrypt
        :return: The decrypted DNA sequence as a string
        :raises ValueError: If the encryption key is not set
        """
        if not self.fernet:
            raise ValueError("Encryption key is not set.")
        decrypted_data = self.fernet.decrypt(encrypted_dna.encode('utf-8'))
        return decrypted_data.decode('utf-8')

    def load_file(self, file_path: str) -> str:
        """
        Load the content of a file.

        :param file_path: The path to the file to load
        :return: The content of the file
        :raises FileNotFoundError: If the file does not exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r') as file:
            return file.read()

    def save_file(self, data: str, output_path: str):
        """
        Save data to a file.

        :param data: The data to save to the file
        :param output_path: The path where the file will be saved
        """
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(data)
        print(f"File saved at: {output_path}")

    def validate_file(self, file_path: str):
        """
        Validate that the provided path is a valid file.

        :param file_path: The path to validate
        :raises FileNotFoundError: If the path is not a valid file
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Provided path is not a valid file: {file_path}")

    def dna_statistics(self, dna_sequence: str) -> dict:
        """
        Provide statistics about the DNA sequence.

        :param dna_sequence: DNA sequence as a string
        :return: Dictionary with nucleotide counts and sequence length
        :raises ValueError: If the DNA sequence contains invalid nucleotides
        """
        valid_nucleotides = {'A', 'T', 'C', 'G'}
        if any(nucleotide not in valid_nucleotides for nucleotide in dna_sequence):
            raise ValueError("Invalid nucleotides found in the DNA sequence.")

        stats = {nucleotide: dna_sequence.count(nucleotide) for nucleotide in valid_nucleotides}
        stats['length'] = len(dna_sequence)
        return stats

    def compare_dna(self, dna_seq1: str, dna_seq2: str) -> float:
        """
        Compare two DNA sequences and return the similarity percentage.

        :param dna_seq1: First DNA sequence
        :param dna_seq2: Second DNA sequence
        :return: Similarity percentage
        :raises ValueError: If the DNA sequences are not of equal length
        """
        if len(dna_seq1) != len(dna_seq2):
            raise ValueError("DNA sequences must be of equal length to compare.")

        matches = sum(1 for a, b in zip(dna_seq1, dna_seq2) if a == b)
        return (matches / len(dna_seq1)) * 100
