from enum import Enum
import colorama

WINBAT = """
@echo off
:: BatchGotAdmin
:--------------------------
@Rem --> Check for Permission
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

@Rem if error flag set, we do not have admin.
if %errorlevel% NEQ 0 (
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"
:-----------------------------------

@Rem check registry for ansi colour code
echo [REGISTRY CHECK]
reg query HKCU\Console\ | find /I "VirtualTerminalLevel" > nul
if %errorlevel% NEQ 0 (
    @Rem ANSI settings not found.
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1
    echo added registry for ANSI escape sequence
) else (
    echo found existing registry for ANSI escape sequence. Skipping..
)
"""

class Color(Enum):
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    BLUE = colorama.Fore.BLUE
    BLACK = colorama.Fore.BLACK
    CYAN = colorama.Fore.CYAN
    MAGENTA = colorama.Fore.MAGENTA
    WHITE = colorama.Fore.WHITE
    YELLOW = colorama.Fore.YELLOW
    LIGHTRED = colorama.Fore.LIGHTRED_EX
    LIGHTGREEN = colorama.Fore.LIGHTGREEN_EX
    LIGHTBLUE = colorama.Fore.LIGHTBLUE_EX
    LIGHTBLACK = colorama.Fore.LIGHTBLACK_EX
    LIGHTCYAN = colorama.Fore.LIGHTCYAN_EX
    LIGHTMAGENTA = colorama.Fore.LIGHTMAGENTA_EX
    LIGHTWHITE = colorama.Fore.LIGHTWHITE_EX
    LIGHTYELLOW = colorama.Fore.LIGHTYELLOW_EX

    @staticmethod
    def colorize() -> None:
        return colorama.init()
    
    @staticmethod
    def fix_ANSI_in_Windows() -> None:
        with open('fix-ANSI.bat', 'w') as bat_reference:
            bat_reference.write(WINBAT)

    def __init__(self, color: str) -> None:
        self.color = color
    
    def __str__(self) -> str:
        return self.color
    
    def __repr__(self) -> str:
        return self.color
    
    def render(self) -> str:
        return str(self)
    
    @property
    def reset(self) -> str:
        return colorama.Fore.RESET