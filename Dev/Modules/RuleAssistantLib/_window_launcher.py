"""Subprocess launcher for PyQt6 Rule Assistant window"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Crash log
_crash_log = Path(__file__).parent / '_launcher_CRASH.log'

def log_crash(msg):
    """Write crash log"""
    try:
        with open(_crash_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {msg}\n")
            f.flush()
        print(f"[LOG] {msg}", file=sys.stderr)
    except:
        pass

print(f"[START] Launcher starting, PID={os.getpid()}", file=sys.stderr)
log_crash("[INIT] Launcher process starting")

# Setup Python path - add src_py's PARENT so that src_py becomes a package
src_py_dir = Path(__file__).parent
src_py_parent = src_py_dir.parent
sys.path.insert(0, str(src_py_parent))
log_crash(f"[PATH] Added to sys.path: {src_py_parent}")
log_crash(f"[PATH] src_py_dir: {src_py_dir}")

try:
    # Parse args
    log_crash("[ARGS] Parsing command-line arguments")
    parser = argparse.ArgumentParser()
    parser.add_argument('--rule-file', required=True)
    parser.add_argument('--flex-data-file', required=True)
    parser.add_argument('--test-data-file', required=True)
    parser.add_argument('--ui-lang-code', default='en')
    parser.add_argument('--result-file', required=True)
    parser.add_argument('--came-from-lrt', action='store_true')

    args = parser.parse_args()
    log_crash(f"[ARGS] Arguments parsed: result_file={args.result_file}")

    # Import Qt - this is where it might hang
    log_crash("[QT] About to import PyQt6")
    print("[IMPORT] Importing PyQt6...", file=sys.stderr)

    from PyQt6.QtWidgets import QApplication
    log_crash("[QT] PyQt6.QtWidgets imported successfully")
    print("[IMPORT] PyQt6 imported OK", file=sys.stderr)

    # Import window using package import (NOT relative import)
    # This ensures that relative imports within main_window.py work correctly
    log_crash("[WINDOW] About to import RuleAssistantWindow")
    print("[IMPORT] Importing RuleAssistantWindow...", file=sys.stderr)

    # Use absolute import from the src_py package
    import src_py.view.main_window as main_window_module
    RuleAssistantWindow = main_window_module.RuleAssistantWindow
    log_crash("[WINDOW] RuleAssistantWindow imported successfully")
    print("[IMPORT] RuleAssistantWindow imported OK", file=sys.stderr)

    # Create app
    log_crash("[QT] Creating QApplication")
    print("[QT] Creating QApplication...", file=sys.stderr)

    app = QApplication(sys.argv)
    log_crash("[QT] QApplication created")
    print("[QT] QApplication created OK", file=sys.stderr)

    # Create window
    log_crash(f"[WINDOW] Creating window with rule_file={args.rule_file}")
    print("[WINDOW] Creating RuleAssistantWindow...", file=sys.stderr)

    window = RuleAssistantWindow(
        rule_file=args.rule_file,
        flex_data_file=args.flex_data_file,
        test_data_file=args.test_data_file,
        came_from_lrt=args.came_from_lrt,
        ui_lang_code=args.ui_lang_code,
    )
    log_crash("[WINDOW] RuleAssistantWindow created")
    print("[WINDOW] Window created OK", file=sys.stderr)

    # Show and run
    log_crash("[SHOW] Calling window.show()")
    print("[SHOW] Showing window...", file=sys.stderr)

    window.show()
    log_crash("[SHOW] window.show() returned")
    print("[EXEC] Running app.exec()...", file=sys.stderr)

    log_crash("[EXEC] Starting app.exec()")
    print("[EXEC] Running event loop - window is open for 30 seconds...", file=sys.stderr)
    try:
        # Keep window open with QTimer-based approach to avoid exec() crash
        log_crash("[EXEC] Using timer-based window management")
        import time
        from PyQt6.QtCore import QEventLoop
        start_time = time.time()
        timeout_seconds = 30

        while time.time() - start_time < timeout_seconds:
            try:
                # Process all pending events so QWebEngineView can render HTML
                app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents)
                # Let Qt process any pending events without hanging
                if not window.isVisible():
                    log_crash("[EXEC] Window closed by user")
                    break
                # Simple sleep to avoid busy loop
                time.sleep(0.01)
            except Exception as loop_error:
                log_crash(f"[EXEC] Error in event loop: {loop_error}")
                break

        log_crash("[EXEC] Window timeout reached or closed")
        print("[EXEC] Event loop timeout - closing window", file=sys.stderr)
    except Exception as exec_error:
        log_crash(f"[EXEC] Event loop fatal error: {exec_error}")
        import traceback
        log_crash(traceback.format_exc())
        print(f"[EXEC] Event loop error: {exec_error}", file=sys.stderr)

    # Get and save result
    log_crash("[RESULT] Getting result from window")
    try:
        result = window.get_result()
        log_crash(f"[RESULT] Result: saved={result.saved}, rule_index={result.rule_index}, launch_lrt={result.launch_lrt}")

        result_data = {
            'saved': result.saved,
            'rule_index': result.rule_index,
            'launch_lrt': result.launch_lrt,
        }

        log_crash(f"[FILE] Writing to {args.result_file}")
        print(f"[FILE] Writing result to {args.result_file}...", file=sys.stderr)

        with open(args.result_file, 'w') as f:
            json.dump(result_data, f)
        log_crash("[FILE] Result written successfully")
        print("[SUCCESS] Result written, exiting normally", file=sys.stderr)
    except Exception as result_error:
        log_crash(f"[ERROR] Failed to get/write result: {result_error}")
        import traceback
        log_crash(traceback.format_exc())
        print(f"[ERROR] Failed to write result: {result_error}", file=sys.stderr)

    log_crash("[EXIT] Exiting normally")
    sys.exit(0)

except Exception as e:
    log_crash(f"[ERROR] Exception: {e}")
    import traceback
    log_crash(traceback.format_exc())

    print(f"[ERROR] {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)

    # Try to write error result
    try:
        result_data = {'saved': False, 'rule_index': None, 'launch_lrt': False}
        with open(args.result_file, 'w') as f:
            json.dump(result_data, f)
        log_crash("[FILE] Error result written")
    except:
        log_crash("[FILE] Failed to write error result")

    log_crash("[EXIT] Exiting with error")
    sys.exit(1)
