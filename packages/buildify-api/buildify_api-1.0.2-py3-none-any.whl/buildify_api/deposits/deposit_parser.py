import os
import json
from .deposit_processor import DepositProcessor  # Assuming DepositProcessor is in the same module
from ..utils.logger_config import get_logger

logger = get_logger(__name__)


class DepositParser:
    def __init__(self, output_directory):
        self.output_directory = os.path.abspath(output_directory)
        self.deposit_processor = DepositProcessor()
        logger.info(f"Initialized DepositDataProcessor for directory: {self.output_directory}")

    def process_all_object_folders(self):
        """Process all <objectId> folders in the base directory."""
        for folder_name in os.listdir(self.output_directory):
            folder_path = os.path.join(self.output_directory, folder_name)

            if os.path.isdir(folder_path):
                data_file_path = os.path.join(folder_path, "data.json")

                if os.path.exists(data_file_path):
                    try:
                        self.process_object_folder(folder_path, data_file_path)
                    except Exception as e:
                        logger.error(f"Failed to process folder {folder_name}: {e}")
                        self.save_error(folder_path, f"Processing failed: {e}")
                else:
                    logger.warning(f"No data.json found in folder: {folder_path}")
                    self.save_error(folder_path, "data.json file is missing.")

    def process_object_folder(self, folder_path, data_file_path):
        """Process a single <objectId> folder."""

        dir_name = os.path.basename(folder_path)
        logger.info(f"Processing folder: {dir_name}")

        # Load the data.json file
        with open(data_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract paymentStructures and milestones
        payment_structures = data.get("paymentStructures", [])
        if not payment_structures:
            logger.warning(f"No paymentStructures found in {dir_name}")
            self.save_error(folder_path, "No paymentStructures found in data.json")
            return

        milestones = payment_structures[0].get("milestones", [])
        if not milestones:
            logger.warning(f"No milestones found in the first paymentStructure of {dir_name}")
            self.save_error(folder_path, "No milestones found in the first paymentStructure")
            return

        # Process the milestones using DepositProcessor
        try:
            processed_data = self.deposit_processor.process_milestones(milestones)
        except Exception as e:
            logger.error(f"Error processing milestones in {dir_name}")
            self.save_error(folder_path, f"Error processing milestones: {e}", milestones=milestones)
            return

        # Save the processed data to deposits.json
        self.save_deposits(folder_path, processed_data, milestones)

    def save_deposits(self, folder_path, processed_data, milestones):
        """Save deposits.json with processed data and original milestones."""
        deposits_file_path = os.path.join(folder_path, "deposits.json")
        deposits_content = {
            "original_milestones": milestones,
            "processed": processed_data,
        }
        with open(deposits_file_path, "w", encoding="utf-8") as f:
            json.dump(deposits_content, f, indent=4)

        dir_name = os.path.basename(folder_path)
        logger.info(f"Saved deposits.json for {dir_name}")

    def save_error(self, folder_path, error_message, milestones=None):
        """Save deposits.json with an error message and original milestones if available."""
        deposits_file_path = os.path.join(folder_path, "deposits.json")
        deposits_content = {
            "error": error_message,
            "original_milestones": milestones if milestones else [],
        }
        with open(deposits_file_path, "w", encoding="utf-8") as f:
            json.dump(deposits_content, f, indent=4)

        dir_name = os.path.basename(folder_path)
        logger.info(f"Saved deposits.json with error for {dir_name}")


if __name__ == "__main__":
    output_directory = "path/to/output_directory"  # Replace with the actual path
    processor = DepositParser(output_directory)
    processor.process_all_object_folders()
