import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import agent_bridge  # noqa: E402


class FakePopen:
    calls = []

    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        self.kwargs = kwargs
        self.pid = 12345
        self.returncode = 0
        FakePopen.calls.append(self)

    def communicate(self, input=None, timeout=None):
        self.input = input
        self.timeout = timeout
        return ("ok", "")


def test_run_capture_detaches_child_stdin_on_windows(monkeypatch):
    FakePopen.calls = []
    monkeypatch.setattr(agent_bridge.sys, "platform", "win32")
    monkeypatch.setattr(agent_bridge, "wrap_command_for_runtime", lambda cmd, runtime, workdir=None: (cmd, None))
    monkeypatch.setattr(agent_bridge.subprocess, "Popen", FakePopen)

    cp = agent_bridge.run_capture(["opencode", "run", "prompt"], runtime="windows")

    assert cp.returncode == 0
    assert FakePopen.calls[0].kwargs["shell"] is True
    assert FakePopen.calls[0].kwargs["stdin"] is subprocess.DEVNULL


def test_run_live_detaches_child_stdin_on_windows(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(agent_bridge.sys, "platform", "win32")
    monkeypatch.setattr(agent_bridge, "wrap_command_for_runtime", lambda cmd, runtime, workdir=None: (cmd, None))
    monkeypatch.setattr(agent_bridge.subprocess, "run", fake_run)

    cp = agent_bridge.run_live(["opencode", "run", "prompt"], runtime="windows", workdir=None, timeout=60)

    assert cp.returncode == 0
    assert calls[0][1]["shell"] is True
    assert calls[0][1]["stdin"] is subprocess.DEVNULL


def test_codex_exec_prompt_uses_controlled_stdin(monkeypatch):
    FakePopen.calls = []
    monkeypatch.setattr(agent_bridge.sys, "platform", "win32")
    monkeypatch.setattr(agent_bridge, "wrap_command_for_runtime", lambda cmd, runtime, workdir=None: (cmd, None))
    monkeypatch.setattr(agent_bridge.subprocess, "Popen", FakePopen)

    agent_bridge.run_capture(["codex", "exec", "--sandbox", "read-only", "hello"], runtime="windows")

    assert FakePopen.calls[0].cmd == ["codex", "exec", "--sandbox", "read-only", "-"]
    assert FakePopen.calls[0].input == "hello"
    assert FakePopen.calls[0].kwargs["stdin"] == subprocess.PIPE


def test_codex_exec_option_is_not_treated_as_prompt(monkeypatch):
    FakePopen.calls = []
    monkeypatch.setattr(agent_bridge.sys, "platform", "win32")
    monkeypatch.setattr(agent_bridge, "wrap_command_for_runtime", lambda cmd, runtime, workdir=None: (cmd, None))
    monkeypatch.setattr(agent_bridge.subprocess, "Popen", FakePopen)

    agent_bridge.run_capture(["codex", "exec", "--help"], runtime="windows")

    assert FakePopen.calls[0].cmd == ["codex", "exec", "--help"]
    assert FakePopen.calls[0].kwargs["stdin"] is subprocess.DEVNULL
    assert FakePopen.calls[0].input is None


def test_run_capture_kills_process_tree_on_timeout(monkeypatch):
    class TimeoutPopen(FakePopen):
        def communicate(self, input=None, timeout=None):
            raise subprocess.TimeoutExpired(self.cmd, timeout, output="partial", stderr="late")

    killed = []
    FakePopen.calls = []
    monkeypatch.setattr(agent_bridge.sys, "platform", "win32")
    monkeypatch.setattr(agent_bridge, "wrap_command_for_runtime", lambda cmd, runtime, workdir=None: (cmd, None))
    monkeypatch.setattr(agent_bridge.subprocess, "Popen", TimeoutPopen)
    monkeypatch.setattr(agent_bridge, "terminate_process_tree", lambda pid: killed.append(pid))

    with pytest.raises(subprocess.TimeoutExpired) as exc:
        agent_bridge.run_capture(["codex", "exec", "hello"], runtime="windows", timeout=10)

    assert killed == [12345]
    assert exc.value.output == "partial"
    assert exc.value.stderr == "late"


def test_timeout_summary_includes_captured_partial_output():
    exc = subprocess.TimeoutExpired(["codex"], timeout=60, output="final answer\n", stderr="shutdown warning\n")

    summary = agent_bridge.timeout_summary(exc, limit=200)

    assert summary["timed_out_after"] == 60
    assert summary["partial_output_emitted"] is True
    assert "final answer" in summary["partial_output"]
    assert "shutdown warning" in summary["partial_output"]
