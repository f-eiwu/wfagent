# -*- mode: python ; coding: utf-8 -*-
"""Packaging spec for a transferable Windows coding-agent.exe."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files

project_root = Path(SPECPATH).resolve().parent
src = project_root / "src"
tui_css = src / "coding_agent" / "tui" / "app.tcss"

datas = [(str(tui_css), "coding_agent/tui")]
binaries = []
hiddenimports = [
    "coding_agent",
    "coding_agent.cli",
    "coding_agent.tui.app",
    "coding_agent.tui.run_phase",
    "coding_agent.tools.factory",
    "coding_agent.tools.file_tools",
    "coding_agent.tools.shell_tools",
]

for package in ("textual", "rich", "openai", "httpx", "certifi", "prompt_toolkit"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

datas += collect_data_files("coding_agent")

a = Analysis(
    [str(src / "coding_agent" / "__main__.py")],
    pathex=[str(src)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="coding-agent",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
