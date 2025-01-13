import os
import json
import re
from datetime import datetime
from .utils.logger_config import get_logger

logger = get_logger(__name__)


class OccupancyDateParser:
    def __init__(self, output_directory):
        self.output_directory = os.path.abspath(output_directory)
        logger.info(f"Initialized DepositsOccupancyParser for directory: {self.output_directory}")

    @staticmethod
    def parse_date(date_str):
        """Parse a date string into a datetime object."""
        if not date_str:
            return None

        date_str = date_str.lower().strip()

        # Default current year if no year is provided
        if not re.search(r'\d{4}', date_str):
            date_str = f"{date_str} {datetime.now().year}"

        # Handle seasonal or approximate date formats
        month_map = {
            "early": 1, "mid": 6, "late": 12, "spring": 3, "summer": 6,
            "fall": 9, "autumn": 9, "winter": 12, "q1": 3, "q2": 6, "q3": 9, "q4": 12,
            "determined": 12, "end": 12
        }

        month = None
        year = None

        for key, value in month_map.items():
            if key in date_str:
                month = value
                break

        if not month:
            try:
                # Extract month and convert to numerical value
                month_name = date_str.split()[0]
                month = datetime.strptime(month_name[:3], "%b").month
            except ValueError:
                pass

        try:
            year = int(re.search(r'(\d{4})', date_str).group(1))
        except AttributeError:
            logger.warning(f"Year not found in date string: {date_str}")
            return None

        if not month:
            month = 1

        try:
            return datetime(year, month, 1)
        except ValueError as e:
            logger.warning(f"Invalid date construction for {date_str}: {e}")
            return None

    def parse(self):
        """Process all <objectId> folders in the base directory."""
        problematic_dates = {}

        for folder_name in os.listdir(self.output_directory):
            folder_path = os.path.join(self.output_directory, folder_name)

            if os.path.isdir(folder_path):
                data_file_path = os.path.join(folder_path, "data.json")

                if os.path.exists(data_file_path):
                    try:
                        self.process_object_folder(folder_path, data_file_path, problematic_dates)
                    except Exception as e:
                        logger.error(f"Failed to process folder {folder_name}: {e}")
                else:
                    logger.warning(f"No data.json found in folder: {folder_path}")

        if problematic_dates:
            logger.info("Problematic dates encountered:")
            for obj_id, date_str in problematic_dates.items():
                logger.info(f"ObjectId: {obj_id}, Invalid Date: {date_str}")

    def process_object_folder(self, folder_path, data_file_path, problematic_dates):
        """Process a single <objectId> folder."""
        dir_name = os.path.basename(folder_path)
        logger.info(f"Processing folder: {dir_name}")

        try:
            with open(data_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read JSON file {data_file_path}: {e}")
            return

        first_occupancy_date = data.get("firstOccupancyDate")
        estimated_completion_date = data.get("estimatedCompletionDate")

        occupancy_date_str = first_occupancy_date or estimated_completion_date
        parsed_date = self.parse_date(occupancy_date_str)

        if not occupancy_date_str:
            logger.warning(f"No Occupancy Date found in {dir_name}")

        # Save the original and parsed dates
        output_path = os.path.join(folder_path, "parsed_date.json")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({
                    "firstOccupancyDate": first_occupancy_date,
                    "estimatedCompletionDate": estimated_completion_date,
                    "parsedDate": parsed_date.isoformat() if parsed_date else None
                }, f, indent=4)

            dir_name = os.path.basename(folder_path)
            logger.info(f"Saved parsed data to {dir_name}")
        except Exception as e:
            logger.error(f"Failed to write parsed data to {output_path}: {e}")

        if not parsed_date and occupancy_date_str:
            obj_id = os.path.basename(folder_path)
            problematic_dates[obj_id] = occupancy_date_str


if __name__ == "__main__":
    output_directory = "path/to/output_directory"  # Replace with the actual path
    parser = OccupancyDateParser(output_directory)
    parser.parse()
