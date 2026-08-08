"""
Additional unit tests for BatchExecutor edge cases.

Covers: nonexistent scripts, args passing, cancel, timeout,
async callbacks, validation failures, and ExecutionResult dataclass.
"""

import pytest
import sys
import time
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.batch_executor import BatchExecutor, ExecutionResult


@pytest.mark.unit
class TestExecutionResult:
    """Test ExecutionResult dataclass behavior."""

    def test_fields_accessible(self):
        result = ExecutionResult(
            success=True, output="hello", errors="", return_code=0, duration=1.5
        )
        assert result.success is True
        assert result.output == "hello"
        assert result.errors == ""
        assert result.return_code == 0
        assert result.duration == 1.5

    def test_failure_result(self):
        result = ExecutionResult(
            success=False, output="", errors="bad", return_code=1, duration=0.2
        )
        assert result.success is False
        assert result.return_code == 1

    def test_result_with_multiline_output(self):
        result = ExecutionResult(
            success=True, output="line1\nline2\nline3", errors="", return_code=0, duration=0.5
        )
        assert result.output.count("\n") == 2


@pytest.mark.unit
class TestBatchExecutorInit:
    """Test BatchExecutor initialization."""

    def test_default_init(self):
        executor = BatchExecutor()
        assert executor.on_output is None
        assert executor.on_progress is None
        assert executor.process is None
        assert executor._cancelled is False

    def test_init_with_callbacks(self):
        output_cb = lambda line: None
        progress_cb = lambda pct: None
        executor = BatchExecutor(on_output=output_cb, on_progress=progress_cb)
        assert executor.on_output is output_cb
        assert executor.on_progress is progress_cb


@pytest.mark.unit
class TestExecuteNonexistentScript:
    """Test execute() with missing script files."""

    def test_execute_nonexistent_script(self, tmp_path):
        """Executing a nonexistent script returns failure result"""
        executor = BatchExecutor()
        result = executor.execute(tmp_path / "no_such_file.bat")
        assert result.success is False
        assert result.return_code == -1
        assert "not found" in result.errors.lower()
        assert result.duration == 0

    def test_execute_deeply_nested_nonexistent(self, tmp_path):
        """Deeply nested nonexistent path returns failure"""
        executor = BatchExecutor()
        result = executor.execute(tmp_path / "a" / "b" / "c" / "script.bat")
        assert result.success is False
        assert result.return_code == -1


@pytest.mark.unit
class TestExecuteWithArgs:
    """Test execute() passes arguments correctly."""

    def test_execute_with_args(self, tmp_path):
        """execute() passes args to subprocess"""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\necho %*\n")

        with patch("subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(side_effect=["output line", ""])
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(return_value="")
            proc.wait = MagicMock(return_value=0)
            mock_popen.return_value = proc

            executor = BatchExecutor()
            result = executor.execute(script, args=[":apply_all"])

            cmd = mock_popen.call_args[0][0]
            assert str(script) in cmd
            assert ":apply_all" in cmd

    def test_execute_without_args(self, tmp_path):
        """execute() works without args (cmd is just script path)"""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")

        with patch("subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(return_value="")
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(return_value="")
            proc.wait = MagicMock(return_value=0)
            mock_popen.return_value = proc

            executor = BatchExecutor()
            result = executor.execute(script)

            cmd = mock_popen.call_args[0][0]
            assert len(cmd) == 1  # Just the script path


@pytest.mark.unit
class TestCancel:
    """Test cancel() behavior."""

    def test_cancel_sets_flag(self):
        """cancel() sets _cancelled flag"""
        executor = BatchExecutor()
        assert executor._cancelled is False
        executor.cancel()
        assert executor._cancelled is True

    def test_cancel_with_no_process(self):
        """cancel() doesn't crash when no process is running"""
        executor = BatchExecutor()
        executor.cancel()  # Should not raise
        assert executor._cancelled is True

    def test_cancel_terminates_running_process_tree(self):
        """On Windows, cancel targets the complete process tree."""
        executor = BatchExecutor()
        proc = MagicMock(pid=4321)
        proc.poll.return_value = None
        executor.process = proc

        completed = MagicMock(returncode=0)
        with patch("core.batch_executor.sys.platform", "win32"), patch(
            "core.batch_executor.subprocess.run", return_value=completed
        ) as taskkill:
            executor.cancel()

        taskkill.assert_called_once()
        assert taskkill.call_args.args[0] == [
            "taskkill", "/PID", "4321", "/T", "/F"
        ]
        assert executor._cancelled is True

    def test_cancel_kills_if_tree_and_terminate_time_out(self):
        """Fallback kill is used when taskkill fails and terminate times out."""
        import subprocess

        executor = BatchExecutor()
        proc = MagicMock(pid=4321)
        proc.poll.return_value = None
        proc.wait.side_effect = [
            subprocess.TimeoutExpired(cmd="test", timeout=5),
            None,
        ]
        executor.process = proc

        with patch("core.batch_executor.sys.platform", "win32"), patch(
            "core.batch_executor.subprocess.run",
            return_value=MagicMock(returncode=1),
        ):
            executor.cancel()

        proc.terminate.assert_called_once()
        proc.kill.assert_called_once()

    def test_cancel_during_spawn_observes_published_process(self, tmp_path):
        """Cancellation requested inside Popen's critical section sees the process."""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")
        executor = BatchExecutor()
        popen_entered = threading.Event()
        allow_popen_return = threading.Event()
        terminated = threading.Event()
        proc = MagicMock(pid=4321)
        proc.stdout.readline.return_value = ""
        proc.stderr.readline.return_value = ""
        proc.poll.return_value = None
        proc.wait.side_effect = lambda timeout=None: (
            terminated.wait(2) and -1
        )

        def blocking_popen(*args, **kwargs):
            popen_entered.set()
            assert allow_popen_return.wait(2)
            return proc

        def terminate_tree(candidate):
            assert candidate is proc
            terminated.set()

        with patch("core.batch_executor.subprocess.Popen", side_effect=blocking_popen), patch.object(
            executor, "_terminate_process_tree", side_effect=terminate_tree
        ) as terminate:
            result_holder = []
            execute_thread = threading.Thread(
                target=lambda: result_holder.append(executor.execute(script))
            )
            execute_thread.start()
            assert popen_entered.wait(2)

            cancel_thread = threading.Thread(target=executor.cancel)
            cancel_thread.start()
            assert executor._cancel_event.wait(2)
            allow_popen_return.set()

            cancel_thread.join(2)
            execute_thread.join(2)

        assert not cancel_thread.is_alive()
        assert not execute_thread.is_alive()
        terminate.assert_called_once_with(proc)
        assert result_holder[0].success is False
        assert executor.process is None


@pytest.mark.unit
class TestExecuteCancelledFlag:
    """Cancellation persists for the lifetime of one executor transaction."""

    def test_pre_cancelled_executor_refuses_to_spawn(self, tmp_path):
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")
        executor = BatchExecutor()
        executor.cancel()

        with patch("subprocess.Popen") as mock_popen:
            result = executor.execute(script)

        assert executor._cancelled is True
        assert result.success is False
        assert "cancelled" in result.errors.lower()
        mock_popen.assert_not_called()


@pytest.mark.unit
class TestExecuteAsync:
    """Test execute_async() behavior."""

    def test_execute_async_calls_callback(self, tmp_path):
        """execute_async calls on_complete callback"""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")

        with patch("subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(return_value="")
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(return_value="")
            proc.wait = MagicMock(return_value=0)
            mock_popen.return_value = proc

            callback_results = []
            executor = BatchExecutor()
            executor.execute_async(script, on_complete=lambda r: callback_results.append(r))

            # Wait for the daemon thread to complete
            time.sleep(1.0)

            assert len(callback_results) == 1
            assert callback_results[0].success is True

    def test_execute_async_without_callback(self, tmp_path):
        """execute_async works without on_complete callback"""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")

        with patch("subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(return_value="")
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(return_value="")
            proc.wait = MagicMock(return_value=0)
            mock_popen.return_value = proc

            executor = BatchExecutor()
            executor.execute_async(script)  # No callback

            time.sleep(0.5)
            # Should not raise


@pytest.mark.unit
class TestExecuteTimeout:
    """Test timeout handling."""

    def test_execute_timeout_returns_failure(self, tmp_path):
        """Script that times out returns failure result"""
        import subprocess

        script = tmp_path / "slow.bat"
        script.write_text("@echo off\n")

        with patch("subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(return_value="")
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(return_value="")
            proc.wait = MagicMock(side_effect=subprocess.TimeoutExpired(cmd="slow.bat", timeout=1))
            proc.stdout.close = MagicMock()
            proc.stderr.close = MagicMock()
            proc.terminate = MagicMock()
            mock_popen.return_value = proc

            executor = BatchExecutor()
            result = executor.execute(script, timeout=1)

            assert result.success is False
            assert "timed out" in result.errors.lower()
            assert result.return_code == -1
            assert result.duration == 1


@pytest.mark.unit
class TestExecuteSubprocessError:
    """Test execute() when subprocess raises unexpected errors."""

    def test_execute_generic_exception(self, tmp_path):
        """Generic exception during execution returns failure"""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")

        with patch("subprocess.Popen", side_effect=OSError("spawn error")):
            executor = BatchExecutor()
            result = executor.execute(script)

            assert result.success is False
            assert result.return_code == -1
            assert "spawn error" in result.errors

    def test_execute_with_on_output_callback(self, tmp_path):
        """on_output callback receives output lines"""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")

        with patch("subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(side_effect=["hello world", ""])
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(return_value="")
            proc.wait = MagicMock(return_value=0)
            mock_popen.return_value = proc

            output_lines = []
            executor = BatchExecutor(on_output=lambda line: output_lines.append(line))
            result = executor.execute(script)

            assert "hello world" in output_lines

    def test_execute_receives_stderr(self, tmp_path):
        """stderr lines are captured in error output"""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")

        with patch("subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(return_value="")
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(side_effect=["error occurred", ""])
            proc.wait = MagicMock(return_value=0)
            mock_popen.return_value = proc

            executor = BatchExecutor()
            result = executor.execute(script)

            assert "error occurred" in result.errors

    def test_execute_drains_reader_threads_before_building_result(self, tmp_path):
        """Output consumed during reader-thread join must be present in the result."""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")

        class DeferredThread:
            def __init__(self, target, args, daemon):
                self.target = target
                self.args = args
                self.ran = False

            def start(self):
                pass

            def join(self, timeout=None):
                if not self.ran:
                    self.ran = True
                    self.target(*self.args)

        proc = MagicMock()
        proc.stdout.readline = MagicMock(side_effect=["late stdout", ""])
        proc.stderr.readline = MagicMock(side_effect=["late stderr", ""])
        proc.wait.return_value = 0

        with patch("core.batch_executor.subprocess.Popen", return_value=proc), patch(
            "core.batch_executor.threading.Thread", DeferredThread
        ):
            result = BatchExecutor().execute(script)

        assert result.output == "late stdout"
        assert result.errors == "late stderr"


@pytest.mark.unit
class TestExecuteValidation:
    """Test script safety validation before execution."""

    def test_execute_script_validation_exception_handled(self, tmp_path):
        """If validation raises, executor fails closed before process launch."""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\necho test\n")

        with patch("subprocess.Popen") as mock_popen, \
             patch("core.batch_parser.BatchParser") as MockParser:
            MockParser.side_effect = Exception("parser crash")

            executor = BatchExecutor()
            result = executor.execute(script)

            assert result.success is False
            assert result.return_code == -1
            assert "validation failed" in result.errors.lower()
            mock_popen.assert_not_called()

    def test_execute_reuse_after_cancel_is_rejected(self, tmp_path):
        """A cancelled transaction cannot silently spawn a later script."""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")
        executor = BatchExecutor()
        executor.cancel()

        with patch("subprocess.Popen") as mock_popen:
            result = executor.execute(script)

        assert executor._cancelled is True
        assert result.success is False
        assert "cancelled" in result.errors.lower()
        mock_popen.assert_not_called()


@pytest.mark.unit
class TestRecoveryRootPinning:
    """The batch engine must write recovery artifacts where the GUI reads them."""

    def test_recovery_environment_pins_backups_dir_to_writable_root(self):
        from core.batch_executor import recovery_environment
        from core.paths import backup_dir

        environment = recovery_environment()
        assert Path(environment["BACKUPS_DIR"]) == backup_dir()

    def test_execute_passes_backups_dir_to_the_batch_process(self, tmp_path):
        from core.paths import backup_dir

        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")

        with patch("core.batch_executor.subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(return_value="")
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(return_value="")
            proc.wait = MagicMock(return_value=0)
            mock_popen.return_value = proc

            BatchExecutor().execute(script)

            environment = mock_popen.call_args.kwargs["env"]
            assert Path(environment["BACKUPS_DIR"]) == backup_dir()


@pytest.mark.unit
class TestBatchArgumentInjection:
    """cmd.exe acts on shell metacharacters before a .bat can validate its args.

    The app runs elevated, so an argument carrying '&' would execute its tail with
    administrator privileges. Arguments are refused, not escaped.
    """

    @staticmethod
    def _probe_script(tmp_path):
        script = tmp_path / "probe.bat"
        script.write_text("@echo off\r\necho ARG=[%~1]\r\n", encoding="utf-8")
        return script

    @pytest.mark.parametrize(
        "hostile",
        [
            "a&whoami",
            'x"&calc&"y',
            "a|b",
            "a>out.txt",
            "a<in.txt",
            "a^b",
            "a\nb",
        ],
    )
    def test_shell_metacharacter_argument_is_refused_before_spawn(
        self, tmp_path, hostile
    ):
        script = self._probe_script(tmp_path)
        with patch("core.batch_executor.subprocess.Popen") as mock_popen:
            result = BatchExecutor().execute(script, args=[hostile])

        assert result.success is False
        assert result.errors == "Refusing unsafe batch argument"
        assert mock_popen.call_count == 0, "process must never be spawned"

    @pytest.mark.parametrize(
        "legitimate", ["restore_from_backup", "create_snapshot", ":apply_all", "2026-08-04_10-00-00"]
    )
    def test_legitimate_arguments_still_execute(self, tmp_path, legitimate):
        script = self._probe_script(tmp_path)
        with patch("core.batch_executor.subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(return_value="")
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(return_value="")
            proc.wait = MagicMock(return_value=0)
            mock_popen.return_value = proc

            BatchExecutor().execute(script, args=[legitimate])

        assert mock_popen.call_count == 1
        assert legitimate in mock_popen.call_args[0][0]


@pytest.mark.unit
class TestScriptPathInjection:
    """The script path is the first token on the command line, so it splits too."""

    def test_script_path_with_metacharacter_is_refused(self, tmp_path):
        script = tmp_path / "probe&whoami.bat"
        script.write_text("@echo off\r\n", encoding="utf-8")

        with patch("core.batch_executor.subprocess.Popen") as mock_popen:
            result = BatchExecutor().execute(script)

        assert result.success is False
        assert result.errors == "Refusing unsafe script path"
        assert mock_popen.call_count == 0

    def test_ordinary_script_path_is_unaffected(self, tmp_path):
        script = tmp_path / "probe.bat"
        script.write_text("@echo off\r\n", encoding="utf-8")

        with patch("core.batch_executor.subprocess.Popen") as mock_popen:
            proc = MagicMock()
            proc.stdout = MagicMock()
            proc.stdout.readline = MagicMock(return_value="")
            proc.stderr = MagicMock()
            proc.stderr.readline = MagicMock(return_value="")
            proc.wait = MagicMock(return_value=0)
            mock_popen.return_value = proc

            BatchExecutor().execute(script)

        assert mock_popen.call_count == 1
