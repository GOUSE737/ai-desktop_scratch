import os
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from utils.paths import get_common_user_dirs, get_user_home_dir
from utils.logger import get_logger

logger = get_logger("FileManager")

class FileManager:
    """
    Handles file searching, folder creation, file renaming, moving, copying, and safe deletion.
    """
    def __init__(self):
        self.common_dirs = get_common_user_dirs()

    def create_folder(self, folder_name: str, parent_path: Optional[Path] = None) -> Tuple[bool, str]:
        """Creates a new directory in standard Desktop/Documents or target path."""
        target_dir = parent_path or self.common_dirs.get("desktop") or get_user_home_dir()
        new_folder_path = target_dir / folder_name.strip()

        try:
            new_folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder at: '{new_folder_path}'")
            return True, f"Folder '{folder_name}' created successfully at {new_folder_path.name}."
        except Exception as e:
            logger.error(f"Failed to create folder '{folder_name}': {e}")
            return False, f"Failed to create folder: {str(e)}"

    def search_files(self, query: str, extension: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Searches user directories (Desktop, Documents, Downloads) for matching files.
        """
        results = []
        search_term = query.lower().strip()
        search_dirs = [
            self.common_dirs["desktop"],
            self.common_dirs["documents"],
            self.common_dirs["downloads"]
        ]

        # Extract file extension filter if query specifies like 'pdf', 'txt', 'python'
        ext_filter = extension
        if not ext_filter:
            if "pdf" in search_term:
                ext_filter = ".pdf"
            elif "python" in search_term or "py" in search_term:
                ext_filter = ".py"
            elif "doc" in search_term or "word" in search_term:
                ext_filter = ".docx"

        for s_dir in search_dirs:
            if not s_dir.exists():
                continue
            for root, _, files in os.walk(s_dir):
                for f in files:
                    f_lower = f.lower()
                    if ext_filter and not f_lower.endswith(ext_filter):
                        continue
                    if search_term in f_lower or not search_term or search_term in ["pdf", "files", "python"]:
                        full_path = Path(root) / f
                        results.append({
                            "name": f,
                            "path": str(full_path),
                            "size": full_path.stat().st_size if full_path.exists() else 0,
                            "extension": full_path.suffix
                        })
                        if len(results) >= max_results:
                            return results
        return results

    def rename_item(self, source_path_str: str, new_name: str) -> Tuple[bool, str]:
        """Renames a file or folder safely."""
        source_path = Path(source_path_str)
        if not source_path.exists():
            # Try looking up file in desktop/documents
            found = self.search_files(source_path_str, max_results=1)
            if found:
                source_path = Path(found[0]["path"])
            else:
                return False, f"File or folder '{source_path_str}' not found."

        new_path = source_path.parent / new_name.strip()
        try:
            source_path.rename(new_path)
            logger.info(f"Renamed '{source_path}' to '{new_path}'")
            return True, f"Renamed to '{new_name}' successfully."
        except Exception as e:
            logger.error(f"Rename failed: {e}")
            return False, f"Rename operation failed: {str(e)}"

    def move_item(self, source_path_str: str, dest_folder_name: str) -> Tuple[bool, str]:
        """Moves a file or folder into a destination folder."""
        source_path = Path(source_path_str)
        if not source_path.exists():
            found = self.search_files(source_path_str, max_results=1)
            if found:
                source_path = Path(found[0]["path"])
            else:
                return False, f"Source '{source_path_str}' not found."

        dest_dir = self.common_dirs.get("desktop") / dest_folder_name.strip()
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(str(source_path), str(dest_dir))
            logger.info(f"Moved '{source_path}' to '{dest_dir}'")
            return True, f"Moved '{source_path.name}' to '{dest_folder_name}'."
        except Exception as e:
            logger.error(f"Move item failed: {e}")
            return False, f"Move operation failed: {str(e)}"

    def delete_item(self, target_path_str: str) -> Tuple[bool, str]:
        """
        Deletes a file or directory (High Risk action requiring prior confirmation).
        """
        target_path = Path(target_path_str)
        if not target_path.exists():
            found = self.search_files(target_path_str, max_results=1)
            if found:
                target_path = Path(found[0]["path"])
            else:
                return False, f"Target '{target_path_str}' not found for deletion."

        try:
            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()
            logger.warning(f"Deleted item at: '{target_path}'")
            return True, f"Successfully deleted '{target_path.name}'."
        except Exception as e:
            logger.error(f"Delete operation failed: {e}")
            return False, f"Deletion failed: {str(e)}"
