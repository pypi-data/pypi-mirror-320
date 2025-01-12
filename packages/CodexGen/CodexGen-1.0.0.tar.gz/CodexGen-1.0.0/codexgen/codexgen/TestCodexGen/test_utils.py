import json
from codexgen import CodexUtils
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

class TestCodexUtils:
    def __init__(self):
        self.codexutils = None
        self.total_steps = 5

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
        # Initialize CodexUtils 
        try:
            self.codexutils = CodexUtils()
            self.check_and_log('Initialization', 'Success', 'CodexUtils initialized.', 1)
        except Exception as e:
            self.check_and_log('Initialization', 'Failure', str(e), 1)

        # Example 1: Checksum
        try:
            dna_sequence = "ATGCGT"
            checksum_result = self.codexutils.checksum(dna_sequence)
            self.check_and_log('Checksum', 'Success', f"Checksum: {checksum_result}", 2)
        except Exception as e:
            self.check_and_log('Checksum', 'Failure', str(e), 2)

        # Example 2: Validate DNA sequence
        try:
            dna_sequence = "ATGCGT"
            is_valid = self.codexutils.validate_dna_sequence(dna_sequence)
            self.check_and_log('Validate DNA', 'Success', f"Is valid DNA: {is_valid}", 3)
        except Exception as e:
            self.check_and_log('Validate DNA', 'Failure', str(e), 3)

        # Example 3: Encryption Key
        try:
            key = self.codexutils.generate_key(output_path="key.key")
            self.check_and_log('Encryption Key', 'Success', f"Encryption key: {key}", 4)
        except Exception as e:
            self.check_and_log('Encryption Key', 'Failure', str(e), 4)

        # Example 4: Load encryption key
        try:
            key = self.codexutils.load_key(file_path="key.key")
            self.check_and_log('Load Key', 'Success', f"Loaded key: {key}", 5)
        except Exception as e:
            self.check_and_log('Load Key', 'Failure', str(e), 5)

