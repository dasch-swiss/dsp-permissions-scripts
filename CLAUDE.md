# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python library for managing DSP (DaSCH Service Platform) permissions through the DSP-API. The scripts allow administrators to retrieve, modify, and update three types of permissions:

- **AP** (Administrative Permissions): Project-level permissions for user groups
- **DOAP** (Default Object Access Permissions): Default permissions applied to resources/values when created
- **OAP** (Object Access Permissions): Instance-level permissions for specific resources and values

## Development Commands

### Environment Setup
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync all dependencies including dev dependencies
uv sync --all-extras --dev

# Activate virtual environment
source .venv/bin/activate
```

### Code Quality
```bash
# Format code
ruff format

# Run all linting checks
ruff check

# Run type checks
mypy .

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Testing
```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_ap_model.py

# Run a specific test function
pytest tests/test_ap_model.py::test_function_name

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s
```

## Architecture

### Module Organization

The codebase is organized by permission type, with each having parallel operations:

```
dsp_permissions_scripts/
├── ap/               # Administrative Permissions
│   ├── ap_model.py       # Data models
│   ├── ap_get.py         # Retrieve from server
│   ├── ap_set.py         # Update on server
│   ├── ap_delete.py      # Delete from server
│   └── ap_serialize.py   # JSON serialization
├── doap/             # Default Object Access Permissions
│   └── (same structure as ap/)
├── oap/              # Object Access Permissions
│   └── (same structure as ap/)
├── models/           # Core data models
│   ├── scope.py          # Permission scopes (CR, D, M, V, RV)
│   ├── group.py          # User groups (PROJECT_ADMIN, PROJECT_MEMBER, etc.)
│   ├── host.py           # DSP server environments
│   ├── errors.py         # Custom exceptions
│   └── group_utils.py    # Group helper functions
└── utils/            # Shared utilities
    ├── dsp_client.py     # HTTP client for DSP-API
    ├── authentication.py # Login/logout
    ├── get_logger.py     # Logging setup
    └── project.py        # Project-level operations
```

### Typical Workflow

Users typically:
1. Copy `dsp_permissions_scripts/template.py` to a new file
2. Configure the host (localhost, prod, dev, test) and project shortcode
3. Modify the three functions (`modify_aps`, `modify_doaps`, `modify_oaps`) to implement desired changes
4. Run the script to:
   - Retrieve current permissions and serialize to JSON in `project_data/<shortcode>/`
   - Apply modifications via DSP-API
   - Retrieve updated permissions and serialize again for verification

### Core Concepts

**Permission Scopes**: Rights are hierarchical (each includes all previous):
- No permission → `RV` (restricted view) → `V` (view) → `M` (modify) → `D` (delete) → `CR` (change rights)

**User Groups**:
- Built-in: `UnknownUser`, `KnownUser`, `ProjectMember`, `ProjectAdmin`, `Creator`, `SystemAdmin`
- Custom project-specific groups can also be defined

**DspClient**: Central HTTP client class that:
- Manages authentication tokens
- Handles retries with exponential backoff
- Logs all requests/responses (with sensitive data masked)
- Raises `ApiError` for permanent failures or `PermissionsAlreadyUpToDate` when no changes needed

### Hosts and Environments

The `Hosts` class provides access to different DSP environments:
- `localhost`: Local development server (`http://0.0.0.0:3333`)
- `prod`: Production (`https://api.dasch.swiss`)
- `rdu`: RDU environment (`https://api.rdu.dasch.swiss`)
- Other: Dynamic construction for dev/test/staging environments (`https://api.{identifier}.dasch.swiss`)

Credentials are stored in `.env` file (never commit this file).

## Code Standards

- All code must be strongly typed and pass `mypy --strict`
- Code must be formatted with `ruff format`
- Code must pass all ruff linting rules (see pyproject.toml for enabled rules)
- Use pathlib for file paths
- Use dataclasses for data bundling
- Prefer functions over classes with state and behavior
- Pre-commit hooks will enforce formatting and run checks before commits

## Important Notes

- The template file is the entry point - all other code is library/consume-only
- JSON files in `project_data/` contain serialized permissions for review before applying changes
- The DSP-API documentation is at https://docs.dasch.swiss/latest/DSP-API/
- Always retrieve and serialize original permissions before making modifications
- The DspClient automatically retries transient errors up to 10 times with exponential backoff
