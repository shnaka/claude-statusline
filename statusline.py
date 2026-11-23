#!/usr/bin/env python3
"""Claude Code のステータスライン。モデル、effort、ブランチ、コンテキストと使用量のバーを 1 行で出す。"""
import json, os, sys, subprocess, time
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

data = json.load(sys.stdin)

# 5 時間と 7 日の使用量を、statusline の外（Claude のセッションやスクリプト）から読めるように残す。
# 使用量はアカウント単位なので、どのセッションが書いても同じ値になる。
def _save_rate_limits():
    try:
        limits = data.get('rate_limits')
        if not limits:
            return
        cache_dir = os.path.expanduser('~/.claude/cache')
        os.makedirs(cache_dir, exist_ok=True)
        path = os.path.join(cache_dir, 'rate-limits.json')
        tmp = f'{path}.{os.getpid()}.tmp'
        with open(tmp, 'w') as f:
            json.dump({'rate_limits': limits, 'updated_at': time.time()}, f)
        os.replace(tmp, path)
    except Exception:
        pass

_save_rate_limits()

BLOCKS = '░▏▎▍▌▋▊▉█'
R = '\033[0m'
DIM = '\033[2m'
CYAN = '\033[38;2;100;200;255m'

def git_branch(cwd):
    if not cwd:
        return None
    try:
        result = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'],
            cwd=cwd, capture_output=True, text=True, timeout=0.5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=cwd, capture_output=True, text=True, timeout=0.5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None

def gradient(pct):
    if pct < 50:
        r = int(pct * 5.1)
        return f'\033[38;2;{r};200;80m'
    else:
        g = int(200 - (pct - 50) * 4)
        return f'\033[38;2;255;{max(g,0)};60m'

def bar(pct, width=10):
    pct = min(max(pct, 0), 100)
    filled = pct * width / 100
    full = int(filled)
    frac = int((filled - full) * 8)
    b = '█' * full
    if full < width:
        b += BLOCKS[frac]
        b += '░' * (width - full - 1)
    return b

def fmt(label, pct):
    p = round(pct)
    return f'{label} {gradient(pct)}{bar(pct)} {p}%{R}'

EFFORT_COLORS = {
    'low':    '\033[38;2;100;220;120m',
    'medium': '\033[38;2;100;200;255m',
    'high':   '\033[38;2;255;220;80m',
    'xhigh':  '\033[38;2;255;150;60m',
    'max':    '\033[38;2;255;80;100m',
}

model = data.get('model', {}).get('display_name', 'Claude')
effort = data.get('effort', {}).get('level')
if effort:
    color = EFFORT_COLORS.get(effort, CYAN)
    model = f'{model} {color}{effort}{R}'
parts = [model]

cwd = data.get('workspace', {}).get('current_dir') or data.get('cwd')
branch = git_branch(cwd)
if branch:
    parts.append(f'{CYAN}⎇ {branch}{R}')

ctx = data.get('context_window', {}).get('used_percentage')
if ctx is not None:
    parts.append(fmt('ctx', ctx))

five = data.get('rate_limits', {}).get('five_hour', {}).get('used_percentage')
if five is not None:
    parts.append(fmt('5h', five))

week = data.get('rate_limits', {}).get('seven_day', {}).get('used_percentage')
if week is not None:
    parts.append(fmt('7d', week))

print(f'{DIM}│{R}'.join(f' {p} ' for p in parts), end='')

