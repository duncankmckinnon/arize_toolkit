# Releasing to PyPI

This document explains the process for releasing new versions of the Arize Toolkit package to PyPI.

## Prerequisites

Before you can release a new version, you need:

1. **PyPI API Token**: 
   - Generate a token at [PyPI Settings](https://pypi.org/manage/account/token/)
   - Add it as a repository secret in GitHub with the name `PYPI_API_TOKEN`

2. **Write Access to the Repository**:
   - You need to be able to create tags and releases

## Release Process

### Option 1: Manual Release (Recommended for important releases)

1. **Update CHANGELOG.md** (if you have one):
   ```markdown
   # Changelog

   ## v0.1.0 (YYYY-MM-DD)
   - Feature: Added new feature X
   - Fix: Fixed bug in Y
   - Changed: Updated Z
   ```

2. **Create and push a tag**:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. **Create a GitHub Release**:
   - Go to the [Releases page](https://github.com/duncankmckinnon/arize_toolkit/releases)
   - Click "Draft a new release"
   - Select your tag
   - Add a title and description
   - Click "Publish release"

4. **Monitor the Workflow**:
   - Go to the [Actions tab](https://github.com/duncankmckinnon/arize_toolkit/actions)
   - You should see the "Release Python Package to PyPI" workflow running
   - The workflow will:
     - Run tests on multiple Python versions
     - Build the package
     - Publish to PyPI
     - Upload build artifacts to the GitHub release

### Option 2: Tag-Only Release (Quick releases)

Simply push a tag and the workflow will handle the rest:

```bash
git tag v0.1.1
git push origin v0.1.1
```

## Version Format

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API changes
- **MINOR**: Added functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

Always prefix with "v" (e.g., `v1.0.0`).

## After Release

- Verify the package is available on [PyPI](https://pypi.org/project/arize-toolkit/)
- Test installation with `pip install arize-toolkit`
- Announce the release to users if applicable 