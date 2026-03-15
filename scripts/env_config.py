"""Read environment detection config written by hooks/setup-deps.sh.

Usage:
    from env_config import load_env_config

    config = load_env_config()
    if config["PDF_BACKEND"] == "typst":
        # Use Typst renderer
    else:
        # Use Python fallback renderer

The config file lives at ``workspace/.env-config`` and is regenerated on
every session start by the SessionStart hook.
"""

from pathlib import Path


_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_CONFIG_PATH = _PROJECT_ROOT / "workspace" / ".env-config"

# Defaults used when the config file hasn't been generated yet (e.g. tests
# or manual script invocation outside a Claude session).
_DEFAULTS: dict[str, str] = {
    "HAS_UV": "false",
    "HAS_PIP": "false",
    "PKG_MANAGER": "none",
    "HAS_TYPST": "false",
    "TYPST_SOURCE": "none",
    "PDF_BACKEND": "python-fallback",
    "HAS_PYTHON_DOCX": "false",
    "HAS_PDF_FALLBACK": "false",
    "FONTS_DIR": str(_PROJECT_ROOT / "fonts"),
    "FONTS_ACCESSIBLE": "false",
    "PLUGIN_ROOT": str(_PROJECT_ROOT),
}


def load_env_config(config_path: Path | None = None) -> dict[str, str]:
    """Load and return the environment config as a string-keyed dict.

    Parameters
    ----------
    config_path:
        Override the default config file path (useful for testing).

    Returns
    -------
    dict[str, str]
        Keys match the variable names written by ``setup-deps.sh``.
        Boolean-style values are the strings ``"true"`` / ``"false"``.
    """
    path = config_path or _CONFIG_PATH
    config = dict(_DEFAULTS)

    if not path.exists():
        return config

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        config[key.strip()] = value.strip()

    return config


def has_typst(config: dict[str, str] | None = None) -> bool:
    """Return True if Typst is available for PDF generation."""
    cfg = config or load_env_config()
    return cfg.get("HAS_TYPST", "false") == "true"


def pdf_backend(config: dict[str, str] | None = None) -> str:
    """Return the PDF backend name: ``'typst'`` or ``'python-fallback'``."""
    cfg = config or load_env_config()
    return cfg.get("PDF_BACKEND", "python-fallback")


def has_uv(config: dict[str, str] | None = None) -> bool:
    """Return True if uv package manager is available."""
    cfg = config or load_env_config()
    return cfg.get("HAS_UV", "false") == "true"


def has_python_docx(config: dict[str, str] | None = None) -> bool:
    """Return True if python-docx is importable."""
    cfg = config or load_env_config()
    return cfg.get("HAS_PYTHON_DOCX", "false") == "true"


def has_pdf_fallback(config: dict[str, str] | None = None) -> bool:
    """Return True if the Python PDF fallback library (fpdf2) is importable."""
    cfg = config or load_env_config()
    return cfg.get("HAS_PDF_FALLBACK", "false") == "true"


def fonts_dir(config: dict[str, str] | None = None) -> Path:
    """Return the path to the bundled fonts directory."""
    cfg = config or load_env_config()
    return Path(cfg.get("FONTS_DIR", str(_PROJECT_ROOT / "fonts")))


def fonts_accessible(config: dict[str, str] | None = None) -> bool:
    """Return True if the bundled fonts directory contains usable font files."""
    cfg = config or load_env_config()
    return cfg.get("FONTS_ACCESSIBLE", "false") == "true"
