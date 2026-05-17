from __future__ import annotations

import http.client
import json
import re
import socket
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

from .config import BotConfig

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

DOCKER_SOCK = "/var/run/docker.sock"


def ok(msg: str) -> None:
    print(f"{GREEN}[+]{RESET} {msg}")


def info(msg: str) -> None:
    print(f"{CYAN}[*]{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{YELLOW}[!]{RESET} {msg}")


def err(msg: str) -> None:
    print(f"{RED}[-]{RESET} {msg}")


def detect_my_team() -> Optional[int]:
    env = socket.gethostname()
    match = re.match(r"team(\d+)", env)
    if match:
        return int(match.group(1))
    return None


@dataclass
class BotContext:
    config: BotConfig
    num_teams: int
    my_team: int | None
    hostname: str = field(default_factory=socket.gethostname)
    _flag_re_cache: re.Pattern | None = field(default=None, init=False, repr=False)

    def flag_re(self) -> re.Pattern:
        if self._flag_re_cache is None:
            self._flag_re_cache = re.compile(self.config.flag_re)
        return self._flag_re_cache

    def target_ip(self, team_id: int) -> str:
        return self.config.ip_pattern.format(team=team_id)

    def service_url(self, team_id: int) -> str:
        return f"http://{self.target_ip(team_id)}:{self.config.service_port}"

    def get(self, url: str, opener=None) -> str | None:
        try:
            fn = opener.open if opener else urllib.request.urlopen
            with fn(url, timeout=self.config.timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, OSError):
            return None

    def post(self, url: str, data: dict[str, str], opener=None) -> str | None:
        payload = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=payload)
        try:
            fn = opener.open if opener else urllib.request.urlopen
            with fn(req, timeout=self.config.timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, OSError):
            return None

    def post_json(
        self,
        url: str,
        body: dict[str, object],
        extra_headers: dict[str, str] | None = None,
    ) -> tuple[int, str]:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        for key, value in (extra_headers or {}).items():
            req.add_header(key, value)

        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                return resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, OSError) as exc:
            return 0, str(exc)


class UnixSocketHTTPConnection(http.client.HTTPConnection):
    def __init__(self, sock_path: str) -> None:
        super().__init__("localhost")
        self._sock_path = sock_path

    def connect(self) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self._sock_path)
        self.sock = sock


def docker_get(path: str):
    try:
        conn = UnixSocketHTTPConnection(DOCKER_SOCK)
        conn.request("GET", path, headers={"Host": "localhost"})
        resp = conn.getresponse()
        if resp.status == 200:
            return json.loads(resp.read())
    except Exception:
        pass
    return None


def docker_post(path: str) -> bool:
    try:
        conn = UnixSocketHTTPConnection(DOCKER_SOCK)
        conn.request("POST", path, headers={"Host": "localhost", "Content-Length": "0"})
        resp = conn.getresponse()
        return 200 <= resp.status < 300
    except Exception:
        return False


def ping_team(ctx: BotContext, team_id: int) -> bool:
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "2", ctx.target_ip(team_id)],
        capture_output=True,
    )
    return result.returncode == 0


def ping_all(ctx: BotContext) -> None:
    info(f"Ping sweep - {ctx.num_teams} teams")
    for team_id in range(1, ctx.num_teams + 1):
        ip = ctx.target_ip(team_id)
        alive = ping_team(ctx, team_id)
        status = f"{GREEN}UP{RESET}" if alive else f"{RED}DOWN{RESET}"
        print(f"  team{team_id:>2}  {ip}  {status}")
