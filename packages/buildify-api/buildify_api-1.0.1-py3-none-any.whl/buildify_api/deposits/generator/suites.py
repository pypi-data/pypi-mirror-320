from datetime import datetime, timedelta, date
import json
from ...utils.logger_config import get_logger

logger = get_logger(__name__)


class SuiteDepositsGenerator:
    def __init__(self, occupancy_date: date, current_date: date = None):
        if not occupancy_date:
            logger.error("Occupancy date is required.")
            raise ValueError("Occupancy date is required.")
        self.occupancy_date = occupancy_date
        self.current_date = current_date or datetime.now().date()
        logger.info(f"Initialized SuiteDepositsGenerator with occupancy_date: {self.occupancy_date} and current_date: {self.current_date}")

    @staticmethod
    def convert_date_to_days(target_date: str, current_date: date) -> int:
        """Convert a date string to days relative to the current date."""
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        return (target_date - current_date).days

    def process_deposits(self, deposits_list: list):
        """Process the suite deposit list to structure and order deposits."""
        if not deposits_list:
            logger.warning("Empty deposits list provided.")
            return []

        processed_deposits = []

        for deposit in deposits_list:
            variant = deposit.get("variant", None)
            price = deposit.get("price", 0)
            d_days = deposit.get("days", None)
            d_date = deposit.get("date")

            # If no timing information, skip
            if (d_days is None or d_days == 0) and not d_date:
                logger.warning(f"Skipping deposit with no timing information: {deposit}")
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
                "price": price,
                "days": d_days,
                "date": deposit_date.isoformat()
            })

        # Sort deposits by days ascending
        processed_deposits.sort(key=lambda x: x["days"])

        # Handle occupancy deposit
        occupancy_deposit = {
            "variant": None,
            "last": True,
            "price": 0,
            "days": 9999,
            "date": self.occupancy_date.isoformat(),
        }

        # Merge deposits occurring after occupancy date
        valid_deposits = []
        for deposit in processed_deposits:
            if deposit["days"] > (self.occupancy_date - self.current_date).days:
                logger.info(f"Merging deposit into occupancy: {deposit}")
                # occupancy_deposit["percent"] += deposit["percent"]
                # occupancy_deposit["fixed"] += deposit["fixed"]
                occupancy_deposit["price"] += deposit["price"]
            else:
                valid_deposits.append(deposit)

        valid_deposits.append(occupancy_deposit)
        return valid_deposits

    def generate_deposits(self, deposits_list: list):
        """Main function to generate suite deposits."""
        if not deposits_list:
            logger.warning("No deposits provided for generation.")
            return []

        try:
            return self.process_deposits(deposits_list)
        except Exception as e:
            logger.error(f"Failed to process suite deposits: {e}")
            raise ValueError(f"Failed to process suite deposits: {e}")

    @staticmethod
    def test_method():
        """Run predefined tests for suite deposit generator."""
        def custom_json_encoder(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        current_date = date(2024, 1, 1)
        occupancy_date = current_date + timedelta(days=300)

        test_cases = [
            {
                "name": "Test 1: Basic scenario",
                "deposits": [
                    {"days": 30, "percent": 5, "price": 0},
                    {"date": "2025-01-01", "percent": 5, "price": 0},
                    {"days": 360, "percent": 15, "price": 0},
                    {"days": 9999, "percent": 10, "price": 0},
                ],
            },
            {
                "name": "Test 2: No occupancy deposits",
                "deposits": [
                    {"days": 10, "percent": 2, "price": 0},
                    {"days": 20, "percent": 3, "price": 0},
                    {"days": 60, "percent": 5, "price": 0},
                ],
            },
            {
                "name": "Test 3: Multiple occupancy deposits",
                "deposits": [
                    {"days": 9999, "percent": 10, "price": 0},
                    {"days": 9999, "percent": 5, "price": 0},
                    {"days": 300, "percent": 5, "price": 0},
                ],
            },
            {
                "name": "Test 4: Date-based deposit",
                "deposits": [
                    {"date": (current_date + timedelta(days=100)).isoformat(), "percent": 10, "price": 1000},
                ],
            },
        ]

        for case in test_cases:
            logger.info(f"Running {case['name']}")
            generator = SuiteDepositsGenerator(occupancy_date, current_date)
            response = generator.generate_deposits(case["deposits"])
            print(case["name"])
            print("Input:", json.dumps(case["deposits"], indent=4, default=custom_json_encoder))
            print("Response:", json.dumps(response, indent=4, default=custom_json_encoder))
            print("========================================")


if __name__ == "__main__":
    SuiteDepositsGenerator.test_method()
