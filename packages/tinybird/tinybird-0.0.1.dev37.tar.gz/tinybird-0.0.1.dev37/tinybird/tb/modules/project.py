import glob
import os
from pathlib import Path
from typing import List, Optional

from tinybird.tb.modules.config import CLIConfig


class Project:
    extensions = ("datasource", "pipe")

    def __init__(self, folder: Optional[str] = None):
        self.folder = folder or os.getcwd()
        self.path = Path(self.folder)

    def get_config(self) -> CLIConfig:
        return CLIConfig.get_project_config(self.folder)

    @property
    def vendor_path(self) -> str:
        return f"{self.path}/vendor"

    def get_project_files(self) -> List[str]:
        project_files: List[str] = []
        for extension in self.extensions:
            for project_file in glob.glob(f"{self.path}/**/*.{extension}", recursive=True):
                if self.vendor_path in project_file:
                    continue
                project_files.append(project_file)
        return project_files

    def get_vendor_files(self) -> List[str]:
        vendor_files: List[str] = []
        for project_file in glob.glob(f"{self.vendor_path}/**/*.datasource", recursive=True):
            vendor_files.append(project_file)
        return vendor_files

    @property
    def datasources(self) -> List[str]:
        return [Path(f).stem for f in glob.glob(f"{self.path}/**/*.datasource", recursive=True)]

    @property
    def pipes(self) -> List[str]:
        return [Path(f).stem for f in glob.glob(f"{self.path}/**/*.pipe", recursive=True)]
