# Jira Backup Python

[![datree-badge](https://s3.amazonaws.com/catalog.static.datree.io/datree-badge-28px.svg)](https://datree.io/?src=badge)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python-based backup tool for Atlassian Cloud Jira and Confluence instances with multi-cloud storage support and automated scheduling.

## 🚀 Features

- **Jira & Confluence Backups**: Create backups for both Jira and Confluence Cloud instances
- **Multi-Cloud Support**: Stream backups directly to AWS S3, Google Cloud Storage, or Azure Blob Storage
- **Local Download**: Option to download backup files locally
- **Cross-Platform Scheduling**: Automatically create cron jobs (Linux/macOS) or scheduled tasks (Windows)
- **Configuration Wizard**: Interactive setup for easy configuration
- **API Token Authentication**: Secure authentication using Atlassian API tokens

## 📋 Prerequisites

- Python 3.8 or higher
- Atlassian Cloud account (Jira and/or Confluence)
- API token from [Atlassian](https://id.atlassian.com/manage/api-tokens)
- (Optional) Cloud storage account: AWS, Google Cloud, or Azure

## 🛠️ Installation

### From PyPI

```shell
pip install jira_backup
```

### From source

1. **Clone the repository**
   ```bash
   git clone https://github.com/datreeio/jira-backup-py.git
   cd jira-backup-py
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install this project with its dependencies**
   ```bash
   pip install .
   ```

### Post-installation steps

1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage/api-tokens) and create a token.
2. See the [Configuration](#configuration) section below.

## ⚙️ Configuration

### Configuration file

- `jira_backup` looks for a `config.yaml` file in the working directory.
- You can pass a config file explicitly with `-C /path/to/config.yaml` or `--config /path/to/config.yaml`.
- You can [generate a config file using the wizard](#configuration-wizard).
- For source checkouts, you can start from the example file: `cp config.example.yaml config.yaml`

#### Configuration validation

- The config file is loaded with `yaml.safe_load` and validated with Pydantic before any backup starts.
- Keys are case-insensitive.
- Unknown keys are rejected.
- Duplicate keys are considered an error.
- Booleans must be real YAML booleans (`true` or `false`), not quoted strings.
- `host_url` must be the Atlassian hostname without `https://` or a path.

#### Configuration example

```yaml
---
host_url: "your-instance.atlassian.net"
user_email: "your.email@company.com"
api_token: "your-api-token"
include_attachments: false
download_locally: true

# AWS S3 Configuration (optional)
upload_to_s3:
  aws_endpoint_url: ""
  aws_region: "us-east-1"
  s3_bucket: "my-backup-bucket"
  s3_dir: "Atlassian/"
  aws_access_key: "your-access-key"
  aws_secret_key: "your-secret-key"
  aws_is_secure: true

# Google Cloud Storage Configuration (optional)
upload_to_gcp:
  gcp_project_id: "my-project-id"
  gcs_bucket: "my-backup-bucket"
  gcs_dir: "Atlassian/"
  gcp_service_account_key: "/path/to/service-account-key.json"

# Azure Blob Storage Configuration (optional)
upload_to_azure:
  azure_account_name: "mystorageaccount"
  azure_container: "my-backup-container"
  azure_dir: "Atlassian/"
  azure_connection_string: "DefaultEndpointsProtocol=https;AccountName=..."
  azure_account_key: ""

# Custom Filename (optional)
# Supports placeholders:
# - {timestamp} - Current timestamp (DDMMYYYY_HHMM)
# - {date} - Current date (YYYY-MM-DD)
# - {time} - Current time (HHMM)
# - {uuid} - UUID from backup URL
# - {type} - Backup type (jira/confluence)
custom_filename:
  jira: "jira.{timestamp}"
  confluence: "confluence.{timestamp}"
```

#### Configuration wizard

For interactive setup, run:
```bash
python -m jira_backup -w
```

This will guide you through setting up basic Jira credentials and S3 configuration.

## 🚀 Usage

### Manual Backup

```bash
# Backup Jira (default)
python -m jira_backup -j

# Backup Confluence
python -m jira_backup -c

# Run configuration wizard
python -m jira_backup -w
```

### Automated Scheduling

Set up scheduled backups using system schedulers:

```bash
# Setup automated Jira backup every 4 days at 10:00 AM (default)
python -m jira_backup -s

# Setup automated Confluence backup every 7 days at 2:30 PM  
python -m jira_backup -s --schedule-days 7 --schedule-time 14:30 --schedule-service confluence

# Setup automated Jira backup every 2 days at 6:00 AM
python -m jira_backup -s --schedule-days 2 --schedule-time 06:00 --schedule-service jira
```

This will create:
- **Linux/macOS**: A cron job in your crontab
- **Windows**: A scheduled task in Task Scheduler

Scheduled tasks store an absolute config path.
If you do not pass `-C` or `--config`,
the scheduler uses `config.yaml` from the directory where you ran the scheduling command.

### Command Line Options

| Option               | Description                                                               |
|----------------------|---------------------------------------------------------------------------|
| `-j, --jira`         | Backup Jira (default if no service specified)                             |
| `-c, --confluence`   | Backup Confluence                                                         |
| `-C, --config`       | Path to the config file (default: `config.yaml` in the current directory) |
| `-w, --wizard`       | Run configuration wizard                                                  |
| `-s, --schedule`     | Setup automated scheduled backup                                          |
| `--schedule-days`    | Frequency in days for scheduled backup (default: 4)                       |
| `--schedule-time`    | Time for scheduled backup in HH:MM format (default: 10:00)                |
| `--schedule-service` | Service for scheduled backup (jira/confluence, default: jira)             |

## 🔧 Advanced Configuration

### Minimal Configuration

If you only want to download backups locally without cloud storage,
simply omit the `upload_to_xxx` sections:

```yaml
---
host_url: "your-instance.atlassian.net"
user_email: "your.email@company.com"
api_token: "your-api-token"
include_attachments: false
download_locally: true
```

### Multiple Cloud Providers

You can configure multiple cloud storage providers simultaneously - the script will upload to all configured destinations:

```yaml
upload_to_s3:
  s3_bucket: "my-s3-bucket"
  # ... S3 config

upload_to_gcp:
  gcs_bucket: "my-gcs-bucket"
  # ... GCP config

upload_to_azure:
  azure_container: "my-azure-container"
  # ... Azure config
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📝 Changelog

- **2025-06-24**: Added separate cron schedules for Jira and Confluence backups
- **2025-06-24**: Made cloud storage configuration sections optional
- **2025-06-24**: Added automated scheduling support for backup tasks
- **2025-06-23**: Added Google Cloud Storage and Azure Blob Storage support
- **2020-09-04**: Added Confluence backup support
- **2019-01-16**: Updated to use API tokens instead of passwords

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original concept inspired by [Atlassian Labs' automatic-cloud-backup](https://bitbucket.org/atlassianlabs/automatic-cloud-backup/)
- Thanks to all contributors who have helped improve this project

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/jira-backup-py/issues)

---

**Note**: This tool is not officially supported by Atlassian. Use at your own risk and always verify your backups are working correctly.
