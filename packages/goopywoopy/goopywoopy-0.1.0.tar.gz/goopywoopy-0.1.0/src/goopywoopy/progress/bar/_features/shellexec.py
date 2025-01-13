from typing import List, Union, Self, Protocol
from ....abc import Feature
from ....tools.terminal import terminal_width
from ..types import ProgressBar
from pathlib import Path
import subprocess
import time
import os

class GenericCallback(Protocol):
    def __call__(self, line: str, rendered: str) -> None: ...

class BottomFix(GenericCallback, Protocol):
    ...

class GenericLogFunction(Protocol):
    def __call__(self, line: str) -> None: ...

def process_stdout_stderr(cls: ProgressBar, process: subprocess.Popen, callback: Union[GenericCallback, None] = None, logfunc: Union[GenericLogFunction, None] = None) -> None:
    while True:
        stdout: str = process.stdout.readline()
        stderr: str = process.stderr.readline()
        if stdout:
            if callback is not None:
                callback(stdout.strip(), cls.render())
                if cls.tolog: # even if call back is present, check if user wants to log
                    logfunc(f"stdout: {stdout.strip()}")
            else:
                logfunc(f"stdout: {stdout.strip()}")
        if stderr:
            if callback is not None:
                callback(stderr.strip(), cls.render())
                if cls.tolog:
                    logfunc(f"stderr: {stderr.strip()}")
            else:
                logfunc(f"stderr: {stderr.strip()}")
        
        if not stdout and not stderr and process.poll() is not None:
            break

class ShellExecution(Feature):
    @staticmethod
    def BOTTOMFIX_CALLBACK(line: str, rendered: str) -> None:
        print(' ' * terminal_width(), end='\r')
        print(line, flush=True)
        print(rendered.strip(), end='\r')

    def use_shell_codes(self: Union[ProgressBar, Self], codes: List[str], delay: float = 0.1, callback: Union[GenericCallback, None] = None) -> None:
        for code in codes:
            if self.tolog:
                self.log(f'\nCommand: {code}\nType: SHELL')
            
            try:
                # callback(f'comand: {code}', self.render())
                process = subprocess.Popen(code.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            except FileNotFoundError:
                if callback is not None:
                    callback(
                        f'FileNotFoundError: command {code} not found. Failed to run as a shell command.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'FileNotFoundError: command {code} not found. Failed to run as a shell command.')
                else:
                    self.log(f'FileNotFoundError: command {code} not found. Failed to run as a shell command.')
                continue
            except PermissionError:
                if callback is not None:
                    callback(
                        f'Permission Error: Cannot run shell command {code}. Skipping.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'Permission Error: Cannot run sheel command {code}. Skipping.')
                else:
                    self.log(f'Permission Error: Cannot run sheel command {code}. Skipping.')
                continue
            except (subprocess.SubprocessError, subprocess.CalledProcessError) as e:
                if callback is not None:
                    callback(
                        f'Subprocess Error: {e}. Skipping.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'Subprocess Error: {e}. Skipping.')
                else:
                    self.log(f'Subprocess Error: {e}. Skipping.')
                continue
            except ValueError:
                if callback is not None:
                    callback(
                        f'ValueError: possible command error with command({code}) when it is split into parts({code.split()}). Skipping.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'ValueError: possible command error with command({code}) when it is split into parts({code.split()}). Skipping.')
                else:
                    self.log(f'ValueError: possible command error with command({code}) when it is split into parts({code.split()}). Skipping.')
                continue
            except OSError as e:
                if callback is not None:
                    callback(
                        f'OSError: Unexpect oserror: {e}. Skipping.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'OSError: Unexpect oserror: {e}. Skipping.')
                else:
                    self.log(f'OSError: Unexpect oserror: {e}. Skipping.')
                continue
            except Exception as e:
                if callback is not None:
                    callback(
                        f'An Exception has occured. Details: {e}',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'An Exception has occured. Details: {e}')
                else:
                    self.log(f'An Exception has occured. Details: {e}')
                continue
            finally:
                process_stdout_stderr(self, process, callback, self.log)
                process.wait()
                self.precursor._complete += 1
                print(self.render().strip(), end='\r')
                time.sleep(delay)
    
    def use_shell_scripts(self: ProgressBar, script_paths: List[str], delay: float = 0.1, callback: Union[GenericCallback, None] = None) -> None:
        for path in script_paths:
            path = Path(path).expanduser().resolve()
            if not path.exists():
                raise FileNotFoundError(f"Filepath: {path} does not exist.")
            
            try:
                os.chmod(str(path), 0o755)
            except PermissionError:
                if callback is not None:
                    callback(
                        f'Permission Error: Cannot make file {path} executable. Assuming it is already set as executable.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'Permission Error: Cannot make file {path} executable. Assuming it is already set as executable.')
                else:
                    self.log(f'Permission Error: Cannot make file {path} executable. Assuming it is already set as executable.')
            except OSError as e:
                if callback is not None:
                    callback(
                        f'OSError: Skipping {path}. Details: {e}',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f"OSError: Skipping {path}. Details: {e}")
                else:
                    self.log(f"OSError: Skipping {path}. Details: {e}")
                continue
            
            # set command
            command = f"/bin/bash -c {path}"

            if self.tolog:
                self.log(f"\n SCRIPT: {path}; TYPE: SHELL")

            # try process
            try:
                process = subprocess.Popen(command.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            except FileNotFoundError:
                if callback is not None:
                    callback(
                        f'FileNotFoundError: command {command} not found. Failed to run as a shell command.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'FileNotFoundError: command {command} not found. Failed to run as a shell command.')
                else:
                    self.log(f'FileNotFoundError: command {command} not found. Failed to run as a shell command.')
                continue
            except PermissionError:
                if callback is not None:
                    callback(
                        f'Permission Error: Cannot run shell command {command}. Skipping.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'Permission Error: Cannot run sheel command {command}. Skipping.')
                else:
                    self.log(f'Permission Error: Cannot run sheel command {command}. Skipping.')
                continue
            except (subprocess.SubprocessError, subprocess.CalledProcessError) as e:
                if callback is not None:
                    callback(
                        f'Subprocess Error: {e}. Skipping.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'Subprocess Error: {e}. Skipping.')
                else:
                    self.log(f'Subprocess Error: {e}. Skipping.')
                continue
            except ValueError:
                if callback is not None:
                    callback(
                        f'ValueError: possible command error with command({command}) when it is split into parts({command.split()}). Skipping.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'ValueError: possible command error with command({command}) when it is split into parts({command.split()}). Skipping.')
                else:
                    self.log(f'ValueError: possible command error with command({command}) when it is split into parts({command.split()}). Skipping.')
                continue
            except OSError as e:
                if callback is not None:
                    callback(
                        f'OSError: Unexpect oserror: {e}. Skipping.',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'OSError: Unexpect oserror: {e}. Skipping.')
                else:
                    self.log(f'OSError: Unexpect oserror: {e}. Skipping.')
                continue
            except Exception as e:
                if callback is not None:
                    callback(
                        f'An Exception has occured. Details: {e}',
                        self.render()
                    )
                    if self.tolog:
                        self.log(f'An Exception has occured. Details: {e}')
                else:
                    self.log(f'An Exception has occured. Details: {e}')
                continue
            finally:
                process_stdout_stderr(self, process, callback, self.log)
                process.wait()
                self.precursor._complete += 1
                print(self.render(), end='\r')
                time.sleep(delay)