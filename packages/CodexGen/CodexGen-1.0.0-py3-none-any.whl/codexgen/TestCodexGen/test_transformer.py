import json
from codexgen import CodexTransformers
from cryptography.fernet import Fernet
from tqdm import tqdm

# ANSI escape codes for colors
class Colors:
    RESET = "\033[0m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"

# Icons
class Icons:
    SUCCESS = "✅"
    FAILURE = "❌"
    WARNING = "⚠️"
    LOADING = "🔃"

class TestCodexTransformer:
    def __init__(self):
        self.codexgen = None
        self.total_steps = 8

    def check_and_log(self, step_name: str, status: str, details: str = '', step_number: int = 1):
        """
        Helper function to log each checkpoint status with colored output, icons, and step progress.
        
        :param step_name: Name of the step
        :param status: Success or Failure status
        :param details: Additional details for the step
        :param step_number: The current step number
        """
        progress = f"Step {step_number}/{self.total_steps}"
        
        if status == 'Success':
            color = Colors.GREEN
            icon = Icons.SUCCESS
        elif status == 'Failure':
            color = Colors.RED
            icon = Icons.FAILURE
        elif status == 'Warning':
            color = Colors.YELLOW
            icon = Icons.WARNING
        else:
            color = Colors.BLUE
            icon = Icons.LOADING

        print(f"{color}[{step_name}] - {icon} {status} {progress}{Colors.RESET}")
        if details:
            print(f"Details: {details}")

    def run_tests(self):
        """
        Run all test steps in sequence
        """
        # Initialize CodexTransformers 
        try:
            codextransformers = CodexTransformers()
            self.check_and_log('Initialization', 'Success', 'codextransformers initialized.', 1)
        except Exception as e:
            self.check_and_log('Initialization', 'Failure', str(e), 1)

        # Example 1: Covert DNA to RNA
        try:
            dna_sequence = 'ATG'
            rna_sequence = codextransformers.dna_to_rna(dna_sequence)
            self.check_and_log('DNA to RNA conversion', 'Success', f'RNA sequence: {rna_sequence}', 2)
        except Exception as e:
            self.check_and_log('DNA to RNA conversion', 'Failure', str(e), 2)

        # Example 2: Covert DNA to Protein
        try:
            dna_sequence = 'ATG'
            protein_sequence = codextransformers.dna_to_protein(dna_sequence)
            self.check_and_log('DNA to Protein conversion', 'Success', f'Protein sequence: {protein_sequence}', 3)
        except Exception as e:
            self.check_and_log('DNA to Protein conversion', 'Failure', str(e), 3)

        # Example 3: Reverse Complement
        try:
            dna_sequence = 'ATG'
            reverse_complement = codextransformers.reverse_complement(dna_sequence)
            self.check_and_log('Reverse Complement', 'Success', f'Reverse complement: {reverse_complement}', 4)
        except Exception as e:
            self.check_and_log('Reverse Complement', 'Failure', str(e), 4)


        # Example 4: RNA to DNA
        try:
            rna_sequence = 'AUG'
            dna_sequence = codextransformers.rna_to_dna(rna_sequence)
            self.check_and_log('RNA to DNA conversion', 'Success', f'DNA sequence: {dna_sequence}', 5)
        except Exception as e:
            self.check_and_log('RNA to DNA conversion', 'Failure', str(e), 5)


        # Example 5: RNA to Protein
        try:
            rna_sequence = 'AUG'
            protein_sequence = codextransformers.rna_to_protein(rna_sequence)
            self.check_and_log('RNA to Protein conversion', 'Success', f'Protein sequence: {protein_sequence}', 6)
        except Exception as e:
            self.check_and_log('RNA to Protein conversion', 'Failure', str(e), 6)


        # Example 6: Protein to DNA
        try:
            protein_sequence = 'M'
            dna_sequence = codextransformers.protein_to_dna(protein_sequence)
            self.check_and_log('Protein to DNA conversion', 'Success', f'DNA sequence: {dna_sequence}', 7)
        except Exception as e:
            self.check_and_log('Protein to DNA conversion', 'Failure', str(e), 7)


        # Example 7: Protein to RNA
        try:
            protein_sequence = 'M'
            rna_sequence = codextransformers.protein_to_rna(protein_sequence)
            self.check_and_log('Protein to RNA conversion', 'Success', f'RNA sequence: {rna_sequence}', 8)
        except Exception as e:
            self.check_and_log('Protein to RNA conversion', 'Failure', str(e), 8)

            
