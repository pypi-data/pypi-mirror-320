import json
from codexgen import CodexGen
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

class TestCodexCore:
    def __init__(self):
        self.codexgen = None
        self.total_steps = 7

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
        # Initialize CodexGen with optional encryption key
        try:
            encryption_key = Fernet.generate_key().decode('utf-8')
            self.codexgen = CodexGen(encryption_key=encryption_key)
            self.check_and_log('Initialization', 'Success', 'Encryption key generated and CodexGen initialized.', 1)
        except Exception as e:
            self.check_and_log('Initialization', 'Failure', str(e), 1)

        # Example 1: Convert data to DNA sequence
        try:
            data = {"name": "John Doe", "age": 30, "is_student": False}
            print("Original data:", data)
            dna_sequence = self.codexgen.to_dna(data)
            print("Converted DNA sequence:", dna_sequence)
            self.check_and_log('Data to DNA conversion', 'Success', '', 2)
        except Exception as e:
            self.check_and_log('Data to DNA conversion', 'Failure', str(e), 2)

        # Example 2: Convert DNA sequence back to original data
        try:
            original_data = self.codexgen.to_binary(dna_sequence)
            print("Converted back to original data:", original_data)
            self.check_and_log('DNA to Data conversion', 'Success', '', 3)
        except Exception as e:
            self.check_and_log('DNA to Data conversion', 'Failure', str(e), 3)

        # Example 3: Encrypt and decrypt a DNA sequence
        try:
            encrypted_dna = self.codexgen.encrypt(dna_sequence)
            print("Encrypted DNA sequence:", encrypted_dna)

            decrypted_dna = self.codexgen.decrypt(encrypted_dna)
            print("Decrypted DNA sequence:", decrypted_dna)
            self.check_and_log('Encryption and Decryption', 'Success', '', 4)
        except Exception as e:
            self.check_and_log('Encryption and Decryption', 'Failure', str(e), 4)

        # Example 4: Load a file and convert its content to DNA
        try:
            file_content = self.codexgen.load_file("example.txt")  # Ensure you have a file named 'example.txt'
            print("File content:", file_content)

            dna_from_file = self.codexgen.to_dna(file_content)
            print("DNA sequence from file:", dna_from_file)
            self.check_and_log('File loading and DNA conversion', 'Success', '', 5)
        except Exception as e:
            self.check_and_log('File loading and DNA conversion', 'Failure', str(e), 5)

        # Example 5: Save DNA sequence to file
        try:
            self.codexgen.save_file(dna_sequence, "output_dna.txt")
            print("DNA sequence saved to output_dna.txt")
            self.check_and_log('Saving DNA to file', 'Success', '', 6)
        except Exception as e:
            self.check_and_log('Saving DNA to file', 'Failure', str(e), 6)

        # Example 6: Validate file
        try:
            self.codexgen.validate_file("output_dna.txt")
            print("File is valid.")
            self.check_and_log('File validation', 'Success', '', 7)
        except FileNotFoundError as e:
            self.check_and_log('File validation', 'Failure', f"Error: {e}", 7)
        except Exception as e:
            self.check_and_log('File validation', 'Failure', str(e), 7)


