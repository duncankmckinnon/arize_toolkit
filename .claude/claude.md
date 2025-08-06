Project Overview

Arize Toolkit is a Python library that provides tools for interacting with Arize AI APIs

Key Features

- Model Management: Access and manage models, retrieve performance metrics and inference volumes
- Monitor Tools: Create, copy, and manage monitors and alerting
- Custom Metrics: Create and manage custom metrics
- LLM Features: Work with prompts, annotations, and language model features
- Data Import: Import data from cloud storage (S3, GCS, Azure) and databases (BigQuery, Snowflake, Databricks)
- Dashboard Tools: Create and manage dashboards
- Prompt Optimization Extension: Automated prompt improvement using meta-prompt techniques

Technical Stack

- Language: Python 3.9-3.12
- Build System: Hatchling with hatch-vcs
- Key Dependencies: pandas, pydantic v2, gql (GraphQL), requests
- Testing: pytest, pytest-cov
- Code Style: black, flake8, isort
- Documentation: MkDocs with Material theme
- Package Manager: Uses uv for dependency management

Project Structure

- arize_toolkit/: Main package with client, models, queries, and utilities
- arize_toolkit/extensions/prompt_optimizer/: Prompt optimization extension
- tests/: Comprehensive test suite with 92% coverage
- docs_site/: Documentation site
- examples/: Example notebooks
