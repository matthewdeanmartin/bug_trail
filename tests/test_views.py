import logging
from unittest.mock import patch

from bug_trail_core.handlers import BugTrailHandler

from bug_trail.view_shared import detail_file_name, detail_file_name_grouped, pretty_column_name
from bug_trail.views import render_all, render_detail, render_main


def test_render_main(tmp_path):
    # Create a temporary database file and log folder
    db_path = tmp_path / "test.db"
    log_folder = tmp_path / "logs"
    log_folder.mkdir()

    # Set up the database and insert test log records
    handler = BugTrailHandler(str(db_path))
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.ERROR)
    logger.handlers.clear()
    logger.addHandler(handler)

    # Insert test log records
    test_message = "Test error log"
    logger.error(test_message)

    # Call render_main to render the HTML file
    render_main(str(db_path), str(log_folder), "")

    # Verify the HTML file is created
    index_file = log_folder / "index.html"
    assert index_file.exists()

    # Optionally, check the contents of the HTML file
    with open(index_file, encoding="utf-8") as f:
        content = f.read()
        assert test_message in content

    for leftover in logger.handlers:
        logger.removeHandler(leftover)
    # # Clean up
    # handler.close()


def test_pretty_column_name_special_cases():
    assert pretty_column_name("lineno") == "Line Number"
    assert pretty_column_name("funcName") == "Function Name"
    # Add tests for other special cases


def test_pretty_column_name_regular():
    assert pretty_column_name("some_column") == "Some Column"
    assert pretty_column_name("another_one") == "Another One"
    # Add tests for other regular cases


def test_detail_file_name():
    log_entry = {"created": "2022.01.01_12_00_00", "filename": "test_file.py", "lineno": 123}
    assert detail_file_name(log_entry) == "detail_2022_01_01_12_00_00_test_file_py_123.html"


def test_detail_file_name_grouped():
    log_entry = {
        "TemporalDetails": {"created": "2022.01.01_12_00_00"},
        "SourceContext": {"filename": "test_file.py", "lineno": 123},
    }
    assert detail_file_name_grouped(log_entry) == "detail_2022_01_01_12_00_00_test_file_py_123.html"


def test_render_detail(tmp_path):
    db_path = tmp_path / "test.db"
    log_folder = tmp_path / "logs"
    log_folder.mkdir()

    # Set up the database and insert test log records
    handler = BugTrailHandler(str(db_path))
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.ERROR)
    logger.handlers.clear()
    logger.addHandler(handler)

    # Insert test log records
    test_message = "Test error log"
    logger.error(test_message)

    # Call render_detail
    location = render_detail(str(db_path), str(log_folder), "")

    # Optionally, check the contents of the HTML file
    with open(location, encoding="utf-8") as f:
        content = f.read()
        assert "Test error log" in content  # Check for specific content based on log_entry

    for leftover in logger.handlers:
        logger.removeHandler(leftover)


@patch("bug_trail.views.empty_folder")
@patch("bug_trail.views.render_main")
@patch("bug_trail.views.render_detail")
def test_render_all(mock_render_detail, mock_render_main, mock_empty_folder):
    db_path = "mock_db_path"
    logs_folder = "mock_logs_folder"

    # Call render_all
    render_all(db_path, logs_folder, "", "")

    # Verify that the respective functions were called with correct arguments
    mock_empty_folder.assert_called_once_with(logs_folder)
    mock_render_main.assert_called_once_with(db_path, logs_folder, "")
    mock_render_detail.assert_called_once_with(db_path, logs_folder, "")
