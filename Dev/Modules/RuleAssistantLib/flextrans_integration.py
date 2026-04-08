"""Integration point for FlexTools RuleAssistant module

This module provides the StartRuleAssistant function that RuleAssistant.py
in FlexTools calls to launch the PyQt6 Rule Assistant window as a subprocess.
"""

import sys
import os
import subprocess
import json
import tempfile
import logging
from typing import Optional
from datetime import datetime

# Fallback crash log - writes directly to file if logging fails
_crash_log = os.path.join(os.path.dirname(__file__), 'flextrans_CRASH.log')

def _write_crash_log(msg):
    """Direct file write as fallback if logging fails"""
    try:
        with open(_crash_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {msg}\n")
            f.flush()
    except:
        pass

_write_crash_log("[INIT] flextrans_integration.py loading (subprocess mode)")

# Setup logging
import tempfile
_log_file = os.path.join(tempfile.gettempdir(), 'flextrans_integration.log')

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# Remove any existing handlers to avoid duplicates
for handler in _logger.handlers[:]:
    _logger.removeHandler(handler)

try:
    _file_handler = logging.FileHandler(_log_file, mode='w')
    _file_handler.setLevel(logging.DEBUG)
    _file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    _logger.addHandler(_file_handler)

    _console_handler = logging.StreamHandler(sys.stderr)
    _console_handler.setLevel(logging.DEBUG)
    _console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    _logger.addHandler(_console_handler)

    _logger.propagate = True
except Exception as e:
    print(f"WARNING: Failed to setup logging: {e}", file=sys.stderr)

_logger.info("flextrans_integration.py loaded (subprocess mode)")
_logger.info(f"Log file: {_log_file}")


def start_rule_assistant(
    rule_file: str,
    flex_data_file: str,
    test_data_file: str,
    came_from_lrt: bool = False,
    ui_lang_code: str = "en"
) -> tuple[bool, Optional[int], bool]:
    """Launch the Rule Assistant window as a subprocess.

    This is called by RuleAssistant.py in the FlexTools environment.
    The window runs in a separate process to avoid event loop conflicts.

    Args:
        rule_file: Path to rule XML file (read/write)
        flex_data_file: Path to FLEx metadata XML file (read)
        test_data_file: Path to test data HTML file (read)
        came_from_lrt: Whether launched from Live Rule Tester
        ui_lang_code: UI language code ("en", "fr", "es", "de")

    Returns:
        Tuple of (saved: bool, rule_index: Optional[int], launch_lrt: bool)
        - saved: True if user saved rules
        - rule_index: Index of rule to generate, or None if generate all or none
        - launch_lrt: True if user wants to launch Live Rule Tester afterwards
    """
    _write_crash_log("[START] start_rule_assistant() called")
    _logger.info("=" * 80)
    _logger.info("start_rule_assistant() called (subprocess mode)")
    _logger.info("=" * 80)
    _logger.info(f"  rule_file: {rule_file}")
    _logger.info(f"  flex_data_file: {flex_data_file}")
    _logger.info(f"  test_data_file: {test_data_file}")
    _logger.info(f"  came_from_lrt: {came_from_lrt}")
    _logger.info(f"  ui_lang_code: {ui_lang_code}")

    try:
        # Build command to launch subprocess
        # We'll launch a separate Python script that creates and shows the window
        _write_crash_log("[SUBPROCESS] Building subprocess command")

        # Get the path to the window launcher script
        src_py_dir = os.path.dirname(os.path.abspath(__file__))
        launcher_script = os.path.join(src_py_dir, '_window_launcher.py')

        # Verify launcher script exists
        if not os.path.exists(launcher_script):
            raise FileNotFoundError(f"Launcher script not found: {launcher_script}")
        _write_crash_log(f"[SUBPROCESS] Launcher script exists: {launcher_script}")

        # Use Python executable from sys.executable
        python_exe = sys.executable
        _logger.info(f"Python executable: {python_exe}")
        _logger.info(f"Launcher script: {launcher_script}")
        _write_crash_log(f"[SUBPROCESS] Python exe: {python_exe}")

        # Create temp files for result and subprocess output
        result_file = os.path.join(tempfile.gettempdir(), f'rule_assistant_result_{os.getpid()}_{int(os.urandom(4).hex(), 16)}.json')
        subprocess_log = os.path.join(os.path.dirname(__file__), '_launcher_subprocess.log')
        _logger.info(f"Result file: {result_file}")
        _logger.info(f"Subprocess log: {subprocess_log}")
        _write_crash_log(f"[SUBPROCESS] Result file: {result_file}")
        _write_crash_log(f"[SUBPROCESS] Subprocess log: {subprocess_log}")

        # Build command with arguments
        cmd = [
            python_exe,
            launcher_script,
            '--rule-file', rule_file,
            '--flex-data-file', flex_data_file,
            '--test-data-file', test_data_file,
            '--ui-lang-code', ui_lang_code,
            '--result-file', result_file,
        ]

        if came_from_lrt:
            cmd.append('--came-from-lrt')

        _write_crash_log(f"[SUBPROCESS] Full command:")
        for i, arg in enumerate(cmd):
            _write_crash_log(f"[SUBPROCESS]   arg[{i}]: {arg}")
        _logger.info(f"Launching subprocess: {python_exe} {launcher_script}")

        # Set environment variable to tell subprocess it has an isolated Qt event loop
        # RULE_ASSISTANT_STANDALONE=1 means: running as a subprocess with clean event loop
        # (prevents Qt conflicts, even though it's still "launched FROM" FlexTools)
        env = os.environ.copy()
        env['RULE_ASSISTANT_STANDALONE'] = '1'
        _write_crash_log("[SUBPROCESS] Set RULE_ASSISTANT_STANDALONE=1")

        # Launch subprocess and wait for it to complete
        _write_crash_log("[SUBPROCESS] Calling subprocess.run()")
        _logger.info("About to call subprocess.run()...")

        # Redirect stderr to file so we can see subprocess errors
        _write_crash_log(f"[SUBPROCESS] Redirecting stderr to {subprocess_log}")
        with open(subprocess_log, 'w') as log_handle:
            result = subprocess.run(
                cmd,
                timeout=300,
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                env=env,
            )
        _write_crash_log(f"[SUBPROCESS] subprocess.run() returned with code {result.returncode}")
        _logger.info(f"subprocess.run() returned with code {result.returncode}")

        # Read and log subprocess output
        try:
            with open(subprocess_log, 'r') as f:
                output = f.read()
            if output:
                _write_crash_log(f"[SUBPROCESS] Output:\n{output}")
                _logger.info(f"Subprocess output:\n{output}")
        except Exception as e:
            _write_crash_log(f"[SUBPROCESS] Failed to read log: {e}")

        # Read result from file
        if os.path.exists(result_file):
            _write_crash_log("[RESULT] Reading result from file")
            try:
                with open(result_file, 'r') as f:
                    result_data = json.load(f)

                saved = result_data.get('saved', False)
                rule_index = result_data.get('rule_index', None)
                launch_lrt = result_data.get('launch_lrt', False)

                _logger.info(f"Result from subprocess: saved={saved}, rule_index={rule_index}, launch_lrt={launch_lrt}")
                _write_crash_log(f"[RESULT] saved={saved}, rule_index={rule_index}, launch_lrt={launch_lrt}")

                # Clean up result file
                try:
                    os.remove(result_file)
                except:
                    pass

                _write_crash_log("[END] Returning result")
                return (saved, rule_index, launch_lrt)
            except Exception as e:
                _logger.error(f"Failed to read result file: {e}")
                _write_crash_log(f"[ERROR] Failed to read result file: {e}")
                # Return default (not saved)
                return (False, None, False)
        else:
            _logger.error(f"Result file not created: {result_file}")
            _write_crash_log(f"[ERROR] Result file not created: {result_file}")
            # Return default (not saved)
            return (False, None, False)

    except Exception as e:
        import traceback
        _logger.error(f"EXCEPTION in start_rule_assistant: {str(e)}")
        _logger.error(traceback.format_exc())
        _write_crash_log(f"[ERROR] Exception: {str(e)}")
        raise
