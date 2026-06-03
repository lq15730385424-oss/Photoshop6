#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ALIASES = {
    'claude': 'claude',
    'claude-code': 'claude',
    'codex': 'codex',
    'openai-codex': 'codex',
    'gemini': 'gemini',
    'gemini-cli': 'gemini',
    'opencode': 'opencode',
    'qwen': 'qwen',
    'qwencode': 'qwen',
    'qwen-code': 'qwen',
    'qwen-code-cli': 'qwen',
    'copilot': 'copilot',
    'github-copilot': 'copilot',
    'gh-copilot': 'copilot',
}

DEFAULT_AGENT_ORDER = ['claude', 'codex', 'gemini', 'opencode', 'qwen', 'copilot']

AGENTS: Dict[str, Dict[str, object]] = {
    'claude': {
        'binary': 'claude',
        'version_cmd': ['claude', '--version'],
        'check_cmd': ['claude', 'auth', 'status', '--text'],
        'smoke_cmd': ['claude', '-p', 'Respond with exactly: CLAUDE_SMOKE_OK', '--output-format', 'text', '--permission-mode', 'plan', '--no-session-persistence'],
        'smoke_token': 'CLAUDE_SMOKE_OK',
        'note': 'Claude Code print mode is preferred for bounded delegation.',
    },
    'codex': {
        'binary': 'codex',
        'version_cmd': ['codex', '--version'],
        'check_cmd': ['codex', 'exec', '--help'],
        'smoke_cmd': ['codex', 'exec', '--skip-git-repo-check', '--sandbox', 'read-only', 'Respond with exactly: CODEX_SMOKE_OK'],
        'smoke_token': 'CODEX_SMOKE_OK',
        'note': 'Codex non-interactive exec is the default; keep --skip-git-repo-check for non-repo work.',
    },
    'gemini': {
        'binary': 'gemini',
        'version_cmd': ['gemini', '--version'],
        'check_cmd': ['gemini', '--help'],
        'smoke_cmd': ['gemini', '-p', 'Respond with exactly: GEMINI_SMOKE_OK'],
        'smoke_token': 'GEMINI_SMOKE_OK',
        'note': 'Gemini -p is the preferred bounded mode.',
    },
    'opencode': {
        'binary': 'opencode',
        'version_cmd': ['opencode', '--version'],
        'check_cmd': ['opencode', 'auth', 'list'],
        'smoke_cmd': ['opencode', 'run', 'Respond with exactly: OPENCODE_SMOKE_OK'],
        'smoke_token': 'OPENCODE_SMOKE_OK',
        'note': 'OpenCode run is the preferred bounded mode.',
    },
    'qwen': {
        'binary': 'qwen',
        'version_cmd': ['qwen', '--version'],
        'check_cmd': ['qwen', 'auth', 'status'],
        'smoke_cmd': ['qwen', 'Respond with exactly: QWEN_SMOKE_OK', '--output-format', 'text'],
        'smoke_token': 'QWEN_SMOKE_OK',
        'note': 'Use positional prompts for one-shot Qwen runs.',
    },
    'copilot': {
        'binary': 'copilot',
        'version_cmd': ['copilot', '--version'],
        'note': 'Stay inside the selected runtime. Prefer direct copilot there; use same-runtime gh copilot only if direct copilot is unavailable there.',
    },
}

WINDOWS_PATH_RE = re.compile(r'^(?P<drive>[a-zA-Z]):[\\/](?P<rest>.*)$')
MNT_PATH_RE = re.compile(r'^/mnt/(?P<drive>[a-zA-Z])/(?P<rest>.*)$')


@dataclass
class WorkdirContext:
    host_runtime: str
    target_runtime: str
    host_path: Path
    target_path: str


def is_wsl() -> bool:
    if os.environ.get('WSL_DISTRO_NAME'):
        return True
    if os.name == 'nt':
        return False
    try:
        return 'microsoft' in Path('/proc/sys/kernel/osrelease').read_text().lower()
    except Exception:
        return False


def current_runtime() -> str:
    if os.name == 'nt':
        return 'windows'
    if is_wsl():
        return 'wsl'
    return 'linux'


def default_target_runtime() -> str:
    runtime = current_runtime()
    if runtime == 'windows':
        return 'windows'
    if runtime == 'wsl':
        return 'wsl'
    return 'linux'


def ps_quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def canonical_agent(name: str) -> str:
    key = name.strip().lower()
    if key not in ALIASES:
        raise SystemExit(f'Unknown agent {name!r}. Known names: {", ".join(sorted(ALIASES))}')
    return ALIASES[key]


def effective_runtime(requested: str) -> str:
    requested = requested.strip().lower()
    host = current_runtime()
    if requested == 'current':
        return default_target_runtime()
    if requested == 'windows':
        if host == 'windows' or shutil.which('powershell.exe'):
            return 'windows'
        raise SystemExit('Windows runtime requested but powershell.exe is not available from this host runtime.')
    if requested == 'wsl':
        if host == 'wsl' or shutil.which('wsl.exe'):
            return 'wsl'
        raise SystemExit('WSL runtime requested but wsl.exe is not available from this host runtime.')
    raise SystemExit(f'Unsupported runtime policy: {requested}')


def windows_to_wsl_path(raw: str) -> Optional[str]:
    match = WINDOWS_PATH_RE.match(raw.strip())
    if not match:
        return None
    drive = match.group('drive').lower()
    rest = match.group('rest').replace('\\', '/').lstrip('/')
    return f'/mnt/{drive}/{rest}' if rest else f'/mnt/{drive}'


def wsl_to_windows_path(path: Path) -> Optional[str]:
    match = MNT_PATH_RE.match(str(path))
    if not match:
        return None
    drive = match.group('drive').upper()
    rest = match.group('rest').replace('/', '\\')
    return f'{drive}:\\{rest}' if rest else f'{drive}:\\'


def normalize_host_path(raw: str) -> Path:
    host = current_runtime()
    raw = raw.strip()
    if host == 'windows':
        match = MNT_PATH_RE.match(raw)
        if match:
            drive = match.group('drive').upper()
            rest = match.group('rest').replace('/', '\\')
            raw = f'{drive}:\\{rest}' if rest else f'{drive}:\\'
        return Path(raw).expanduser().resolve()
    converted = windows_to_wsl_path(raw)
    if converted:
        raw = converted
    return Path(raw).expanduser().resolve()


def resolve_workdir(raw: str, target_runtime: str) -> WorkdirContext:
    host = current_runtime()
    host_path = normalize_host_path(raw)
    if target_runtime == 'windows':
        if host == 'windows':
            target_path = str(host_path)
        else:
            target_path = wsl_to_windows_path(host_path)
            if not target_path:
                raise SystemExit(f'Path {host_path} has no Windows translation. Use a path under /mnt/<drive>/... for Windows runtime execution.')
    elif target_runtime in {'wsl', 'linux'}:
        if host == 'windows':
            target_path = windows_to_wsl_path(str(host_path))
            if not target_path:
                raise SystemExit(f'Path {host_path} has no WSL translation.')
        else:
            target_path = str(host_path)
    else:
        raise SystemExit(f'Unsupported target runtime: {target_runtime}')
    return WorkdirContext(host_runtime=host, target_runtime=target_runtime, host_path=host_path, target_path=target_path)


def summarize_output(cp: subprocess.CompletedProcess, limit: int = 800) -> str:
    text = '\n'.join(part for part in [(cp.stdout or '').strip(), (cp.stderr or '').strip()] if part).strip()
    return text[:limit]


def _text_from_timeout_part(part: object) -> str:
    if part is None:
        return ''
    if isinstance(part, bytes):
        return part.decode('utf-8', errors='replace')
    return str(part)


def timeout_summary(exc: subprocess.TimeoutExpired, limit: int = 4000) -> dict:
    partial = '\n'.join(
        part.strip()
        for part in [
            _text_from_timeout_part(getattr(exc, 'output', None)),
            _text_from_timeout_part(getattr(exc, 'stderr', None)),
        ]
        if part and part.strip()
    ).strip()
    return {
        'timed_out_after': exc.timeout,
        'partial_output_emitted': bool(partial),
        'partial_output': partial[:limit],
    }


def windows_command_source(name: str) -> Optional[str]:
    ps = shutil.which('powershell.exe') or shutil.which('powershell')
    if not ps:
        return None
    script = f"& {{ $cmd = Get-Command {ps_quote(name)} -ErrorAction SilentlyContinue; if ($cmd) {{ Write-Output $cmd.Source }} }}"
    try:
        cp = subprocess.run([ps, '-NoProfile', '-Command', script], capture_output=True, text=True, timeout=20)
        lines = (cp.stdout or '').strip().splitlines()
        return lines[0].strip() if cp.returncode == 0 and lines else None
    except Exception:
        return None


def wsl_command_source(name: str) -> Optional[str]:
    wsl = shutil.which('wsl.exe')
    if not wsl:
        return None
    try:
        cp = subprocess.run([wsl, 'bash', '-lc', f'command -v {shlex.quote(name)}'], capture_output=True, text=True, timeout=20)
        lines = (cp.stdout or '').strip().splitlines()
        return lines[0].strip() if cp.returncode == 0 and lines else None
    except Exception:
        return None


def runtime_command_source(name: str, runtime: str) -> Optional[str]:
    host = current_runtime()
    native = default_target_runtime()
    if runtime == native:
        return shutil.which(name)
    if host == 'wsl' and runtime == 'windows':
        return windows_command_source(name)
    if host == 'windows' and runtime == 'wsl':
        return wsl_command_source(name)
    return None


def build_windows_wrapper(native_cmd: List[str], workdir: Optional[str]) -> List[str]:
    script_parts: List[str] = []
    if workdir:
        script_parts.append(f'Set-Location {ps_quote(workdir)}')
    script_parts.append('& ' + ' '.join(ps_quote(arg) for arg in native_cmd))
    return ['powershell.exe', '-NoProfile', '-Command', '& { ' + '; '.join(script_parts) + ' }']


def build_wsl_wrapper(native_cmd: List[str], workdir: Optional[str]) -> List[str]:
    command = ''
    if workdir:
        command += f'cd {shlex.quote(workdir)} && '
    command += ' '.join(shlex.quote(arg) for arg in native_cmd)
    return ['wsl.exe', 'bash', '-lc', command]


def wrap_command_for_runtime(native_cmd: List[str], runtime: str, workdir: Optional[WorkdirContext] = None) -> Tuple[List[str], Optional[str]]:
    host = current_runtime()
    native = default_target_runtime()
    if runtime == native:
        return native_cmd, str(workdir.host_path) if workdir else None
    if host == 'wsl' and runtime == 'windows':
        return build_windows_wrapper(native_cmd, workdir.target_path if workdir else None), None
    if host == 'windows' and runtime == 'wsl':
        return build_wsl_wrapper(native_cmd, workdir.target_path if workdir else None), None
    raise SystemExit(f'Cross-runtime execution from {host} to {runtime} is not supported here.')


def prepare_subprocess_command(native_cmd: List[str]) -> Tuple[List[str], Optional[str]]:
    if len(native_cmd) >= 3 and native_cmd[0] == 'codex' and native_cmd[1] == 'exec' and native_cmd[-1] != '-' and not native_cmd[-1].startswith('-'):
        prompt = native_cmd[-1]
        return native_cmd[:-1] + ['-'], prompt
    return native_cmd, None


def terminate_process_tree(pid: int) -> None:
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, text=True)
        return
    try:
        os.kill(pid, 15)
    except OSError:
        pass


def run_capture(native_cmd: List[str], runtime: str, workdir: Optional[WorkdirContext] = None, timeout: int = 30) -> subprocess.CompletedProcess:
    native_cmd, controlled_input = prepare_subprocess_command(native_cmd)
    wrapped_cmd, cwd = wrap_command_for_runtime(native_cmd, runtime, workdir)
    # Detach stdin so agent CLIs do not append the wrapper's input stream to the prompt.
    # Keep shell=True on Windows because npm .CMD shims are not reliably executable via CreateProcess.
    use_shell = sys.platform == 'win32'
    stdin_value = subprocess.PIPE if controlled_input is not None else subprocess.DEVNULL
    proc = subprocess.Popen(
        wrapped_cmd,
        cwd=cwd,
        stdin=stdin_value,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        shell=use_shell,
    )
    try:
        stdout, stderr = proc.communicate(input=controlled_input, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        terminate_process_tree(proc.pid)
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            stdout = _text_from_timeout_part(exc.output)
            stderr = _text_from_timeout_part(exc.stderr)
        exc.output = stdout if stdout is not None else _text_from_timeout_part(exc.output)
        exc.stderr = stderr if stderr is not None else _text_from_timeout_part(exc.stderr)
        raise
    return subprocess.CompletedProcess(wrapped_cmd, proc.returncode, stdout=stdout, stderr=stderr)


def run_live(native_cmd: List[str], runtime: str, workdir: Optional[WorkdirContext], timeout: Optional[int]) -> subprocess.CompletedProcess:
    native_cmd, controlled_input = prepare_subprocess_command(native_cmd)
    wrapped_cmd, cwd = wrap_command_for_runtime(native_cmd, runtime, workdir)
    # Detach stdin so agent CLIs do not append the wrapper's input stream to the prompt.
    # Keep shell=True on Windows because npm .CMD shims are not reliably executable via CreateProcess.
    use_shell = sys.platform == 'win32'
    stdin_arg = {} if controlled_input is not None else {'stdin': subprocess.DEVNULL}
    return subprocess.run(wrapped_cmd, cwd=cwd, input=controlled_input, text=True, encoding='utf-8', **stdin_arg, timeout=timeout, shell=use_shell)


def resolve_copilot_runner(runtime: str) -> dict:
    direct = runtime_command_source('copilot', runtime)
    if direct:
        return {
            'mode': 'direct',
            'binary': 'copilot',
            'path': direct,
            'note': f'Using direct copilot inside {runtime}.',
        }
    gh = runtime_command_source('gh', runtime)
    if gh:
        return {
            'mode': 'gh',
            'binary': 'gh copilot',
            'path': gh,
            'note': f'Falling back to same-runtime gh copilot inside {runtime} because direct copilot is unavailable there.',
        }
    return {
        'mode': 'missing',
        'binary': 'copilot',
        'path': None,
        'note': f'No direct copilot or gh fallback found inside {runtime}.',
    }


def copilot_native_command(runtime: str, base_args: List[str]) -> List[str]:
    runner = resolve_copilot_runner(runtime)
    if runner['mode'] == 'direct':
        return ['copilot'] + base_args
    if runner['mode'] == 'gh':
        return ['gh', 'copilot', '--'] + base_args
    return ['copilot'] + base_args


def detect(agent: str, runtime: str) -> dict:
    info = AGENTS[agent]
    meta = {
        'agent': agent,
        'aliases': sorted([alias for alias, canon in ALIASES.items() if canon == agent]),
        'host_runtime': current_runtime(),
        'target_runtime': runtime,
        'cross_runtime': runtime != default_target_runtime(),
        'note': info['note'],
    }
    if agent == 'copilot':
        runner = resolve_copilot_runner(runtime)
        version = None
        if runner['path']:
            try:
                cp = run_capture(copilot_native_command(runtime, ['--version']), runtime=runtime, timeout=20)
                version = summarize_output(cp, limit=200)
            except Exception as exc:
                version = f'version check failed: {exc}'
        return {
            **meta,
            'binary': runner['binary'],
            'path': runner['path'],
            'installed': bool(runner['path']),
            'version': version,
            'runner_mode': runner['mode'],
            'runner_note': runner['note'],
        }

    binary = str(info['binary'])
    path = runtime_command_source(binary, runtime)
    version = None
    if path:
        try:
            cp = run_capture(list(info['version_cmd']), runtime=runtime, timeout=20)
            version = summarize_output(cp, limit=200)
        except Exception as exc:
            version = f'version check failed: {exc}'
    return {
        **meta,
        'binary': binary,
        'path': path,
        'installed': bool(path),
        'version': version,
    }


def do_check(agent: str, smoke: bool, workdir: WorkdirContext, timeout: int, runtime: str) -> dict:
    result = detect(agent, runtime)
    if not result['installed']:
        result['check_ok'] = False
        result['check_output'] = 'binary not found'
        result['smoke_ok'] = None
        return result

    if agent == 'copilot':
        try:
            cp = run_capture(copilot_native_command(runtime, ['--help']), runtime=runtime, workdir=workdir, timeout=timeout)
            result['check_ok'] = cp.returncode == 0
            result['check_output'] = summarize_output(cp)
            result['check_exit_code'] = cp.returncode
        except Exception as exc:
            result['check_ok'] = False
            result['check_output'] = str(exc)
            result['check_exit_code'] = None

        if smoke:
            try:
                cp = run_capture(copilot_native_command(runtime, ['-p', 'Respond with exactly: COPILOT_SMOKE_OK', '--allow-all-tools']), runtime=runtime, workdir=workdir, timeout=timeout)
                output = summarize_output(cp, limit=2000)
                result['smoke_ok'] = (cp.returncode == 0 and 'COPILOT_SMOKE_OK' in output)
                result['smoke_output'] = output
                result['smoke_exit_code'] = cp.returncode
            except subprocess.TimeoutExpired as exc:
                result['smoke_ok'] = False
                result['smoke_output'] = f'timed out after {timeout} seconds'
                result['smoke_timeout'] = timeout_summary(exc)
                result['smoke_exit_code'] = None
            except Exception as exc:
                result['smoke_ok'] = False
                result['smoke_output'] = str(exc)
                result['smoke_exit_code'] = None
        else:
            result['smoke_ok'] = None
        return result

    info = AGENTS[agent]
    try:
        cp = run_capture(list(info['check_cmd']), runtime=runtime, workdir=workdir, timeout=timeout)
        result['check_ok'] = cp.returncode == 0
        result['check_output'] = summarize_output(cp)
        result['check_exit_code'] = cp.returncode
    except Exception as exc:
        result['check_ok'] = False
        result['check_output'] = str(exc)
        result['check_exit_code'] = None

    if smoke:
        try:
            cp = run_capture(list(info['smoke_cmd']), runtime=runtime, workdir=workdir, timeout=timeout)
            output = summarize_output(cp, limit=2000)
            token = str(info['smoke_token'])
            result['smoke_ok'] = (cp.returncode == 0 and token in output)
            result['smoke_output'] = output
            result['smoke_exit_code'] = cp.returncode
        except subprocess.TimeoutExpired as exc:
            result['smoke_ok'] = False
            result['smoke_output'] = f'timed out after {timeout} seconds'
            result['smoke_timeout'] = timeout_summary(exc)
            result['smoke_exit_code'] = None
        except Exception as exc:
            result['smoke_ok'] = False
            result['smoke_output'] = str(exc)
            result['smoke_exit_code'] = None
    else:
        result['smoke_ok'] = None
    return result


def build_run_command(agent: str, prompt: str, output_format: str, model: Optional[str], allow_write: bool, yolo: bool, extra_args: List[str], workdir: WorkdirContext, runtime: str) -> List[str]:
    if agent == 'claude':
        cmd = ['claude', '-p', prompt, '--output-format', output_format, '--no-session-persistence']
        if model:
            cmd += ['--model', model]
        if yolo:
            cmd += ['--permission-mode', 'bypassPermissions']
        elif allow_write:
            cmd += ['--permission-mode', 'acceptEdits']
        else:
            cmd += ['--permission-mode', 'plan']
        cmd += extra_args
        return cmd

    if agent == 'codex':
        cmd = ['codex', 'exec', '--skip-git-repo-check']
        if model:
            cmd += ['--model', model]
        if yolo:
            cmd += ['--dangerously-bypass-approvals-and-sandbox']
        else:
            cmd += ['--sandbox', 'workspace-write' if allow_write else 'read-only']
        if output_format == 'json':
            cmd += ['--json']
        cmd += extra_args
        cmd += [prompt]
        return cmd

    if agent == 'gemini':
        cmd = ['gemini', '-p', prompt, '--output-format', output_format]
        if model:
            cmd += ['--model', model]
        if yolo:
            cmd += ['--yolo']
        else:
            cmd += ['--approval-mode', 'auto_edit' if allow_write else 'plan']
        cmd += extra_args
        return cmd

    if agent == 'opencode':
        cmd = ['opencode', 'run', prompt, '--dir', workdir.target_path]
        if model:
            cmd += ['--model', model]
        if output_format == 'json':
            cmd += ['--format', 'json']
        if allow_write or yolo:
            cmd += ['--dangerously-skip-permissions']
        cmd += extra_args
        return cmd

    if agent == 'qwen':
        cmd = ['qwen', prompt, '--output-format', output_format]
        if model:
            cmd += ['--model', model]
        if yolo:
            cmd += ['--yolo']
        else:
            cmd += ['--approval-mode', 'auto-edit' if allow_write else 'plan']
        cmd += extra_args
        return cmd

    if agent == 'copilot':
        cmd = ['-p', prompt, '--add-dir', workdir.target_path]
        if output_format != 'text':
            cmd += ['--output-format', 'json']
        if yolo or allow_write:
            cmd += ['--allow-all']
        else:
            cmd += ['--allow-all-tools']
        if model:
            cmd += ['--model', model]
        cmd += extra_args
        return copilot_native_command(runtime, cmd)

    raise SystemExit(f'Unsupported agent: {agent}')


def route_candidates(current_agent: str, runtime: str, requested_agent: Optional[str] = None) -> dict:
    requested = canonical_agent(requested_agent) if requested_agent else None
    order = [agent for agent in DEFAULT_AGENT_ORDER if agent != current_agent]
    if requested and requested != current_agent:
        order = [requested] + [agent for agent in order if agent != requested]
        order.append(current_agent)
    elif requested and requested == current_agent:
        order = [current_agent] + [agent for agent in DEFAULT_AGENT_ORDER if agent != current_agent]
    else:
        order.append(current_agent)

    detections = {agent: detect(agent, runtime) for agent in DEFAULT_AGENT_ORDER}
    candidates = []
    for agent in order:
        if requested and requested == current_agent and agent == current_agent:
            reason = 'explicit-self-override'
        elif requested and agent == requested:
            reason = 'explicit-target'
        elif agent == current_agent:
            reason = 'self-fallback'
        else:
            reason = 'peer-first'
        candidates.append({
            'agent': agent,
            'installed': bool(detections[agent]['installed']),
            'reason': reason,
            'path': detections[agent]['path'],
        })
    return {
        'host_runtime': current_runtime(),
        'target_runtime': runtime,
        'cross_runtime': runtime != default_target_runtime(),
        'current_agent': current_agent,
        'requested_agent': requested,
        'policy': {
            'same_runtime_default': True,
            'cross_runtime_requires_explicit_choice': True,
            'peer_first': True,
            'self_fallback_last': requested != current_agent,
        },
        'ordered_candidates': candidates,
    }


def print_json(data: object) -> None:
    # Ensure UTF-8 output on Windows
    if sys.platform == 'win32':
        import io
        # Reconfigure stdout to use UTF-8 encoding
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write('\n')


def main() -> int:
    parser = argparse.ArgumentParser(description='Unified wrapper for explicit local CLI agent interop with runtime-local routing by default.')
    sub = parser.add_subparsers(dest='command', required=True)

    p_list = sub.add_parser('list', help='List known agents and installation status for the selected runtime.')
    p_list.add_argument('--runtime', choices=['current', 'windows', 'wsl'], default='current', help='Target runtime. Default keeps execution in the current runtime.')

    p_route = sub.add_parser('route', help='Show peer-first route order for the current agent inside the selected runtime.')
    p_route.add_argument('--current-agent', required=True, help='Current/orchestrator agent name')
    p_route.add_argument('--requested-agent', help='Optional explicit target agent to move to the front')
    p_route.add_argument('--runtime', choices=['current', 'windows', 'wsl'], default='current', help='Target runtime. Cross-runtime requires explicit choice.')

    p_check = sub.add_parser('check', help='Run readiness checks for one agent or all agents in the selected runtime.')
    p_check.add_argument('agent', nargs='?', default='all', help='Agent name or all')
    p_check.add_argument('--smoke', action='store_true', help='Run live smoke prompts in addition to fast checks')
    p_check.add_argument('--workdir', default='.', help='Workdir for checks/smoke tests')
    p_check.add_argument('--timeout', type=int, default=90, help='Timeout per check in seconds. Codex smoke can take longer because plugin/MCP shutdown is part of the CLI lifecycle.')
    p_check.add_argument('--runtime', choices=['current', 'windows', 'wsl'], default='current', help='Target runtime. Cross-runtime requires explicit choice.')

    p_run = sub.add_parser('run', help='Run one bounded non-interactive task through a target agent.')
    p_run.add_argument('agent', help='Target agent name or alias')
    p_run.add_argument('--prompt', required=True, help='Prompt to send to the target agent')
    p_run.add_argument('--workdir', default='.', help='Working directory (Windows path or WSL path)')
    p_run.add_argument('--runtime', choices=['current', 'windows', 'wsl'], default='current', help='Target runtime. Default stays in the current runtime.')
    p_run.add_argument('--current-agent', help='Optional current/orchestrator agent name for metadata')
    p_run.add_argument('--output-format', choices=['text', 'json', 'stream-json'], default='text')
    p_run.add_argument('--model', help='Optional model override where the target agent supports it')
    p_run.add_argument('--allow-write', action='store_true', help='Allow edit-capable execution where supported')
    p_run.add_argument('--yolo', action='store_true', help='Opt into broad auto-approval / low-friction mode where supported')
    p_run.add_argument('--extra-arg', action='append', default=[], help='Repeatable extra native CLI arg appended after the wrapper defaults')
    p_run.add_argument('--timeout', type=int, default=0, help='Optional timeout in seconds (0 = no timeout). Prefer at least 120 for Codex runs that load plugins or MCP servers.')
    p_run.add_argument('--dry-run', action='store_true', help='Print the resolved command instead of executing it')

    args = parser.parse_args()
    runtime = effective_runtime(getattr(args, 'runtime', 'current'))

    if args.command == 'list':
        print_json([detect(agent, runtime) for agent in DEFAULT_AGENT_ORDER])
        return 0

    if args.command == 'route':
        current_agent = canonical_agent(args.current_agent)
        print_json(route_candidates(current_agent=current_agent, runtime=runtime, requested_agent=args.requested_agent))
        return 0

    if args.command == 'check':
        workdir = resolve_workdir(args.workdir, runtime)
        targets = DEFAULT_AGENT_ORDER if args.agent == 'all' else [canonical_agent(args.agent)]
        data = [do_check(agent, smoke=args.smoke, workdir=workdir, timeout=args.timeout, runtime=runtime) for agent in targets]
        print_json(data)
        return 0 if all(item.get('check_ok') or not item.get('installed') for item in data) else 1

    if args.command == 'run':
        agent = canonical_agent(args.agent)
        current_agent = canonical_agent(args.current_agent) if args.current_agent else None
        workdir = resolve_workdir(args.workdir, runtime)
        cmd = build_run_command(
            agent=agent,
            prompt=args.prompt,
            output_format=args.output_format,
            model=args.model,
            allow_write=args.allow_write,
            yolo=args.yolo,
            extra_args=args.extra_arg,
            workdir=workdir,
            runtime=runtime,
        )
        wrapped_cmd, _ = wrap_command_for_runtime(cmd, runtime, workdir)
        printable = ' '.join(shlex.quote(part) for part in wrapped_cmd)
        meta = {
            'agent': agent,
            'current_agent': current_agent,
            'host_runtime': current_runtime(),
            'target_runtime': runtime,
            'cross_runtime': runtime != default_target_runtime(),
            'workdir_host_path': str(workdir.host_path),
            'workdir_target_path': workdir.target_path,
            'command': printable,
            'dry_run': args.dry_run,
        }
        if args.dry_run:
            print_json(meta)
            return 0
        if not workdir.host_path.exists():
            print_json({**meta, 'error': f'workdir does not exist: {workdir.host_path}'})
            return 2
        timeout = None if args.timeout == 0 else args.timeout
        try:
            completed = run_live(cmd, runtime=runtime, workdir=workdir, timeout=timeout)
            return completed.returncode
        except subprocess.TimeoutExpired as exc:
            print_json({**meta, 'error': f'timed out after {args.timeout} seconds', **timeout_summary(exc)})
            return 124

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
