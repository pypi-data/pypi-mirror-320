from datetime import datetime, timedelta, date
import json
from ...utils.logger_config import get_logger

logger = get_logger(__name__)


class ProjectDepositsGenerator:
    def __init__(self, occupancy_date: date, current_date: date = None):
        if not occupancy_date:
            logger.error("Occupancy date is required.")
            raise ValueError("Occupancy date is required.")
        self.occupancy_date = occupancy_date
        self.current_date = current_date or datetime.now().date()
        logger.info(f"Initialized ProjectDepositsGenerator with occupancy_date: {self.occupancy_date}, current_date: {self.current_date}")

    @staticmethod
    def convert_date_to_days(target_date: str, current_date: date) -> int:
        """Convert a date string to days relative to the current date."""
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        return (target_date - current_date).days

    @staticmethod
    def validate_deposit(deposit):
        """Ensure the deposit has valid days or a date."""
        if not deposit.get("days") and not deposit.get("date"):
            logger.warning(f"Invalid deposit found: {deposit}")
            return False
        return True

    def process_deposits(self, deposits_list: list):
        """Process the deposit list to structure and order deposits."""
        if not deposits_list:
            logger.warning("Empty deposits list provided.")
            return []

        processed_deposits = []

        for deposit in deposits_list:
            variant = deposit.get("variant")
            d_days = deposit.get("days", 0)
            d_date = deposit.get("date")

            # If no days and no date, skip
            if not d_days and not d_date:
                logger.warning(f"Skipping deposit due to missing timing: {deposit}")
                continue

            # If days exist, calculate the date
            if d_days:
                deposit_date = self.current_date + timedelta(days=d_days)
            else:
                deposit_date = datetime.strptime(d_date, "%Y-%m-%d").date()

            # Convert date to days if missing days
            if not d_days:
                d_days = self.convert_date_to_days(deposit_date, self.current_date)

            processed_deposits.append({
                "variant": variant,
                "days": d_days,
                "date": deposit_date.isoformat()
            })

        # Sort deposits by days ascending
        processed_deposits.sort(key=lambda x: x["days"])

        # Try to define variant for last deposit (fixed or percentage)
        last_variant = processed_deposits[-1]["variant"]
        if last_variant == "last":
            last_variant = processed_deposits[-2]["variant"]

        # Handle occupancy deposit
        occupancy_deposit = {
            "variant": last_variant,
            "last": True,
            "days": 9999,
            "date": self.occupancy_date.isoformat(),
        }

        # Filter deposits occurring before occupancy
        valid_deposits = [dep for dep in processed_deposits if dep["days"] <= (self.occupancy_date - self.current_date).days]

        # Add the last deposit for occupancy
        valid_deposits.append(occupancy_deposit)

        logger.info(f"Processed deposits: {valid_deposits}")
        return valid_deposits

    def generate_deposits(self, deposits_list: list):
        """Main function to process the deposit list."""
        if not deposits_list:
            logger.warning("No deposits provided for generation.")
            return []

        try:
            return self.process_deposits(deposits_list)
        except Exception as e:
            logger.error(f"Failed to process deposits: {e}")
            raise ValueError(f"Failed to process deposits: {e}")

    @staticmethod
    def test_method():
        """Run predefined tests for deposit generator."""
        def custom_json_encoder(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        current_date = date(2024, 1, 1)
        occupancy_date = current_date + timedelta(days=300)

        test_cases = [
            {
                "name": "Test 1: Simple scenario",
                "deposits": [
                    {"days": 30, "variant": "first"},
                    {"days": 60, "variant": "second"},
                    {"days": 360, "variant": "third"},
                    {"days": 900, "variant": "fourth"},
                ],
            },
            {
                "name": "Test 2: Occupancy deposit scenario",
                "deposits": [
                    {"days": 9999, "variant": "occ1"},
                    {"days": 9999, "variant": "occ2"},
                    {"days": 200, "variant": "early"},
                ],
            },
            {
                "name": "Test 3: Date-based deposits",
                "deposits": [
                    {"date": (current_date + timedelta(days=100)).isoformat(), "variant": "date_dep"},
                    {"days": 9999, "variant": "occ_dep"},
                ],
            },
            {
                "name": "Test 4: Mixed scenario",
                "deposits": [
                    {"variant": "deposit_1", "days": 30},
                    {"variant": "deposit_2", "date": (current_date + timedelta(days=120)).isoformat()},
                    {"variant": "deposit_3", "days": 9999},
                ],
            },
        ]

        for case in test_cases:
            logger.info(f"Running {case['name']}")
            generator = ProjectDepositsGenerator(occupancy_date, current_date)
            print(case["name"])
            response = generator.generate_deposits(case["deposits"])
            print("Input:", json.dumps(case["deposits"], indent=4, default=custom_json_encoder))
            print("Response:", json.dumps(response, indent=4, default=custom_json_encoder))
            print("========================================")


if __name__ == "__main__":
    ProjectDepositsGenerator.test_method()
