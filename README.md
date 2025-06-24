# Jira Backup Python

[![datree-badge](https://s3.amazonaws.com/catalog.static.datree.io/datree-badge-28px.svg)](https://datree.io/?src=badge)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
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

- Python 3.7 or higher
- Atlassian Cloud account (Jira and/or Confluence)
- API token from [Atlassian](https://id.atlassian.com/manage/api-tokens)
- (Optional) Cloud storage account: AWS, Google Cloud, or Azure

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/jira-backup-py.git
   cd jira-backup-py
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate API token**
   - Go to [Atlassian API Tokens](https://id.atlassian.com/manage/api-tokens) and create a token
   
5. **Configure the application**
   - Create a `config.yaml` file with your settings (see Configuration section below)
   - Or run the configuration wizard: `python backup.py -w`

## ⚙️ Configuration

### Configuration File Setup

Create a `config.yaml` file with your settings:

```yaml
---
HOST_URL: "your-instance.atlassian.net"
USER_EMAIL: "your.email@company.com"
API_TOKEN: "your-api-token"
INCLUDE_ATTACHMENTS: false
DOWNLOAD_LOCALLY: true

# AWS S3 Configuration (optional)
UPLOAD_TO_S3:
  S3_BUCKET: "my-backup-bucket"
  AWS_ACCESS_KEY_ID: "your-access-key"
  AWS_SECRET_ACCESS_KEY: "your-secret-key"
  AWS_S3_REGION: "us-east-1"

# Google Cloud Storage Configuration (optional)
UPLOAD_TO_GCP:
  GCP_PROJECT_ID: "my-project-id"
  GCS_BUCKET: "my-backup-bucket"
  GCP_SERVICE_ACCOUNT_KEY: "/path/to/service-account-key.json"

# Azure Blob Storage Configuration (optional)
UPLOAD_TO_AZURE:
  AZURE_ACCOUNT_NAME: "mystorageaccount"
  AZURE_CONTAINER: "my-backup-container"
  AZURE_CONNECTION_STRING: "DefaultEndpointsProtocol=https;AccountName=..."
  # OR use AZURE_ACCOUNT_KEY instead of connection string
  # AZURE_ACCOUNT_KEY: "your-account-key"
```

### Configuration Wizard

For interactive setup, run:
```bash
python backup.py -w
```

This will guide you through setting up basic Jira credentials and S3 configuration.

## 🚀 Usage

### Manual Backup

```bash
# Backup Jira (default)
python backup.py -j

# Backup Confluence
python backup.py -c

# Run configuration wizard
python backup.py -w
```

### Automated Scheduling

Set up scheduled backups using system schedulers:

```bash
# Setup automated Jira backup every 4 days at 10:00 AM (default)
python backup.py -s

# Setup automated Confluence backup every 7 days at 2:30 PM  
python backup.py -s --schedule-days 7 --schedule-time 14:30 --schedule-service confluence

# Setup automated Jira backup every 2 days at 6:00 AM
python backup.py -s --schedule-days 2 --schedule-time 06:00 --schedule-service jira
```

This will create:
- **Linux/macOS**: A cron job in your crontab
- **Windows**: A scheduled task in Task Scheduler

### Command Line Options

| Option | Description |
|--------|-------------|
| `-j, --jira` | Backup Jira (default if no service specified) |
| `-c, --confluence` | Backup Confluence |
| `-w, --wizard` | Run configuration wizard |
| `-s, --schedule` | Setup automated scheduled backup |
| `--schedule-days` | Frequency in days for scheduled backup (default: 4) |
| `--schedule-time` | Time for scheduled backup in HH:MM format (default: 10:00) |
| `--schedule-service` | Service for scheduled backup (jira/confluence, default: jira) |

## 🔧 Advanced Configuration

### Minimal Configuration

If you only want to download backups locally without cloud storage:

```yaml
---
HOST_URL: "your-instance.atlassian.net"
USER_EMAIL: "your.email@company.com"
API_TOKEN: "your-api-token"
INCLUDE_ATTACHMENTS: false
DOWNLOAD_LOCALLY: true
```

Simply omit the `UPLOAD_TO_XXX` sections you don't need.

### Multiple Cloud Providers

You can configure multiple cloud storage providers simultaneously - the script will upload to all configured destinations:

```yaml
UPLOAD_TO_S3:
  S3_BUCKET: "my-s3-bucket"
  # ... S3 config

UPLOAD_TO_GCP:
  GCS_BUCKET: "my-gcs-bucket"
  # ... GCP config

UPLOAD_TO_AZURE:
  AZURE_CONTAINER: "my-azure-container"
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