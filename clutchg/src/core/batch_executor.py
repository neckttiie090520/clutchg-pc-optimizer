"""
Batch Script Executor
Executes Windows batch scripts with real-time output monitoring
"""

import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass

from core.paths import backup_dir
from utils.logger import get_logger

logger = get_logger(__name__)


def recovery_environment() -> dict:
    """Environment that roots batch recovery artifacts in the writable data directory.

    The batch engine defaults its backup root to a directory beside the scripts.
    In a packaged install that location lives under Program Files and is removed on
    uninstall, so committed recovery transactions would be unreachable from the
    Restore Center. BACKUPS_DIR pins both writers to one root.
    """
    environment = dict(os.environ)
    environment["BACKUPS_DIR"] = str(backup_dir())
    return environment


# Windows hands batch arguments to cmd.exe, which acts on shell metacharacters
# before the script can validate anything. An argument carrying one of these would
# run its tail as a separate command with the elevated app's privileges, so any
# argument containing one is refused rather than escaped — every legitimate caller
# passes a label, a fixed keyword, or a timestamp-shaped ID.
_SHELL_METACHARACTERS = frozenset('&|<>^"\'`\n\r\x00')


def _argument_is_shell_safe(argument: str) -> bool:
    """Whether an argument can be passed to a .bat file without cmd.exe injection."""
    return not (_SHELL_METACHARACTERS & set(argument))


@dataclass
class ExecutionResult:
    """Result of batch script execution"""

    success: bool
    output: str
    errors: str
    return_code: int
    duration: float  # seconds


class BatchExecutor:
    """Executes batch scripts with monitoring capabilities."""

    def __init__(
        self,
        on_output: Optional[Callable[[str], None]] = None,
        on_progress: Optional[Callable[[int], None]] = None,
    ):
        """Initialize a single cancellation-aware execution transaction."""
        self.on_output = on_output
        self.on_progress = on_progress
        self.process: Optional[subprocess.Popen] = None
        self._cancel_event = threading.Event()
        self._state_lock = threading.Lock()

    @property
    def _cancelled(self) -> bool:
        """Compatibility view of the persistent per-job cancellation state."""
        return self._cancel_event.is_set()

    @_cancelled.setter
    def _cancelled(self, value: bool) -> None:
        if value:
            self._cancel_event.set()
        else:
            self._cancel_event.clear()

    @staticmethod
    def _cancelled_result(duration: float = 0) -> ExecutionResult:
        return ExecutionResult(
            success=False,
            output="",
            errors="Execution cancelled by user",
            return_code=-1,
            duration=duration,
        )

    def execute(
        self,
        script_path: Path,
        args: Optional[list] = None,
        elevated: bool = True,
        timeout: int = 300,
    ) -> ExecutionResult:
        """Execute one batch script synchronously within this transaction."""
        import time

        start_time = time.time()
        logger.info(f"Executing batch script: {script_path}")

        if self._cancel_event.is_set():
            return self._cancelled_result()
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return ExecutionResult(
                success=False,
                output="",
                errors=f"Script not found: {script_path}",
                return_code=-1,
                duration=0,
            )

        # Refuse shell metacharacters before anything is spawned. cmd.exe would act
        # on them before the batch script could validate its own arguments. The
        # script path is checked too: it is the first token on the command line, so
        # a directory or filename containing '&' splits there just as an argument
        # would. Scripts ship with the app, but the discovery root is a filesystem
        # path and this is the boundary that hands it to cmd.exe.
        if not _argument_is_shell_safe(str(script_path)):
            logger.error(f"Refusing unsafe script path: {script_path!r}")
            return ExecutionResult(
                success=False,
                output="",
                errors="Refusing unsafe script path",
                return_code=-1,
                duration=0,
            )

        for argument in args or ():
            if not _argument_is_shell_safe(str(argument)):
                logger.error(f"Refusing unsafe batch argument: {argument!r}")
                return ExecutionResult(
                    success=False,
                    output="",
                    errors="Refusing unsafe batch argument",
                    return_code=-1,
                    duration=0,
                )

        # Validate before entering the spawn critical section. Cancellation during
        # validation remains set and is checked atomically immediately before Popen.
        from core.batch_parser import BatchParser

        try:
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
            logger.error(f"Could not validate script: {validation_err}")
            return ExecutionResult(
                success=False,
                output="",
                errors=f"Script validation failed: {validation_err}",
                return_code=-1,
                duration=0,
            )

        cmd = [str(script_path)]
        if args:
            cmd.extend(args)

        output_lines: list[str] = []
        error_lines: list[str] = []
        stdout_thread: Optional[threading.Thread] = None
        stderr_thread: Optional[threading.Thread] = None
        proc: Optional[subprocess.Popen] = None

        def read_stream(stream, is_error: bool = False) -> None:
            try:
                for line in iter(stream.readline, ""):
                    if not line:
                        break
                    line = line.rstrip()
                    if is_error:
                        error_lines.append(line)
                    else:
                        output_lines.append(line)
                    if self.on_output:
                        self.on_output(line)
                    logger.debug(f"{'[ERROR]' if is_error else '[OUTPUT]'} {line}")
            except (OSError, ValueError) as exc:
                logger.debug(f"Output stream closed: {exc}")

        def drain_reader_threads() -> None:
            for thread in (stdout_thread, stderr_thread):
                if thread is not None:
                    thread.join(timeout=10)

        try:
            startupinfo = None
            creation_flags = 0
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creation_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

            # The cancellation check, process creation, and handle publication are
            # one atomic operation. cancel() sets the event before taking this lock,
            # so it either prevents Popen or observes and terminates the new process.
            with self._state_lock:
                if self._cancel_event.is_set():
                    return self._cancelled_result(time.time() - start_time)
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=recovery_environment(),
                    creationflags=creation_flags,
                    startupinfo=startupinfo,
                )
                self.process = proc

            stdout_thread = threading.Thread(
                target=read_stream,
                args=(proc.stdout, False),
                daemon=True,
            )
            stderr_thread = threading.Thread(
                target=read_stream,
                args=(proc.stderr, True),
                daemon=True,
            )
            stdout_thread.start()
            stderr_thread.start()

            return_code = proc.wait(timeout=timeout)
            drain_reader_threads()
            duration = time.time() - start_time
            success = return_code == 0 and not self._cancel_event.is_set()
            logger.info(
                f"Script completed: {script_path} "
                f"(return code: {return_code}, duration: {duration:.2f}s)"
            )
            return ExecutionResult(
                success=success,
                output="\n".join(output_lines),
                errors="\n".join(error_lines),
                return_code=return_code,
                duration=duration,
            )
        except subprocess.TimeoutExpired:
            logger.error(f"Script timed out after {timeout}s: {script_path}")
            self._cancel_event.set()
            if proc is not None:
                self._terminate_process_tree(proc)
            drain_reader_threads()
            return ExecutionResult(
                success=False,
                output="\n".join(output_lines),
                errors=f"Script timed out after {timeout} seconds",
                return_code=-1,
                duration=timeout,
            )
        except Exception as exc:
            logger.exception(f"Error executing script: {script_path}")
            if proc is not None and proc.poll() is None:
                self._terminate_process_tree(proc)
            drain_reader_threads()
            return ExecutionResult(
                success=False,
                output="\n".join(output_lines),
                errors=str(exc),
                return_code=-1,
                duration=time.time() - start_time,
            )
        finally:
            if proc is not None:
                for stream in (proc.stdout, proc.stderr):
                    if stream is not None:
                        try:
                            stream.close()
                        except (OSError, ValueError):
                            pass
            drain_reader_threads()
            with self._state_lock:
                if self.process is proc:
                    self.process = None

    def execute_async(
        self,
        script_path: Path,
        on_complete: Optional[Callable[[ExecutionResult], None]] = None,
    ) -> None:
        """Execute a script asynchronously in a daemon thread."""

        def run() -> None:
            result = self.execute(script_path)
            if on_complete:
                on_complete(result)

        threading.Thread(target=run, daemon=True).start()

    def _terminate_process_tree(self, proc: subprocess.Popen) -> None:
        """Terminate the complete Windows process tree with bounded fallbacks."""
        if proc.poll() is not None:
            return
        if sys.platform == "win32" and getattr(proc, "pid", None):
            try:
                result = subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                if result.returncode == 0:
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
                    if proc.poll() is not None:
                        return
            except (OSError, subprocess.SubprocessError) as exc:
                logger.warning(f"Could not terminate process tree with taskkill: {exc}")

        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Process did not terminate — killing forcefully")
            proc.kill()
            try:
                proc.wait(timeout=5)
            except (OSError, subprocess.SubprocessError):
                pass
        except OSError as exc:
            logger.debug(f"Process already exited during cancellation: {exc}")

    def cancel(self) -> None:
        """Persistently cancel this transaction and terminate its active tree."""
        self._cancel_event.set()
        with self._state_lock:
            proc = self.process
        if proc is not None:
            logger.warning("Cancelling batch script execution")
            self._terminate_process_tree(proc)
