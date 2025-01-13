import os
import json
from datetime import datetime
import traceback
from ..utils.logger_config import get_logger
from .generator.project import ProjectDepositsGenerator
from .generator.suites import SuiteDepositsGenerator

logger = get_logger(__name__)


class DepositsFinal:
    def __init__(self, output_directory):
        self.output_directory = os.path.abspath(output_directory)
        logger.info(f"Initialized DepositsProjectProcessor for directory: {self.output_directory}")

    def process(self):
        """Process all <objectId> folders in the base directory."""
        for folder_name in os.listdir(self.output_directory):
            folder_path = os.path.join(self.output_directory, folder_name)

            if os.path.isdir(folder_path):
                parsed_date_path = os.path.join(folder_path, "parsed_date.json")
                deposits_path = os.path.join(folder_path, "deposits.json")

                try:
                    self.process_object_folder(folder_path, parsed_date_path, deposits_path)
                except Exception as e:
                    logger.error(f"Failed to process folder {folder_name}: {e}")

    def process_object_folder(self, folder_path, parsed_date_path, deposits_path):
        """Process a single <objectId> folder."""

        dir_name = os.path.basename(folder_path)
        logger.info(f"Processing folder: {dir_name}")

        # Load data.json
        data_path = os.path.join(folder_path, "data.json")
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                project_data = json.load(f)

        # Load parsed_date.json
        parsed_date = None
        if os.path.exists(parsed_date_path):
            with open(parsed_date_path, "r", encoding="utf-8") as f:
                parsed_date_data = json.load(f)
                parsed_date = parsed_date_data.get("parsedDate")

        # Load deposits.json
        deposits_data = {}
        if os.path.exists(deposits_path):
            with open(deposits_path, "r", encoding="utf-8") as f:
                deposits_data = json.load(f)

        processed_data = deposits_data.get("processed", {})
        with_offer = processed_data.get("with_offer", {})
        deposits = processed_data.get("deposits", [])

        if not deposits:
            logger.error(f"No deposits found in {dir_name}")
            return

        # Extract deposits from floorPlans with `startPrice` and `id`
        floor_plans = project_data.get("floorPlans", [])

        # Default dates
        occupancy_date = (
            datetime.strptime(parsed_date, "%Y-%m-%dT%H:%M:%S").date()
            if parsed_date
            else datetime.now().date()
        )

        # Initialize output data structures
        deposits_project = {
            "original_deposits": deposits,
            "generated_deposits": {
                "with_offer": with_offer,
                "deposits": []
            },
            "occupancy_date": parsed_date or None,
            "current_date": datetime.now().isoformat(),
        }

        # Initialize output data structures
        deposits_suites = {
            "original_deposits": deposits,
            "generated_suites": {
                "with_offer": with_offer,
                "deposits": []
            },
            "occupancy_date": parsed_date or None,
            "current_date": datetime.now().isoformat(),
        }

        # Process project deposits
        try:
            if deposits:
                project_generator = ProjectDepositsGenerator(occupancy_date, datetime.now().date())
                generated_deposits = project_generator.generate_deposits(deposits)
                for gen_deposit in generated_deposits:
                    original_amount = self.get_original_amount(gen_deposit, deposits)
                    gen_deposit["amount"] = original_amount
                deposits_project["generated_deposits"]["deposits"] = generated_deposits

                # Process suite deposits
                try:

                    suites_list = []
                    for plan in floor_plans:
                        plan_id = plan.get("id")
                        start_price = plan.get("startPrice")

                        # If startPrice == 0, skip
                        if start_price == 0:
                            continue

                        # Check if "status" != "Sold Out"
                        item_status = plan.get("status")
                        if item_status != "Available":
                            logger.info(f"Skipping suite {plan_id} with status: {item_status}")
                            continue

                        item = {
                            "floorPlanId": plan_id,
                            "price": start_price,
                            "deposits": []
                        }

                        if start_price is not None:
                            for deposit in deposits:

                                # copy
                                deposit = deposit.copy()

                                deposit_variant = deposit.get("variant")
                                price = deposit.get("amount", 1)
                                if deposit_variant == 'percentage':
                                    price = (price / 100) * start_price

                                # rename amount to price
                                deposit.pop('amount', None)
                                deposit['price'] = price

                                item["deposits"].append(deposit)

                        suites_list.append(item)

                    for suite in suites_list:
                        suite_deposits = suite.get("deposits")
                        suite_generator = SuiteDepositsGenerator(occupancy_date, datetime.now().date())
                        generated_data = suite_generator.generate_deposits(suite_deposits)
                        suite_data = {
                            "floorPlanId": suite.get("floorPlanId"),
                            "price": suite.get("price"),
                            "deposits": generated_data
                        }

                        deposits_suites["generated_suites"]["deposits"].append(suite_data)
                        
                except Exception as e:
                    error_message = f"Error generating deposits_suites.json: {str(e)}"
                    logger.error(error_message)
                    logger.error(traceback.format_exc())
                    deposits_suites["error"] = error_message

        except Exception as e:
            error_message = f"Error generating deposits_project.json: {str(e)}"
            logger.error(error_message)
            deposits_project["error"] = error_message

        # Save deposits_project.json
        project_output_path = os.path.join(folder_path, "deposits_project.json")
        with open(project_output_path, "w", encoding="utf-8") as f:
            json.dump(deposits_project, f, indent=4)
        logger.info(f"Generated deposits_project.json for {dir_name}")

        # Save deposits_suites.json
        suites_output_path = os.path.join(folder_path, "deposits_suites.json")
        with open(suites_output_path, "w", encoding="utf-8") as f:
            json.dump(deposits_suites, f, indent=4)
        logger.info(f"Generated deposits_suites.json for {dir_name}")

    @staticmethod
    def get_original_amount(generated_item, original_items):
        """Match and return the original amount for the generated item."""
        for original_item in original_items:
            if original_item.get("variant") == generated_item.get("variant"):
                return original_item.get("amount", 0)
        # Default amount if no match found
        return None


if __name__ == "__main__":
    output_directory = "path/to/output_directory"  # Replace with the actual path
    processor = DepositsFinal(output_directory)
    processor.process()
