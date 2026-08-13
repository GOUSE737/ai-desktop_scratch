import pytest
from pathlib import Path
from automation.file_manager import FileManager

@pytest.fixture
def tmp_file_env(tmp_path):
    fm = FileManager()
    # Override desktop dir with tmp_path for test isolation
    fm.common_dirs["desktop"] = tmp_path
    return fm, tmp_path

def test_create_folder(tmp_file_env):
    fm, tmp_path = tmp_file_env
    success, msg = fm.create_folder("Major Project", parent_path=tmp_path)
    assert success is True
    assert (tmp_path / "Major Project").exists()

def test_search_files(tmp_file_env):
    fm, tmp_path = tmp_file_env
    test_pdf = tmp_path / "report.pdf"
    test_pdf.write_text("sample content")

    results = fm.search_files("report", extension=".pdf")
    assert len(results) >= 1
    assert results[0]["name"] == "report.pdf"

def test_rename_and_delete(tmp_file_env):
    fm, tmp_path = tmp_file_env
    test_file = tmp_path / "draft.txt"
    test_file.write_text("draft data")

    # Rename
    success_ren, _ = fm.rename_item(str(test_file), "final.txt")
    assert success_ren is True
    assert (tmp_path / "final.txt").exists()
    assert not (tmp_path / "draft.txt").exists()

    # Delete
    success_del, _ = fm.delete_item(str(tmp_path / "final.txt"))
    assert success_del is True
    assert not (tmp_path / "final.txt").exists()
