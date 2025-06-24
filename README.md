# Jira Backup Python

[![datree-badge](https://s3.amazonaws.com/catalog.static.datree.io/datree-badge-28px.svg)](https://datree.io/?src=badge)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python-based backup solution for Atlassian Cloud Jira and Confluence instances with multi-cloud storage support and automated scheduling.

## 🚀 Features

- **Automated Backups**: Schedule periodic backups for Jira and Confluence
- **Multi-Cloud Support**: Upload backups to AWS S3, Google Cloud Storage, or Azure Blob Storage
- **Flexible Scheduling**: Built-in scheduler with cron expression support
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Easy Configuration**: YAML-based configuration with environment variable support
- **Secure**: API token authentication and encrypted cloud storage
- **Retention Management**: Automatic cleanup of old backups based on retention policies

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

4. **Configure the application**
   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml with your settings
   ```

## ⚙️ Configuration

### Basic Configuration

```yaml
jira:
  url: "https://your-instance.atlassian.net"
  username: "your.email@company.com"
  api_token: "your-api-token"
  backup_path: "/backups/jira"

confluence:
  url: "https://your-instance.atlassian.net/wiki"
  username: "your.email@company.com"
  api_token: "your-api-token"
  backup_path: "/backups/confluence"

backup:
  retention_days: 30
  compression: true
  include_attachments: true
```

### Cloud Storage Configuration (Optional)

Configure one or more cloud storage providers:

**AWS S3:**
```yaml
storage:
  provider: "aws"
  aws:
    bucket_name: "my-backup-bucket"
    region: "us-east-1"
    access_key_id: ${AWS_ACCESS_KEY_ID}
    secret_access_key: ${AWS_SECRET_ACCESS_KEY}
```

**Google Cloud Storage:**
```yaml
storage:
  provider: "gcp"
  gcp:
    bucket_name: "my-backup-bucket"
    project_id: "my-project-id"
    credentials_path: "/path/to/service-account.json"
```

**Azure Blob Storage:**
```yaml
storage:
  provider: "azure"
  azure:
    container_name: "my-backup-container"
    account_name: "mystorageaccount"
    account_key: ${AZURE_STORAGE_KEY}
```

### Automated Scheduling

```yaml
scheduler:
  enabled: true
  jira_schedule: "0 2 * * *"      # Daily at 2 AM
  confluence_schedule: "0 3 * * *" # Daily at 3 AM
```

## 🚀 Usage

### Manual Backup

```bash
# Backup both Jira and Confluence
python backup.py

# Backup only Jira
python backup.py --service jira

# Backup only Confluence
python backup.py --service confluence

# Test mode (verify configuration without uploading)
python backup.py --test
```

### Automated Scheduling

Run the scheduler to enable automated backups:

```bash
# Run scheduler in foreground
python scheduler.py

# Run scheduler as a background service (Linux/macOS)
nohup python scheduler.py > scheduler.log 2>&1 &

# Or use the provided systemd service file (Linux)
sudo systemctl enable jira-backup-scheduler
sudo systemctl start jira-backup-scheduler
```

### Quick Setup Commands

For backward compatibility with the original setup commands:

```bash
# Setup automated Jira backup every 4 days at 10:00 AM
python backup.py -s

# Setup automated Confluence backup every 7 days at 2:30 PM  
python backup.py -s --schedule-days 7 --schedule-time 14:30 --schedule-service confluence
```

## 🐳 Docker Support

```bash
# Build the image
docker build -t jira-backup-py .

# Run a manual backup
docker run -v $(pwd)/config.yaml:/app/config.yaml jira-backup-py

# Run the scheduler
docker run -d \
  --name jira-backup-scheduler \
  --restart unless-stopped \
  -v $(pwd)/config.yaml:/app/config.yaml \
  jira-backup-py python scheduler.py
```

## 📚 Documentation

Comprehensive documentation is available at [https://yourusername.github.io/jira-backup-py/](https://yourusername.github.io/jira-backup-py/)

- [Installation Guide](docs/installation.md)
- [Configuration Reference](docs/configuration.md)
- [Cloud Storage Setup](docs/cloud-storage.md)
- [Scheduling Guide](docs/scheduling.md)
- [API Reference](docs/api-reference.md)

## 🔧 Advanced Features

### Environment Variables

Sensitive values can be stored as environment variables:

```bash
export JIRA_API_TOKEN="your-token"
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

### Retention Policies

Configure automatic cleanup of old backups:

```yaml
backup:
  retention_days: 30  # Keep backups for 30 days
  retention_count: 10 # Keep last 10 backups (optional)
```

### Notifications

Get notified about backup status:

```yaml
scheduler:
  notifications:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    from_email: "backup@example.com"
    to_email: "admin@example.com"
    on_failure: true
    on_success: false
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](docs/contributing.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 Changelog

- **2025-06-24**: Added separate cron schedules for Jira and Confluence
- **2025-06-24**: Made cloud storage configuration sections optional
- **2025-06-24**: Added built-in scheduler with cron expression support
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
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/jira-backup-py/discussions)
- **Documentation**: [Project Documentation](https://yourusername.github.io/jira-backup-py/)

---

**Note**: This tool is not officially supported by Atlassian. Use at your own risk and always verify your backups are working correctly.