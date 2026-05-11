# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for CV Matcher
# Build:  pyinstaller cv_matcher.spec

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("static",        "static"),        # HTML UI
        (".env.example",  "."),             # template env file
        ("schema.sql",    "."),             # SQL schema
    ],
    hiddenimports=[
        # FastAPI / Starlette internals
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "starlette.routing",
        "starlette.middleware",
        "starlette.staticfiles",
        "starlette.responses",
        # Database
        "sqlalchemy.dialects.postgresql",
        "psycopg",
        "psycopg.adapt",
        "psycopg._pq._pq_ctypes",
        # CV parsing
        "pdfplumber",
        "docx",
        "pydantic",
        # stdlib
        "email.mime.multipart",
        "email.mime.text",
        "logging.handlers",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "test", "unittest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="cv_matcher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,           # keep console for log output
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="cv_matcher",
)
