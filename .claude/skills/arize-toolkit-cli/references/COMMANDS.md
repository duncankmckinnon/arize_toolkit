# Arize CLI Full Command Reference

## Config

```bash
arize_toolkit config init [--profile-name NAME]     # Interactive profile setup
arize_toolkit config list                            # List all profiles
arize_toolkit config show [--profile-name NAME]      # Show profile details
arize_toolkit config use NAME                        # Set default profile
```

## Spaces

```bash
arize_toolkit spaces list                                          # List all spaces
arize_toolkit spaces get NAME                                      # Get space by name
arize_toolkit spaces create NAME [--private|--public] [--no-switch] # Create space
arize_toolkit spaces switch NAME [--org ORG]                       # Switch active space
arize_toolkit spaces create-key NAME                               # Create space API key
```

## Organizations

```bash
arize_toolkit orgs list                                                                    # List orgs
arize_toolkit orgs create ORG_NAME SPACE_NAME [--description DESC] [--space-private|--space-public] # Create org + space
```

## Users

```bash
arize_toolkit users get SEARCH                                                              # Search user by name/email
arize_toolkit users assign USER_NAMES... [--spaces SPACE...] [--role {admin,member,readOnly,annotator}] # Assign to spaces
arize_toolkit users remove USER_NAME [--space SPACE]                                        # Remove from space
```

## Models (alias: projects)

```bash
arize_toolkit models list                                                   # List models
arize_toolkit models get NAME                                               # Get model details
arize_toolkit models volume NAME [--start-time T] [--end-time T]            # Prediction volume
arize_toolkit models total-volume [--model-name N] [--model-id ID] [--start-time T] [--end-time T] # Total volume
arize_toolkit models performance METRIC ENV [--model-name N] [--model-id ID] [--granularity {hour,day,week,month}] [--start-time T] [--end-time T] # Performance over time
arize_toolkit models delete-data NAME [--start-time T] [--end-time T]       # Delete data (confirms)
```

## Monitors

### List and Get

```bash
arize_toolkit monitors list [--model-name N] [--model-id ID] [--category {drift,dataQuality,performance}]
arize_toolkit monitors get NAME --model MODEL
```

### Create

All create commands share these common options:

```
--notes TEXT                  Notes
--threshold FLOAT             Alert threshold
--std-dev-multiplier FLOAT    Std dev multiplier (default: 2.0)
--operator {greaterThan,lessThan,greaterThanOrEqual,lessThanOrEqual}  (default: greaterThan)
--evaluation-window INT       Window in seconds (default: 259200)
--delay INT                   Delay in seconds (default: 0)
--threshold-mode {single,double}  (default: single)
--threshold2 FLOAT            Second threshold (double mode)
--operator2 {greaterThan,lessThan,greaterThanOrEqual,lessThanOrEqual}
--email EMAIL                 Notification email (repeatable)
--integration-key-id ID       Integration key (repeatable)
```

```bash
# Performance monitor
arize_toolkit monitors create-performance NAME --model MODEL --environment {tracing,production,validation,training} \
  [--performance-metric METRIC] [--custom-metric-id ID] [COMMON_OPTIONS]

# Drift monitor
arize_toolkit monitors create-drift NAME --model MODEL \
  [--drift-metric {psi,js,kl,ks,euclideanDistance,cosineSimilarity}] \
  [--dimension-category CAT] [--dimension-name NAME] [COMMON_OPTIONS]

# Data quality monitor
arize_toolkit monitors create-data-quality NAME --model MODEL \
  --data-quality-metric METRIC --environment {tracing,production,validation,training} \
  [--dimension-category CAT] [--dimension-name NAME] [COMMON_OPTIONS]
```

### Manage

```bash
arize_toolkit monitors delete NAME --model MODEL                                            # Delete (confirms)
arize_toolkit monitors copy NAME --model MODEL [--new-name N] [--new-model M] [--new-space-id ID] # Copy
arize_toolkit monitors values NAME --model MODEL [--granularity G] [--start-time T] [--end-time T] # Values over time
arize_toolkit monitors latest-value NAME --model MODEL [--granularity G]                    # Latest value
```

## Prompts

```bash
arize_toolkit prompts list                              # List all prompts
arize_toolkit prompts get NAME                          # Get prompt
arize_toolkit prompts versions NAME                     # List versions
arize_toolkit prompts create NAME --messages JSON_OR_@FILE \
  [--commit-message MSG] [--description DESC] [--tag TAG...] \
  [--provider PROVIDER] [--model-name MODEL] \
  [--input-variable-format {f_string,mustache,none}]    # Create prompt
arize_toolkit prompts update NAME [--new-name N] [--description DESC] [--tag TAG...] # Update
arize_toolkit prompts delete NAME                       # Delete (confirms)
```

## Custom Metrics

```bash
arize_toolkit custom-metrics list [--model-name N]                         # List metrics
arize_toolkit custom-metrics get NAME --model MODEL                        # Get metric
arize_toolkit custom-metrics create NAME --metric EXPR --model MODEL \
  [--environment {tracing,production,staging,development}] [--description DESC] # Create
arize_toolkit custom-metrics update NAME --model MODEL \
  [--new-name N] [--metric EXPR] [--description DESC] [--environment ENV]  # Update
arize_toolkit custom-metrics delete NAME --model MODEL                     # Delete (confirms)
arize_toolkit custom-metrics copy NAME --model MODEL \
  [--new-model M] [--new-name N] [--new-description DESC] [--new-environment ENV] # Copy
```

## Evaluators

```bash
arize_toolkit evaluators list [--search N] [--name N] [--task-type {template_evaluation,code_evaluation}] # List
arize_toolkit evaluators get NAME                                          # Get evaluator

# Create LLM template evaluator
arize_toolkit evaluators create-template NAME --template TEMPLATE_OR_@FILE --metric-name METRIC \
  [--commit-message MSG] [--description DESC] [--tag TAG...] \
  [--classification-choices JSON] [--direction {maximize,minimize}] \
  [--data-granularity {span,trace,session}] \
  [--include-explanations|--no-explanations] \
  [--use-function-calling|--no-function-calling] \
  [--llm-integration-name NAME] [--llm-model-name NAME]

# Create Python code evaluator
arize_toolkit evaluators create-code NAME --metric-name METRIC --code CODE_OR_@FILE \
  --evaluation-class CLASS --span-attribute ATTR... \
  [--commit-message MSG] [--description DESC] [--tag TAG...] \
  [--data-granularity {span,trace,session}] [--package-imports IMPORTS]

arize_toolkit evaluators edit ID [--name N] [--description DESC] [--tag TAG...] # Edit metadata
arize_toolkit evaluators delete ID                                         # Delete (confirms)
```

## Dashboards

```bash
arize_toolkit dashboards list                                # List dashboards
arize_toolkit dashboards get NAME                            # Get dashboard
arize_toolkit dashboards create NAME                         # Create empty dashboard
arize_toolkit dashboards create-volume NAME [--model M...]   # Create volume dashboard
```

## Traces

```bash
arize_toolkit traces list --model-name NAME [--model-id ID] [--start-time T] [--end-time T] \
  [--count N] [--sort {desc,asc}] [--csv PATH]                                      # List traces
arize_toolkit traces get TRACE_ID --model-name NAME [--model-id ID] [--start-time T] [--end-time T] \
  [--columns COLS] [--all] [--count N] [--csv PATH]                                  # Get trace spans
arize_toolkit traces columns --model-name NAME [--model-id ID] [--start-time T] [--end-time T] # List available columns
```

## Imports

### File Imports (S3, GCS, Azure)

```bash
arize_toolkit imports files list                             # List file import jobs
arize_toolkit imports files get JOB_ID                       # Get job details
arize_toolkit imports files create \
  --blob-store {s3,gcs,azure} --bucket BUCKET --prefix PREFIX \
  --model MODEL --model-type {classification,regression,ranking,object_detection,multi-class,generative} \
  --schema JSON_OR_@FILE \
  [--model-version V] [--environment {production,validation,training,tracing}] \
  [--dry-run] [--batch-id ID] \
  [--azure-tenant-id ID] [--azure-storage-account NAME]     # Create job
arize_toolkit imports files delete JOB_ID                    # Delete (confirms)
```

### Table Imports (BigQuery, Snowflake, Databricks)

```bash
arize_toolkit imports tables list                            # List table import jobs
arize_toolkit imports tables get JOB_ID                      # Get job details
arize_toolkit imports tables create \
  --table-store {BigQuery,Snowflake,Databricks} \
  --model MODEL --model-type {classification,regression,ranking,object_detection,multi-class,generative} \
  --schema JSON_OR_@FILE --table-config JSON_OR_@FILE \
  [--model-version V] [--environment {production,validation,training,tracing}] \
  [--dry-run] [--batch-id ID]                                # Create job
arize_toolkit imports tables delete JOB_ID                   # Delete (confirms)
```
