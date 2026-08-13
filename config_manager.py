import json
from pathlib import Path
from typing import Any, Dict, Optional
from utils.paths import get_project_root, resolve_app_path
from utils.logger import get_logger

logger = get_logger("ConfigManager")

class ConfigManager:
    def __init__(self):
        self.root_dir = get_project_root()
        self.settings_file = self.root_dir / "config" / "settings.json"
        self.apps_file = self.root_dir / "config" / "apps.json"
        
        self._settings: Dict[str, Any] = {}
        self._apps: Dict[str, Any] = {}
        
        self.load_all()

    def load_all(self):
        """Loads settings and app registry from disk."""
        self._settings = self._load_json(self.settings_file)
        self._apps = self._load_json(self.apps_file)

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            logger.warning(f"Config file not found: {path}")
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading config file {path}: {e}")
            return {}

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def update_setting(self, key: str, value: Any) -> bool:
        self._settings[key] = value
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to update setting {key}: {e}")
            return False

    def get_app_info(self, app_name_or_alias: str) -> Optional[Dict[str, Any]]:
        """
        Looks up application by canonical key or alias in apps.json.
        Returns dictionary containing executable name, resolved path, and aliases.
        """
        query = app_name_or_alias.lower().strip()
        
        for app_key, app_data in self._apps.items():
            aliases = [a.lower() for a in app_data.get("aliases", [])]
            if query == app_key.lower() or query in aliases or query == app_data.get("executable", "").lower():
                exec_name = app_data.get("executable")
                resolved = resolve_app_path(exec_name)
                return {
                    "key": app_key,
                    "executable": exec_name,
                    "resolved_path": resolved,
                    "aliases": app_data.get("aliases", [])
                }
        return None

    def get_all_apps(self) -> Dict[str, Any]:
        return self._apps

_config_instance: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
