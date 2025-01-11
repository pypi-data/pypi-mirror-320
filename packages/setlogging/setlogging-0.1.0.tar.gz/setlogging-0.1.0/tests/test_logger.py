import pytest
import json
import os
import logging
from datetime import datetime
from setlogging import get_logger, setup_logging, TimezoneFormatter


class LogCapture:
    def __init__(self):
        self.records = []

    def __enter__(self):
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.DEBUG)
        self.records = []
        self.handler.emit = lambda record: self.records.append(record)
        logging.getLogger().addHandler(self.handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.getLogger().removeHandler(self.handler)


def test_basic_logger():
    """Test basic logger initialization"""
    logger = get_logger()
    assert logger is not None
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG


def test_json_logging(tmp_path):
    """Test JSON format logging"""
    log_file = tmp_path / "test.json"
    logger = get_logger(json_format=True, log_file=str(log_file))
    test_message = "Test JSON logging"
    logger.info(test_message)

    with open(log_file) as f:
        log_entry = json.loads(f.read())
        assert "message" in log_entry
        assert log_entry["message"] == test_message
        assert "level" in log_entry
        assert log_entry["level"] == "INFO"


def test_timezone_awareness():
    """Test timezone information in logs"""
    logger = get_logger()
    formatter = next((h.formatter for h in logger.handlers
                     if isinstance(h.formatter, TimezoneFormatter)), None)
    assert formatter is not None
    assert formatter.local_timezone is not None


def test_file_rotation(tmp_path):
    """Test log file rotation"""
    log_file = tmp_path / "rotate.log"
    max_size_mb = 1  # 1MB
    backup_count = 3
    logger = get_logger(
        log_file=str(log_file),
        max_size_mb=max_size_mb,
        backup_count=backup_count
    )

    # Write enough data to trigger rotation
    for i in range(100):
        logger.info("x" * 1024 * 10)  # 10KB per log entry

    assert os.path.exists(log_file)
    assert os.path.exists(f"{log_file}.1")


def test_invalid_parameters():
    """Test error handling for invalid parameters"""
    with pytest.raises(ValueError):
        get_logger(max_size_mb=-1)

    with pytest.raises(ValueError):
        get_logger(backup_count=-1)

    with pytest.raises(ValueError):
        get_logger(indent=2, json_format=False)


def test_console_output(capsys):
    """Test console output"""
    logger = get_logger(console_output=True)
    test_message = "Test console output"
    logger.info(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.err or test_message in captured.out


def test_json_file_extension():
    """Test JSON file extension is set correctly"""
    logger = get_logger(json_format=True)
    handlers = [h for h in logger.handlers if isinstance(
        h, logging.FileHandler)]
    assert any(h.baseFilename.endswith('.json') for h in handlers)


def test_json_indent(tmp_path):
    """Test JSON indentation formatting"""
    log_file = tmp_path / "test_indent.json"
    indent = 4
    logger = get_logger(
        json_format=True,
        indent=indent,
        log_file=str(log_file)
    )

    test_message = "Test indent"
    logger.info(test_message)

    with open(log_file) as f:
        content = f.read()
        # Verify content is properly indented JSON
        parsed = json.loads(content)
        formatted = json.dumps(parsed, indent=indent)
        assert content.strip() == formatted.strip()
        assert "message" in parsed
        assert parsed["message"] == test_message


def test_json_structure(tmp_path):
    """Test JSON log entry structure"""
    log_file = tmp_path / "test_structure.json"
    logger = get_logger(json_format=True, log_file=str(log_file))

    logger.info("Test message", extra={"custom_field": "value"})

    with open(log_file) as f:
        log_entry = json.loads(f.read())
        required_fields = ["time", "level", "message", "name"]
        for field in required_fields:
            assert field in log_entry
        assert log_entry["custom_field"] == "value"


def test_invalid_json_parameters():
    """Test invalid JSON parameters"""
    # Test invalid indent with json_format=False
    with pytest.raises(ValueError, match="indent parameter is only valid"):
        get_logger(json_format=False, indent=2)


def test_log_level_configuration():
    """Test different log levels"""
    logger = get_logger(log_level=logging.WARNING)
    assert logger.level == logging.WARNING

    # Debug shouldn't log
    with LogCapture() as capture:
        logger.debug("Debug message")
        assert len(capture.records) == 0

        # Warning should log
        logger.warning("Warning message")
        assert len(capture.records) == 1


def test_custom_date_format(tmp_path):
    """Test custom date format"""
    log_file = tmp_path / "date_format.log"
    date_format = "%Y-%m-%d"
    logger = get_logger(
        log_file=str(log_file),
        date_format=date_format
    )
    logger.info("Test message")

    with open(log_file) as f:
        content = f.read()
        assert datetime.now().strftime(date_format) in content


def test_custom_log_format():
    """Test custom log format"""
    custom_format = "%(levelname)s - %(message)s"
    logger = get_logger(log_format=custom_format)

    with LogCapture() as capture:
        logger.info("Test message")
        assert "INFO - Test message" in str(capture.records[0])


def test_multiple_handlers():
    """Test multiple handlers configuration"""
    logger = get_logger(console_output=True)
    assert len(logger.handlers) >= 2  # File and console handlers

    handler_types = [type(h) for h in logger.handlers]
    assert logging.StreamHandler in handler_types
    assert logging.FileHandler in handler_types


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up log files after tests"""
    yield
    for handler in logging.getLogger().handlers[:]:
        handler.close()
        logging.getLogger().removeHandler(handler)
