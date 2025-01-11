"""PJ logger."""

import datetime as dt
import json
import logging
import logging.handlers
import pathlib
import typing as t

import rich.align
import rich.panel


class PanelHandler(logging.Handler):
    """Panel rich handler."""

    colors: t.ClassVar[dict[str, str]] = {
        "Debug": "blue",
        "Info": "green",
        "Warning": "yellow",
        "Error": "red",
        "Critical": "red",
    }
    fallback_color: str = "white"
    title_align: rich.align.AlignMethod = "left"
    show_error_names: bool = True

    def emit(self, record: logging.LogRecord) -> None:
        """Emit rich panel."""
        msg = record.getMessage()
        level = record.levelname.capitalize()
        msg_color = self.colors.get(level, self.fallback_color)
        if self.show_error_names and record.exc_info is not None:
            err_class = record.exc_info[0]
            if err_class is not None:
                level = err_class.__name__
                msg_color = "red"
        panel = rich.panel.Panel(
            msg,
            title=level,
            border_style=msg_color,
            title_align=self.title_align,
        )
        rich.print(panel)


class JsonlFormatter(logging.Formatter):
    """
    Jsonl formatter.

    Courtesy of https://github.com/mCodingLLC
    """

    # @t.override
    def format(self, record: logging.LogRecord) -> str:
        """Customize format."""
        message = self._log_dict(record)
        return json.dumps(message, default=str)

    def _log_dict(self, record: logging.LogRecord) -> dict[str, t.Any]:
        message = {
            "levelname": "",
            "message": "",
            "created": "",
        }
        message.update(record.__dict__)
        message["created"] = dt.datetime.fromtimestamp(record.created, tz=dt.UTC).isoformat()
        if record.relativeCreated is not None:
            message["relativeCreated"] = dt.datetime.fromtimestamp(record.relativeCreated, tz=dt.UTC).isoformat()
        if record.exc_info is not None:
            message["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info is not None:
            message["stack_info"] = self.formatStack(record.stack_info)
        return message


def set_logger(
    name: str | None = None,
    *,
    jsonl_log_file_path: pathlib.Path | str | None = None,
    jsonl_log_file_size: int = 100_000,
    jsonl_log_backup_count: int = 3,
    rich_panel_log: bool = False,
) -> logging.Logger:
    """Set logger."""
    _logger = logging.getLogger(name)
    _logger.setLevel(logging.DEBUG)
    if jsonl_log_file_path is not None:
        _jsonl_handler = logging.handlers.RotatingFileHandler(
            filename=jsonl_log_file_path,
            maxBytes=jsonl_log_file_size,
            backupCount=jsonl_log_backup_count,
        )
        _jsonl_handler.setFormatter(JsonlFormatter())
        _jsonl_handler.set_name("jsonl")
        _jsonl_handler.setLevel(logging.DEBUG)
        _logger.addHandler(_jsonl_handler)
    if rich_panel_log:
        _rich_panel_handler = PanelHandler()
        _rich_panel_handler.set_name("panel")
        _rich_panel_handler.setLevel(logging.INFO)
        _logger.addHandler(_rich_panel_handler)
    return _logger

