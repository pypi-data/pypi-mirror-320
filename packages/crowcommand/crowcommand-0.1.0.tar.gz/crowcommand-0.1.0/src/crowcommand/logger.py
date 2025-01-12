from typing import Any, Optional, Union, TextIO, Dict, Callable
from pathlib import Path
from loguru import logger as _logger
from crowcommander.client import APIClient
from .internal_logger import logger as internal_logger
import traceback
import inspect
import sys
import linecache

class Logger:
    """A wrapper class for the Loguru logger providing type-safe logging functionality."""

    def __init__(self) -> None:
        """Initialize the Logger with a Loguru logger instance."""
        self._logger = _logger
        self._client: APIClient = None
        self._environment = "development"

    def info(self, message: str, **kwargs: Any) -> None:
        """Log a message with severity 'INFO'.

        Args:
            message: The message to be logged.
            **kwargs: Additional keyword arguments passed to the logger.
        """
        return self._logger.info(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log a message with severity 'ERROR'.

        Args:
            message: The message to be logged.
            **kwargs: Additional keyword arguments passed to the logger.
        """
        try:
            if self._client:
                stack_trace = ''.join(traceback.format_stack()[:-1])
                
                payload = {
                    "message": str(message),
                    "context": self._get_caller_context(),
                    "code_location": self._get_code_location(),
                    "stack_trace": stack_trace,
                    "environment": self._environment
                }
                internal_logger.debug("Sending error log to API")
                self._client._make_request("POST", "/api/ingest/logs", json=payload)
        except Exception as e:
            internal_logger.error(f"Failed to send error log to API: {str(e)}")
            pass
        
        return self._logger.error(message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a message with severity 'DEBUG'.

        Args:
            message: The message to be logged.
            **kwargs: Additional keyword arguments passed to the logger.
        """
        return self._logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a message with severity 'WARNING'.

        Args:
            message: The message to be logged.
            **kwargs: Additional keyword arguments passed to the logger.
        """
        return self._logger.warning(message, **kwargs)

    def add(
        self,
        sink: Union[str, Path, TextIO, Callable],
        *,
        level: Optional[Union[str, int]] = None,
        format: Optional[str] = None,
        filter: Optional[Union[str, Dict[str, Any], Callable]] = None,
        colorize: Optional[bool] = None,
        serialize: Optional[bool] = None,
        backtrace: Optional[bool] = None,
        diagnose: Optional[bool] = None,
        enqueue: Optional[bool] = None,
        catch: Optional[bool] = None,
        **kwargs: Any
    ) -> int:
        """Add a logging sink (a destination for log messages).

        Args:
            sink: The sink to write logs to. Can be a file path, sys.stderr, or a callable.
            level: The minimum severity level to log. Can be name ("DEBUG") or number (10).
            format: The format string to use for log messages.
            filter: Filters to apply to log messages.
            colorize: Whether to colorize log messages.
            serialize: Whether to serialize log messages as JSON.
            backtrace: Whether to include backtrace in error logs.
            diagnose: Whether to include extended debug information.
            enqueue: Whether to enqueue log messages for async processing.
            catch: Whether to catch exceptions during sink writing.
            **kwargs: Additional keyword arguments for sink configuration.

        Returns:
            int: An identifier for the added sink that can be used to remove it later.

        Example:
            >>> logger = Logger()
            >>> # Add a file sink for all DEBUG and above messages
            >>> sink_id = logger.add("debug.log", level="DEBUG")
            >>> # Add console sink for INFO and above with custom format
            >>> logger.add(sys.stderr, level="INFO", format="{time} {message}")
        """
        return self._logger.add(
            sink,
            level=level,
            format=format,
            filter=filter,
            colorize=colorize,
            serialize=serialize,
            backtrace=backtrace,
            diagnose=diagnose,
            enqueue=enqueue,
            catch=catch,
            **kwargs
        )

    def remove(self, handler_id: Optional[int] = None) -> None:
        """Remove a logging sink by its identifier.

        Args:
            handler_id: The identifier of the sink to remove, returned by add().
                      If None, all sinks will be removed.

        Example:
            >>> logger = Logger()
            >>> sink_id = logger.add("file.log")
            >>> # Later, remove this specific sink
            >>> logger.remove(sink_id)
            >>> # Or remove all sinks
            >>> logger.remove()
        """
        return self._logger.remove(handler_id)
    
    def _get_caller_context(self) -> Dict[str, Any]:
        """Extract the code context from where the error occurred."""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback:
            tb = traceback.extract_tb(exc_traceback)[-1]
            filename = tb.filename
            lineno = tb.lineno
            
            lines = []
            for i in range(lineno - 10, lineno + 11):  
                line = linecache.getline(filename, i)
                if line:
                    lines.append(line.rstrip())
                    
            if lines:
                return {
                    "code": "\n".join(lines)
                }
        
        return {"code": ""}
    
    def _get_code_location(self) -> str:
        """Get the file and line number where the error occurred."""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback:
            tb = traceback.extract_tb(exc_traceback)[-1]
            return f"{tb.filename}:{tb.lineno}"
        
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back.f_back
            if caller_frame:
                filename = caller_frame.f_code.co_filename
                lineno = caller_frame.f_lineno
                return f"{filename}:{lineno}"
        finally:
            del frame
        return ""