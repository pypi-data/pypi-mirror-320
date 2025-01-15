from typing import TYPE_CHECKING

from graph_sitter.codebase.config_parser import ConfigParser
from graph_sitter.core.file import File
from graph_sitter.enums import NodeType
from graph_sitter.typescript.ts_config import TSConfig

if TYPE_CHECKING:
    from graph_sitter.codebase.codebase_graph import CodebaseGraph
    from graph_sitter.typescript.file import TSFile

import os
from functools import cache


class TSConfigParser(ConfigParser):
    # Cache of path names to TSConfig objects
    config_files: dict[str, TSConfig]
    G: "CodebaseGraph"

    def __init__(self, codebase_graph: "CodebaseGraph", default_config_name: str = "tsconfig.json"):
        super().__init__()
        self.config_files = dict()
        self.G = codebase_graph
        self.default_config_name = default_config_name

    def get_config(self, config_path: str) -> TSConfig | None:
        if config_path in self.config_files:
            return self.config_files[config_path]
        if os.path.exists(config_path):
            self.config_files[config_path] = TSConfig(File.from_content(config_path, open(config_path).read(), self.G, sync=False), self)
            return self.config_files.get(config_path)
        return None

    def parse_configs(self):
        # This only yields a 0.05s speedup, but its funny writing dynamic programming code
        @cache
        def get_config_for_dir(dir_path: str) -> TSConfig | None:
            # Check if the config file exists in the directory
            ts_config_path = os.path.join(dir_path, self.default_config_name)
            # If it does, return the config
            if os.path.exists(ts_config_path):
                if ts_config := self.get_config(ts_config_path):
                    self.config_files[dir_path] = ts_config
                    return ts_config
            # Otherwise, check the parent directory
            if dir_path:
                return get_config_for_dir(os.path.dirname(dir_path))
            return None

        # Get all the files in the codebase
        for file in self.G.get_nodes(NodeType.FILE):
            file: TSFile  # This should be safe because we only call this on TSFiles
            # Get the config for the directory the file is in
            config = get_config_for_dir(os.path.dirname(file.filepath))
            # Set the config for the file
            file.ts_config = config

        # Loop through all the configs and precompute their import aliases
        for config in self.config_files.values():
            config._precompute_import_aliases()
