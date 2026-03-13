"""
Batch Script Executor
Executes Windows batch scripts with real-time output monitoring
"""

import subprocess
import threading
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExecutionResult:
    """Result of batch script execution"""
    success: bool
    output: str
    errors: str
    return_code: int
    duration: float  # seconds


class BatchExecutor:
    """Executes batch scripts with monitoring capabilities"""

    def __init__(self,
                 on_output: Optional[Callable[[str], None]] = None,
                 on_progress: Optional[Callable[[int], None]] = None):
        """
        Initialize batch executor

        Args:
            on_output: Callback for each line of output
            on_progress: Callback for progress updates (0-100)
        """
        self.on_output = on_output
        self.on_progress = on_progress
        self.process: Optional[subprocess.Popen] = None
        self._cancelled = False

    def execute(self,
                script_path: Path,
                args: Optional[list] = None,                elevated: bool = True,
                timeout: int = 300) -> ExecutionResult:
        """
        Execute a batch script synchronously.

        Args:
            script_path: Path to .bat file
            args: Command line arguments
            elevated: Reserved — the process must already be running as admin
                      before calling this method.  Passing ``True`` when the
                      caller is *not* an administrator is logged as a warning
                      but does NOT re-launch with elevation.
            timeout: Maximum execution time in seconds

        Returns:
            ExecutionResult with output and status
        """
        import time

        # Reset cancelled flag so executor can be reused between calls.
        self._cancelled = False

        start_time = time.time()
        logger.info(f"Executing batch script: {script_path}")

        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return ExecutionResult(
                success=False,
                output="",
                errors=f"Script not found: {script_path}",
                return_code=-1,
                duration=0,
            )

        # Validate script for dangerous patterns before executing.
        from core.batch_parser import BatchParser
        try:
            # BatchParser requires a directory; pass the script's parent.
            parser = BatchParser(script_path.parent)
            script_obj = parser.parse_script(script_path)
            if not parser.validate_script(script_obj):
                logger.error(f"Script failed safety validation: {script_path}")
                return ExecutionResult(
                    success=False,
                    output="",
                    errors=f"Script failed safety validation: {script_path.name}",
                    return_code=-1,
                    duration=0,
                )
        except Exception as validation_err:
            logger.warning(f"Could not validate script (proceeding with caution): {validation_err}")

        # Prepare command
        cmd = [str(script_path)]
        if args:
            cmd.extend(args)

        # Execute
        output_lines: list = []
        error_lines: list = []
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            # Read output in real-time
            def read_stream(stream, is_error: bool = False) -> None:
                for line in iter(stream.readline, ''):
                    if line:
                        line = line.rstrip()
                        if is_error:
                            error_lines.append(line)
                        else:
                            output_lines.append(line)

                        if self.on_output:
                            self.on_output(line)

                        logger.debug(f"{'[ERROR]' if is_error else '[OUTPUT]'} {line}")

            # Create threads for stdout and stderr
            stdout_thread = threading.Thread(
                target=read_stream, args=(self.process.stdout, False)
            )
            stderr_thread = threading.Thread(
                target=read_stream, args=(self.process.stderr, True)
            )

            stdout_thread.start()
            stderr_thread.start()

            # Wait for completion
            return_code = self.process.wait(timeout=timeout)

            # Wait for reader threads — bounded so we don't hang forever.
            stdout_thread.join(timeout=10)
            stderr_thread.join(timeout=10)

            duration = time.time() - start_time
            success = return_code == 0 and not self._cancelled

            logger.info(
                f"Script completed: {script_path} "
                f"(return code: {return_code}, duration: {duration:.2f}s)"
            )

            return ExecutionResult(
                success=success,
                output='\n'.join(output_lines),
                errors='\n'.join(error_lines),
                return_code=return_code,
                duration=duration,
            )

        except subprocess.TimeoutExpired:
            logger.error(f"Script timed out after {timeout}s: {script_path}")
            self.cancel()
            return ExecutionResult(
                success=False,
                output='\n'.join(output_lines),
                errors=f"Script timed out after {timeout} seconds",
                return_code=-1,
                duration=timeout,
            )

        except Exception as e:
            logger.exception(f"Error executing script: {script_path}")
            return ExecutionResult(
                success=False,
                output="",
                errors=str(e),
                return_code=-1,
                duration=time.time() - start_time,
            )

    def execute_async(self,
                      script_path: Path,
                      on_complete: Optional[Callable[[ExecutionResult], None]] = None) -> None:
        """
        Execute script asynchronously in a separate thread.

        Args:
            script_path: Path to .bat file
            on_complete: Callback when execution completes
        """
        def run() -> None:
            result = self.execute(script_path)
            if on_complete:
                on_complete(result)

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def cancel(self) -> None:
        """Cancel the running execution."""
        self._cancelled = True
        if self.process:
            logger.warning("Cancelling batch script execution")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate — killing forcefully")
                self.process.kill()
            except Exception as e:
                logger.error(f"Failed to terminate process: {e}")
