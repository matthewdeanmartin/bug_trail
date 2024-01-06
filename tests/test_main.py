from unittest.mock import MagicMock, patch

from bug_trail.__main__ import main


@patch("bug_trail.fs_utils.clear_data")
@patch("bug_trail.fs_utils.prompt_and_update_gitignore")
@patch("bug_trail.views.render_all")
@patch("argparse.ArgumentParser.parse_args")
def test_main_clear(mock_parse_args, mock_render_all, mock_prompt_and_update_gitignore, mock_clear_data):
    mock_parse_args.return_value = MagicMock(clear=True, db="error_log.db", output="logs")

    assert main() == 0
    mock_clear_data.assert_called_once_with("logs", "error_log.db")
    mock_prompt_and_update_gitignore.assert_not_called()
    mock_render_all.assert_not_called()


@patch("bug_trail.fs_utils.clear_data")
@patch("bug_trail.fs_utils.prompt_and_update_gitignore")
@patch("bug_trail.views.render_all")
@patch("argparse.ArgumentParser.parse_args")
def test_main_default_action(mock_parse_args, mock_render_all, mock_prompt_and_update_gitignore, mock_clear_data):
    mock_parse_args.return_value = MagicMock(
        clear=False, db="error_log.db", output="logs", source="source_folder", ctags_file="tags_file"
    )

    assert main() == 0
    mock_clear_data.assert_not_called()
    # temporarily turning this off
    # mock_prompt_and_update_gitignore.assert_called_once_with(".")
    mock_prompt_and_update_gitignore.assert_not_called()
    mock_render_all.assert_called_once_with("error_log.db", "logs", "source_folder", "tags_file")


# Additional tests can be added to cover more scenarios
