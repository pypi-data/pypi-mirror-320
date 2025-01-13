import os
import json
from .utils.logger_config import get_logger
import typing

logger = get_logger(__name__)


class SchemaProject:
    """Represents a single project with methods to access its JSON data."""

    def __init__(self, project_id, project_path):
        self.project_id = project_id
        self.project_path = project_path

    def get_file_details(self, file_name) -> dict:
        """Get details of a specific file."""
        file_path = os.path.join(self.project_path, file_name)
        if os.path.exists(file_path):
            logger.info(f"Processing file: {file_name} in {self.project_path}")
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
                # return {
                #     'name': file_name,
                #     'size': os.path.getsize(file_path),
                #     'path': file_path,
                #     'data': data,
                # }
        logger.warning(f"File {file_name} not found in {self.project_path}")
        return None

    def get_deposits_suites(self) -> dict:
        return self.get_file_details('deposits_suites.json')

    def get_deposits_project(self) -> dict:
        return self.get_file_details('deposits_project.json')

    def get_deposits(self) -> dict:
        return self.get_file_details('deposits.json')

    def get_data(self) -> dict:
        return self.get_file_details('data.json')

    def get_map(self) -> dict:
        return self.get_file_details('map.json')

    def get_parsed_date(self) -> dict:
        return self.get_file_details('parsed_date.json')


class ProjectDataReader:
    """Handles processing of projects and returns a list of Project instances."""

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def process_projects(self) -> typing.List[SchemaProject]:
        """Process each project folder and return a list of Project instances."""
        if not os.path.exists(self.data_dir):
            logger.error(f"Directory {self.data_dir} does not exist.")
            return []

        projects = []
        logger.info(f"Starting processing for projects in {self.data_dir}")

        for project_id in os.listdir(self.data_dir):
            project_path = os.path.join(self.data_dir, project_id)
            if not os.path.isdir(project_path):
                logger.debug(f"Skipping non-directory item: {project_id}")
                continue

            # logger.info(f"Processing project: {project_id}")
            projects.append(SchemaProject(project_id, project_path))

        # logger.info(f"Finished processing all projects in {self.data_dir}")
        return projects
