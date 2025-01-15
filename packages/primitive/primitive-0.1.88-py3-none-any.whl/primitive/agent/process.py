from typing import List
from pathlib import Path
from subprocess import Popen, PIPE
import shlex
import glob
import selectors
from loguru import logger
from abc import abstractmethod


class Process:
    def __init__(
        self,
        cmd,
        env,
        workdir: str = ".",
    ):
        self.cmd = Process.expand_glob_in_cmd(
            cmd_parts=shlex.split(cmd), workdir=workdir
        )
        self.env = env
        self.workdir = workdir
        self.process = None
        self.stdout_thread = None
        self.stderr_thread = None
        self._errors = 0
        self._warnings = 0

    def start(self):
        # Start the process
        self.sel = selectors.DefaultSelector()
        self.process = Popen(
            self.cmd,
            env=self.env,
            cwd=self.workdir,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
        )

        self.sel.register(self.process.stdout, selectors.EVENT_READ)
        self.sel.register(self.process.stderr, selectors.EVENT_READ)

    def log(self):
        for key, _ in self.sel.select():
            data = key.fileobj.readline()
            if not data:
                continue

            if key.fileobj is self.process.stdout:
                raw_data = data.rstrip()
                if "error" in raw_data.lower():
                    logger.error(raw_data)
                    self._errors += 1
                elif "warning" in raw_data.lower():
                    logger.warning(raw_data)
                    self._warnings += 1
                else:
                    logger.info(raw_data)
            elif key.fileobj is self.process.stderr:
                logger.error(data.rstrip())
                self._errors += 1

    def wait(self):
        while True:
            self.log()
            if not self.is_running():
                break

        return self.finish()

    def run(self):
        """Start and wait for the process."""
        self.start()
        return self.wait()

    def is_running(self):
        """Check if the process is still running."""
        return self.process and self.process.poll() is None

    def finish(self):
        """Make sure that logging finishes"""
        if self.process:
            self.sel.unregister(self.process.stdout)
            self.sel.unregister(self.process.stderr)
            self.process.stdout.close()
            self.process.stderr.close()

            return self.process.poll()

    def terminate(self):
        """Terminate the process."""
        if self.process:
            self.process.terminate()

    def kill(self):
        """Kill the process."""
        if self.process:
            self.process.kill()

    @abstractmethod
    def expand_glob_in_cmd(cmd_parts: List[str], workdir: Path):
        # Characters that indicate a glob pattern
        glob_chars = {"*", "?", "[", "]", "{", "}"}
        expanded_cmd = []
        for part in cmd_parts:
            if any(c in part for c in glob_chars):
                matches = glob.glob(str(workdir / part))
                if matches:
                    expanded_cmd.extend(
                        [str(Path(match).relative_to(workdir)) for match in matches]
                    )
                else:
                    expanded_cmd.append(part)
            else:
                expanded_cmd.append(part)
        return expanded_cmd

    @property
    def errors(self) -> int:
        return self._errors

    @property
    def warnings(self) -> int:
        return self._warnings
