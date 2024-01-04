import os
from unittest.mock import mock_open, patch

from bug_trail.fs_utils import (
    clear_data,
    empty_folder,
    get_containing_folder_path,
    is_git_repo,
    prompt_and_update_gitignore,
)


def test_empty_folder(tmp_path):
    # Create subdirectories and files in the temporary directory
    sub_dir = tmp_path / "subfolder"
    sub_dir.mkdir()
    (sub_dir / "testfile.txt").write_text("sample text")

    assert len(os.listdir(sub_dir)) > 0  # Ensure the directory is not empty

    # Call the function
    empty_folder(str(sub_dir))

    # Verify that the directory is now empty
    assert len(os.listdir(sub_dir)) == 0


def test_clear_data(tmp_path):
    # Create a temporary log directory and database file
    log_folder = tmp_path / "logs"
    log_folder.mkdir()
    db_file = tmp_path / "test.db"
    db_file.write_text("sample db content")

    # Ensure the log directory and db file exist
    assert os.path.exists(log_folder)
    assert os.path.exists(db_file)

    # Call the clear_data function
    clear_data(str(log_folder), str(db_file))

    # Verify log folder is empty and db file is removed
    assert len(os.listdir(log_folder)) == 0
    assert not os.path.exists(db_file)


def test_get_containing_folder_path(tmp_path):
    # Create a temporary file
    temp_file = tmp_path / "tempfile.txt"
    temp_file.write_text("sample text")

    # Call the function
    folder_path = get_containing_folder_path(str(temp_file))

    # Verify the returned path is the absolute path of tmp_path
    assert folder_path == str(tmp_path.resolve())


def test_is_git_repo_with_git(tmp_path):
    # Create a .git directory in the temporary path
    (tmp_path / ".git").mkdir()

    # Call the function and verify it returns True
    assert is_git_repo(str(tmp_path))


def test_is_git_repo_without_git(tmp_path):
    # No .git directory

    # Call the function and verify it returns False
    assert not is_git_repo(str(tmp_path))


def test_prompt_and_update_gitignore_already_ignored(tmp_path):
    # Create a .git directory and a .gitignore file with 'logs' in it
    (tmp_path / ".git").mkdir()
    gitignore_path = tmp_path / ".gitignore"
    gitignore_path.write_text("logs")

    with patch("builtins.input", return_value="y"):
        with patch("builtins.open", mock_open(read_data="logs"), create=True):
            prompt_and_update_gitignore(str(tmp_path))
            # Since 'logs' is already in .gitignore, it should not prompt the user


def test_prompt_and_update_gitignore_add_ignore(tmp_path):
    # Create a .git directory and a .gitignore file without 'logs'
    (tmp_path / ".git").mkdir()
    gitignore_path = tmp_path / ".gitignore"
    gitignore_path.write_text("")

    with patch("builtins.input", return_value="y"):
        with patch("builtins.open", mock_open(read_data=""), create=True) as mock_file:
            prompt_and_update_gitignore(str(tmp_path))
            mock_file().write.assert_called_with("\nlogs/")
            # Check if 'logs' was written to .gitignore
