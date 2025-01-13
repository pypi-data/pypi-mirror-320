import os
import json
import requests
import shutil
from .utils.logger_config import get_logger

logger = get_logger(__name__)


class BuildifyApiParser:
    def __init__(
        self,
        api_key,
        base_url="https://api.getbuildify.com/v1",
        provinces=None,
        page_start=0,
        limit=None,
        output_dir="data/projects",
        clean_output_dir=False,
    ):
        self.base_url = base_url
        self.headers = {
            "accept": "application/json",
            "x-api-key": api_key,
        }
        self.provinces = provinces or ["on", "bc"]
        self.page_start = page_start
        self.limit = limit
        self.output_dir = os.path.abspath(output_dir)

        if clean_output_dir:
            self._prepare_output_directory()

    def _prepare_output_directory(self):
        """Prepare the output directory by clearing existing content and recreating it."""
        if os.path.exists(self.output_dir):
            dir_name = os.path.basename(self.output_dir)
            logger.info(f"Clearing existing content in the output directory: {dir_name}")
            shutil.rmtree(self.output_dir)  # Remove all content in the directory
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory is ready: {self.output_dir}")

    def _fetch_listings(self, province, page=0):
        """Fetch listings for a specific province and page."""
        
        # Define the parameters to include in the request
        params = ["builders", "salesCompanies", "salesCentres", "marketingCompanies", "interiorDesigners", "architects"]
        url = f"{self.base_url}/{province}/search_listings/?referrences={','.join(params)}"
        params = {"page": page}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            logger.info(f"Fetched page {page} for province {province}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data for province {province}, page {page}: {e}")
            return None

    def _save_listing_data(self, listing_id, listing_data):
        """Save a single listing's data into its own directory."""
        listing_dir = os.path.join(self.output_dir, listing_id)
        os.makedirs(listing_dir, exist_ok=True)  # Create the directory if it doesn't exist
        listing_file_path = os.path.join(listing_dir, "data.json")

        if not os.path.exists(listing_file_path):
            with open(listing_file_path, "w", encoding="utf-8") as json_file:
                json.dump(listing_data, json_file, indent=4)
            logger.info(f"Saved listing {listing_id}")
        else:
            logger.info(f"Listing {listing_id} already exists. Skipping.")

    def sync_projects_and_floorplans(self, process_project_callback):
        """Synchronize projects and floorplans across all specified provinces."""
        logger.info("Starting synchronization process.")

        total_projects_processed = 0  # Initialize total count globally
        collected_types = set()
        collected_statuses = set()
        collected_floorplan_statuses = set()

        for province in self.provinces:
            logger.info(f"Processing province: {province.upper()}")

            page = self.page_start

            while True:
                # Check if the global limit has been reached
                if self.limit and total_projects_processed >= self.limit:
                    logger.info(f"Global limit of {self.limit} projects reached. Stopping.")
                    return

                # Fetch listings for the current page
                data = self._fetch_listings(province, page=page)

                if not data or not data.get("results"):
                    logger.info(f"No more results for province {province} on page {page}")
                    break

                listings = data["results"]

                # Process each project in the listings
                for project_data in listings:
                    object_id = project_data.get("objectID")
                    selling_status = project_data.get("sellingStatus")
                    types = project_data.get("type", [])

                    # Collect some data for logging
                    collected_types.update(types)
                    collected_statuses.add(selling_status)

                    logger.info(f"Processing project #{object_id} in province {province}")

                    if selling_status.lower() != "selling now":
                        logger.info(f"Skipping project #{object_id} with status: {selling_status}")
                        continue

                    # Skip projects with certain types
                    excluding_types = ["townhouse", "single family home", "townhomes"]
                    allowed_types = ["condo"]

                    if not any(type.lower() in allowed_types for type in types) and any(type.lower() in excluding_types for type in types):
                        logger.info(f"Skipping project #{object_id} with types: {types}")
                        continue

                    # Skip if all floor plan statuses are "sold out" or "sold"
                    floor_plan_statuses = [fp.get("status") for fp in project_data.get("floorPlans", [])]
                    floor_excluding_statuses = ["sold out", "sold"]

                    # Collect some data for logging
                    collected_floorplan_statuses.update(floor_plan_statuses)

                    if all(status and status.lower() in floor_excluding_statuses for status in floor_plan_statuses):
                        logger.info(f"Skipping project #{object_id} due to all floorPlans being sold out or sold")
                        continue

                    # Skip if no date information
                    if not project_data.get("firstOccupancyDate") or not project_data.get("estimatedCompletionDate"):
                        logger.info(f"Skipping project #{object_id} with no date information")
                        continue

                    # Save the project data immediately
                    self._save_listing_data(object_id, project_data)

                    # Optional callback for additional processing
                    logger.info(f"Processing project: {project_data.get('name', 'Unnamed Project')}")
                    process_project_callback(project_data)
                    total_projects_processed += 1

                # Check if we reached the last page for this province
                if page >= data.get("pages", 0) - 1:
                    logger.info(f"Reached the last page for province {province}")
                    break

                # Increment to the next page
                page += 1

        logger.info("Synchronization process completed!")
        logger.info(f"Collected types: {collected_types}")
        logger.info(f"Collected statuses: {collected_statuses}")
        logger.info(f"Collected floorplan statuses: {collected_floorplan_statuses}")
        logger.info(f"Total projects processed: {total_projects_processed}")

    def parse(self, process_project_callback):
        """Main method to parse and process the data."""
        self.sync_projects_and_floorplans(process_project_callback)
