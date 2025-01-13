import os
import re
from pathlib import Path


class LogErrorExtractor:
    def __init__(self, search_text):
        """
        Initialize the LogErrorExtractor.

        :param search_text: Text to search for in log files.
        """
        self.log_dir = os.path.join(Path(__file__).resolve().parent.parent.parent.parent, 'logs')
        os.makedirs(self.log_dir, exist_ok=True)  # Ensure the directory exists
        self.search_text = re.escape(search_text)  # Escape special characters for regex

    def extract_errors_from_file(self, log_file_path):
        """
        Extract errors containing the specified search text from a single log file.

        :param log_file_path: Path to the log file.
        :return: List of extracted values after the search text.
        """
        errors = []
        try:
            with open(log_file_path, 'r', encoding='utf-8') as log_file:
                log_content = log_file.read()
                # Regular expression to match the search text and extract content after it
                pattern = rf"{self.search_text}: (.+)"
                matches = re.findall(pattern, log_content)
                errors.extend(matches)
        except Exception as e:
            print(f"Error reading file {log_file_path}: {e}")
        return errors

    def find_files_and_extract_errors(self):
        """
        Recursively search for files and extract errors containing the search text.

        :return: Dictionary with file paths as keys and list of extracted values as values.
        """
        all_errors = {}
        for root, _, files in os.walk(self.log_dir):
            for file in files:
                # Check all files (not limited by file mask)
                log_file_path = os.path.join(root, file)
                errors = self.extract_errors_from_file(log_file_path)
                if errors:
                    all_errors[log_file_path] = errors
        return all_errors

    def run(self):
        """
        Execute the log file search and error extraction process.

        :return: Dictionary with extracted values found.
        """
        print(f"Searching for '{self.search_text}' in files under directory: {self.log_dir}")
        errors = self.find_files_and_extract_errors()
        return errors


# Example Usage
if __name__ == "__main__":
    search_text = "Invalid deposit structure"  # The text to search for in the logs

    # Initialize and run the extractor
    extractor = LogErrorExtractor(search_text)
    errors_in_logs = extractor.run()

    # Print all errors found
    for log_file, errors in errors_in_logs.items():
        print(f"Errors in {log_file}:")
        for error in errors:
            print(f"  - {error}")
