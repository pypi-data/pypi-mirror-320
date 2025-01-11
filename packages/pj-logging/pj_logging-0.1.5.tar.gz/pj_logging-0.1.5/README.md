[github_release]: https://img.shields.io/github/release/the-citto/pj-logging.svg?logo=github&logoColor=white&color=orange
[pypi_version]: https://img.shields.io/pypi/v/pj-logging.svg?logo=python&logoColor=white
[python_versions]: https://img.shields.io/pypi/pyversions/pj-logging.svg?logo=python&logoColor=white
[github_license]: https://img.shields.io/github/license/the-citto/pj-logging.svg?logo=github&logoColor=white

[![GitHub Release][github_release]](https://github.com/the-citto/pj-logging/releases/)
[![PyPI Version][pypi_version]](https://pypi.org/project/pj-logging/)
[![Python Versions][python_versions]](https://pypi.org/project/pj-logging/)
[![License][github_license]](https://github.com/the-citto/pj-logging/blob/master/LICENSE)
<br>

# ▍▞ PJ logging

Simple logging with 
[rich](https://github.com/Textualize/rich) [Panel](https://rich.readthedocs.io/en/latest/panel.html)s and 
[jsonl](https://jsonlines.org/) (or plain `.log`) files

## Basic Usage

`set_logger` arguments, with types and defaults:

```python
def set_logger(
    name: str | None = None,
    *,
    jsonl_log_file_path: pathlib.Path | str | None = None,
    jsonl_log_file_size: int = 100_000,
    jsonl_log_backup_count: int = 3,
    rich_panel_log: bool = False,
) -> logging.Logger: ...
```

Example, with `rich`'s `Panel`s only

```python
import pj_logging

logger = pj_logging.set_logger(rich_panel_log=True)


...


logger.info("this is an info log with a rich Panel in the terminal")
```

## Advanced usage

The `set_logger` function uses the `logging` `RotatingFileHandler` 
([docs](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler)) for the output file

For different needs, the `JsonlFormatter` can be assigned to a different handler

#

The `PanelHandler` can also be imported and added to an existing logger.

With this approach, it's possible to change values of the class' attributes
before adding the handler to the logger.

```python
class PanelHandler(logging.Handler):
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
```

