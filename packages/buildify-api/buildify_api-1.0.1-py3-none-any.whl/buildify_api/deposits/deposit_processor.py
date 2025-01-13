import json
import re
import dateparser
from ..utils.logger_config import get_logger

logger = get_logger(__name__)


class DepositProcessor:
    def __init__(self):
        self.word_to_num_map = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
            "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20
        }

    def preprocess_text(self, text):
        """Preprocess text: remove extra spaces and unnecessary punctuation, keeping important separators like commas."""
        if isinstance(text, str):
            text = text.strip()
            text = re.sub(r'[^\w\s,]', '', text)  # Keep commas, but remove other punctuation
            return text.lower()
        return ''

    def convert_word_to_number_simple(self, word):
        """Simple conversion of word numbers to numerical format."""
        return self.word_to_num_map.get(word.lower(), None)

    def convert_to_days(self, text):
        """Convert time descriptions into days, including numbers written in words."""
        days = 0
        text = self.preprocess_text(text)

        if "occupancy" in text or "closing" in text:
            logger.info(f"Text '{text}' detected as occupancy or closing.")
            return 9999

        relative_match = re.search(r'at (\d+) days? after signing', text)
        if relative_match:
            return int(relative_match.group(1))

        acceptance_match = re.search(r'on or before the (\d+|\w+)\s+days? after the acceptance date', text)
        if acceptance_match:
            number = acceptance_match.group(1)
            number = re.sub(r'(st|nd|rd|th)$', '', number)
            if number.isdigit():
                return int(number)
            return self.convert_word_to_number_simple(number)

        word_number = re.search(r'(\w+)\s+(days?|weeks?|months?|years?)', text)
        if word_number:
            number = self.convert_word_to_number_simple(word_number.group(1))
            if number:
                if 'day' in word_number.group(2):
                    days += number
                elif 'week' in word_number.group(2):
                    days += number * 7
                elif 'month' in word_number.group(2):
                    days += number * 30
                elif 'year' in word_number.group(2):
                    days += number * 365

        match = re.search(r'(\d+)\s*days?', text)
        if match:
            days += int(match.group(1))

        if days > 0:
            return days

        match = re.search(r'(\d+)\s*weeks?', text)
        if match:
            days += int(match.group(1)) * 7

        match = re.search(r'(\d+)\s*months?', text)
        if match:
            days += int(match.group(1)) * 30

        match = re.search(r'(\d+)\s*years?', text)
        if match:
            days += int(match.group(1)) * 365

        return days

    def is_with_offer(self, text):
        """Check if the deposit is the initial deposit with the signing or offer."""
        keywords = [
            "deposit structure", "with agreement of purchase and sale", "on signing",
            "deposit upon signing agreement", "with agreement", "at signing", "writing",
            "due to signing", "upon writing", "on signing", "at purchase", "with purchase",
            "upon acceptance", "due on signing", "immediate", "first deposit", "initial deposit",
            "on execution", "with the offer", "upon offer", "due upon presentation", "bank draft",
            "upon execution", "aps", "with offer", "w/ agreement", "with signing",
            "with the agreement", "contract signing", "upon contract writing",
            "writing the contract", "time of signing", "now", "at the time of offer",
            "own with", "upon reccession period"
        ]
        text_lower = self.preprocess_text(text)
        for keyword in keywords:
            if keyword in text_lower:
                logger.debug(f"Keyword match found in text '{text}': {keyword}")
                return True
        return False

    def extract_and_parse_dates(self, text):
        """Extract and parse human-readable dates using dateparser."""
        text_lower = text.lower()
        if re.search(r'\bin\s+\d+\s+(days?|weeks?|months?|years?)\b', text_lower):
            return None

        date_pattern = r'\b(?:on\s+|due\s+on\s+|in\s+)?(?:' \
                       r'\d{1,2}(?:\s*(?:st|nd|rd|th))?[\s,]*\w+[\s,]*\d{4}|' \
                       r'\w+[\s,]*\d{1,2}(?:\s*(?:st|nd|rd|th))?,?[\s,]*\d{4}|' \
                       r'\w+\s+\d{4})\b'

        match = re.search(date_pattern, text_lower)
        if match:
            cleaned_text = re.sub(r'\b(on|due on|in)\b', '', match.group(0)).strip()
            parsed_date = dateparser.parse(cleaned_text, settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'MDY'})
            if parsed_date:
                return parsed_date
        return None

    def process_milestones(self, milestones):
        """Process a list of deposits (milestones) and return them in the specified format."""
        result = {"with_offer": {}, "deposits": []}
        offer_found = False

        for milestone in milestones:
            text = self.preprocess_text(milestone['text'])
            suffix = self.preprocess_text(milestone.get('suffix', ''))
            prefix = self.preprocess_text(milestone.get('prefix', ''))

            with_offer = False
            if not offer_found and (self.is_with_offer(suffix) or self.is_with_offer(prefix)):
                with_offer = True
                offer_found = True

            days = self.convert_to_days(text) or self.convert_to_days(suffix) or self.convert_to_days(prefix)
            if any(occ in suffix or occ in prefix for occ in ['occupancy', 'closing']):
                days = 9999

            parsed_dates = self.extract_and_parse_dates(suffix) or self.extract_and_parse_dates(prefix)
            if not with_offer and days == 0 and not parsed_dates:
                logger.error(f"Invalid deposit structure: '{text}' has zero days and no valid date.")
                raise ValueError(f"Invalid deposit structure: '{text}'")

            deposit_data = {
                "days": days,
                "amount": milestone.get("amount"),
                "variant": milestone.get("type"),
            }
            if parsed_dates:
                deposit_data["date"] = parsed_dates.strftime('%Y-%m-%d')

            if with_offer:
                result["with_offer"] = deposit_data
            else:
                result["deposits"].append(deposit_data)

        return result

    def process_json_deposit_structure(self, deposit_json):
        """Main function to process the deposit JSON structure."""
        if "milestones" in deposit_json:
            return self.process_milestones(deposit_json["milestones"])
        else:
            logger.error("Invalid JSON structure: 'milestones' key is missing.")
            raise ValueError("Invalid JSON structure: 'milestones' key is missing.")

    def test_processing(self):
        """Test deposit processing with predefined JSON examples."""
        logger.info("Starting test cases...")

        test_data = [
            {
                "milestones": [
                    {"amount": 5000, "prefix": "", "suffix": " with Offer", "text": "$5000  with Offer", "type": "fixed"},
                    {"amount": 5, "prefix": "", "suffix": " in 30 Days", "text": "5%  in 30 Days", "type": "percentage"},
                    {"amount": 5, "prefix": "", "suffix": "on January 8, 2026", "text": "5% on January 8, 2026", "type": "percentage"},
                    {"amount": 5, "prefix": "", "suffix": "on Apr 1, 2024", "text": "5% on Apr 1, 2024", "type": "percentage"},
                    {"amount": 5, "prefix": "", "suffix": "in 450 Days", "text": "5% in 450 Days", "type": "percentage"}
                ],
                "totalDeposit": 20,
                "type": "Standard"
            },
            {
                "milestones": [
                    {"text": "Initial deposit of $7500", "type": "fixed", "amount": 7500, "prefix": "Initial deposit of", "suffix": ""},
                    {"text": "the balance of 5% in 30 days", "type": "percentage", "amount": 5, "prefix": "the balance of", "suffix": "in 30 days"},
                    {"text": "2.5% in 120 days", "type": "percentage", "amount": 2.5, "prefix": "", "suffix": "in 120 days"},
                    {"text": "2.5% on occupancy", "type": "percentage", "amount": 2.5, "prefix": "", "suffix": "on occupancy"}
                ],
                "totalDeposit": 20
            }
        ]

        for i, data in enumerate(test_data):
            logger.info(f"Running test case {i + 1}")
            try:
                result = self.process_json_deposit_structure(data)
                logger.info(json.dumps(result, indent=4))
            except Exception as e:
                logger.error(f"Error in test case {i + 1}: {e}")


if __name__ == "__main__":
    processor = DepositProcessor()
    processor.test_processing()
