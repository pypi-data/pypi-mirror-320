import os
import json
import requests
from urllib.parse import urlparse
from slugify import slugify
from .utils.logger_config import get_logger

logger = get_logger(__name__)


class DataDownloader:
    def __init__(self, output_directory, download_files=True):
        self.output_directory = os.path.abspath(output_directory)
        self.download_files = download_files

        logger.info(f"Output directory: {self.output_directory}")
        logger.info(f"Download files: {self.download_files}")

    def process(self):
        """Recursively process all data.json files in the output directory."""
        logger.info(f"Starting processing for directory: {self.output_directory}")
        for root, _, files in os.walk(self.output_directory):
            if "data.json" in files:
                data_file = os.path.join(root, "data.json")
                try:
                    self.process_data_file(data_file)
                except Exception as e:
                    logger.error(f"Failed to process {data_file}: {e}")

    def process_data_file(self, data_file):
        """Process a single data.json file."""

        file_name = os.path.basename(data_file)
        logger.info(f"Processing file: {file_name}")
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        listing_id = data.get("objectID")

        logger.info(f"Processing project {listing_id}.")
        listing_dir = os.path.dirname(data_file)
        files_dir = os.path.join(listing_dir, "files")
        os.makedirs(files_dir, exist_ok=True)

        # Map file information
        file_map = {"id": listing_id, "floorPlans": [], "photos": [], "cover": None, "logo": None}

        # Process and map specific files
        file_map["cover"] = self.process_file(data.get("coverPhoto"), files_dir, "cover", listing_id)
        file_map["logo"] = self.process_file(data.get("logo"), files_dir, "logo", listing_id)
        file_map["photos"] = self.process_photos(data.get("photos", []), files_dir, listing_id)
        file_map["floorPlans"] = self.process_floorplans(data.get("floorPlans", []), files_dir, listing_id)

        # Save map.json (overwrite if exists)
        map_file_path = os.path.join(listing_dir, "map.json")
        with open(map_file_path, "w", encoding="utf-8") as map_file:
            json.dump(file_map, map_file, indent=4)
        logger.info(f"Saved map.json for project {listing_id}")

    def process_file(self, item, files_dir, file_name, listing_id):
        """Download a single file like cover or logo."""
        if not item or "url" not in item:
            logger.warning(f"No valid file found for {file_name} in project {listing_id}.")
            return None

        file_url = item["url"]
        ext = self.get_extension(file_url)
        file_path = os.path.join(files_dir, f"{file_name}{ext}")
        filename = f"{file_name}{ext}"

        if not os.path.exists(file_path):
            if self.download_files:
                self.download_file(file_url, file_path, listing_id)
            else:
                logger.info(f"Skipping download for {file_name} in project {listing_id}.")
        else:
            logger.info(f"File already exists for project {listing_id}, skipping: {file_path}")

        return {"id": file_name, "filename": filename, "url": file_url}

    def process_photos(self, photos, files_dir, listing_id):
        """Download photos into a photos/ subfolder."""
        photos_dir = os.path.join(files_dir, "photos")
        os.makedirs(photos_dir, exist_ok=True)

        photo_map = []
        for photo in photos:
            file_url = photo.get("url")
            if not file_url:
                logger.warning(f"Skipping photo due to missing URL in project {listing_id}.")
                continue

            # Create `name` from tags
            tags = " - ".join(photo.get("tags", [])) or "untagged"
            photo_id = photo.get("name")  # Preserve original name
            if not photo_id:
                logger.warning(f"Skipping photo due to missing name in project {listing_id}.")
                continue

            # Generate a slugified filename
            base_name = slugify(photo_id.split(".")[0], lowercase=True, separator="_")  # Remove duplicate extension
            ext = self.get_photo_extension(photo)  # Determine the correct extension
            filename = f"{base_name}{ext}"

            file_path = os.path.join(photos_dir, filename)

            # Download the file if it doesn't exist
            if not os.path.exists(file_path):
                if self.download_files:
                    self.download_file(file_url, file_path, listing_id)
                else:
                    logger.info(f"Skipping download for photo {photo_id} in project {listing_id}.")
            else:
                logger.info(f"Photo already exists for project {listing_id}, skipping: {file_path}")

            # Append to the map
            photo_map.append({
                "id": photo_id,       # Original name from the source data
                "name": tags,         # Name derived from tags
                "filename": filename,  # Slugified filename
                "url": file_url       # Original URL
            })

        return photo_map

    def process_floorplans(self, floorplans, files_dir, listing_id):
        """Download floor plans into a floorPlans/ subfolder."""
        floorplans_dir = os.path.join(files_dir, "floorPlans")
        os.makedirs(floorplans_dir, exist_ok=True)

        floorplan_map = []
        for floorplan in floorplans:
            file_url = floorplan.get("image", {}).get("url")
            if not file_url:
                logger.warning(f"Skipping floorplan due to missing URL in project {listing_id}.")
                continue

            floorplan_id = floorplan.get("id")
            name = floorplan.get("name", "Unnamed Floorplan")  # Extract `name` from source data
            ext = self.get_extension(file_url)
            file_path = os.path.join(floorplans_dir, f"{floorplan_id}{ext}")
            filename = f"{slugify(floorplan_id, lowercase=True, separator='_')}{ext}"

            if not os.path.exists(file_path):
                if self.download_files:
                    self.download_file(file_url, file_path, listing_id)
                else:
                    logger.info(f"Skipping download for floorplan {floorplan_id} in project {listing_id}.")
            else:
                logger.info(f"Floorplan already exists for project {listing_id}, skipping: {file_path}")

            floorplan_map.append({
                "id": floorplan_id,  # Original floorplan ID
                "name": name,        # Floorplan name from source
                "filename": filename,  # Slugified filename
                "url": file_url      # Original URL
            })

        return floorplan_map

    @staticmethod
    def get_photo_extension(photo):
        """Get the file extension for a photo using its `type` field or URL."""
        if "type" in photo and photo["type"].startswith("image/"):
            return f".{photo['type'].split('/')[-1]}"
        return os.path.splitext(urlparse(photo["url"]).path)[1] or ".jpg"

    @staticmethod
    def get_extension(url):
        """Extract the file extension from a URL."""
        return os.path.splitext(urlparse(url).path)[1] or ".jpg"

    @staticmethod
    def download_file(url, save_path, listing_id):
        """Download a file from a URL and save it to a local path."""
        try:
            logger.info(f"[{listing_id}] Downloading: {url} to {save_path}")
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"[{listing_id}] Download complete: {save_path}")
        except requests.RequestException as e:
            logger.error(f"[{listing_id}] Failed to download {url}: {e}")
