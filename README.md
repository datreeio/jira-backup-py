[![datree-badge](https://s3.amazonaws.com/catalog.static.datree.io/datree-badge-28px.svg)](https://datree.io/?src=badge)
# Introduction
Jira and Confluence are not (officially) supporting the option of creating automatic backups for their cloud instance.
This project was created to provide a fully automated infrastructure for backing up Atlassian Cloud Jira or Confluence instances on a periodic basis. 

There are shell and bash scripts out there, which were created in order to download the backup file locally without the use of the "backup manager" UI, 
but most of them are not maintained and throwing errors. So, this project is aiming for full backup automation, and therefore this is the features road map: 

:white_check_mark: Create a script in python  
:white_check_mark: Support creating config.yaml from user input ('wizard')   
:white_check_mark: Download backup file locally  
:white_check_mark: Add an option to stream backup file to S3  
:white_check_mark: Add an option to stream backup file to Google Cloud Storage
:white_check_mark: Add an option to stream backup file to Azure Blob Storage
:white_check_mark: Check how to manually create a cron task on OS X / Linux  
:white_check_mark: Check how to manually create a schedule task on windows  
:white_check_mark: Support adding cron / scheduled task from script    

# Installation
## Prerequisite:  
:heavy_plus_sign: python 3  
:heavy_plus_sign: [virtualenv](https://pypi.org/project/virtualenv/) installed globally (pip install virtualenv)  

## Instructions:
1. Create and start [virtual environment](https://python-guide-cn.readthedocs.io/en/latest/dev/virtualenvs.html) (in this example, the virtualenv will be called "venv")  
2. Install requirements  
```
$(venv) pip install -r requirements.txt
```  
3. Generate an API token at https://id.atlassian.com/manage/api-tokens  
![Screenshot](https://github.com/datreeio/jira-backup-py/blob/master/screenshots/atlassian-api-token.png)  
4. Fill the details at the [config.yaml file](https://github.com/datreeio/jira-backup-py/blob/master/config.json) or run the backup.py script with '-w' flag
5. Configure your preferred cloud storage provider(s) in config.yaml:
   - **For AWS S3**: Set AWS credentials and S3_BUCKET
   - **For Google Cloud**: Set GCP_PROJECT_ID, GCS_BUCKET, and optionally GCP_SERVICE_ACCOUNT_KEY
   - **For Azure**: Set AZURE_ACCOUNT_NAME, AZURE_CONTAINER, and either AZURE_CONNECTION_STRING or AZURE_ACCOUNT_KEY
   
   **Note**: Cloud storage sections (`UPLOAD_TO_S3`, `UPLOAD_TO_GCP`, `UPLOAD_TO_AZURE`) are optional. You can delete any sections you don't need from your config.yaml file. For example, if you only want to download backups locally, you can remove all three upload sections.
6. Run backup.py script with the flag '-j' to backup Jira or '-c' to backup Confluence  
```
$(venv) python backup.py 
```  
![Screenshot](https://github.com/datreeio/jira-backup-py/blob/master/screenshots/terminal.png)

## Automated Scheduling
You can now automatically set up scheduled backups using the built-in scheduling feature:

```bash
# Setup automated Jira backup every 4 days at 10:00 AM
python backup.py -s

# Setup automated Confluence backup every 7 days at 2:30 PM  
python backup.py -s --schedule-days 7 --schedule-time 14:30 --schedule-service confluence

# Setup automated Jira backup every 2 days at 6:00 AM
python backup.py -s --schedule-days 2 --schedule-time 06:00 --schedule-service jira
```

This will automatically create:
- **Linux/macOS**: A cron job in your crontab
- **Windows**: A scheduled task in Task Scheduler

The script automatically detects your operating system and creates the appropriate scheduled task.  

## Cloud Storage Support
The script supports multiple cloud storage providers:
- **AWS S3** - Configure `UPLOAD_TO_S3` section in config.yaml
- **Google Cloud Storage** - Configure `UPLOAD_TO_GCP` section in config.yaml  
- **Azure Blob Storage** - Configure `UPLOAD_TO_AZURE` section in config.yaml

You can use any combination of these providers - the script will upload to all configured destinations.

### Minimal Configuration Example
If you only want to download backups locally without any cloud storage:
```yaml
--- 
HOST_URL: "your-instance.atlassian.net"
USER_EMAIL: "your.email@company.com"
API_TOKEN: "your-api-token"
INCLUDE_ATTACHMENTS: false
DOWNLOAD_LOCALLY: true
```

Simply omit any `UPLOAD_TO_XXX` sections you don't need - the script will skip those providers automatically.

## What's next?
It depends on your needs. You can use this script with any cloud provider or serverless platform. For example, use it with [serverless](https://serverless.com/) to create periodic functions on AWS Lambda, Google Cloud Functions, or Azure Functions that trigger backups and upload to your preferred cloud storage.

## Manual Scheduling (Alternative)
If you prefer to manually create scheduled tasks instead of using the automated scheduling feature, you can still create a cron / scheduled task on your local machine:  
* **OS X / Linux:** set a cron task with crontab 
``` 
echo "* * * * * cd %script dir% && %activate virtualenv% && python backup.py > %log name% 2>&1" | crontab -
```  
Example for adding a cron task which will run every 4 days, at 10:00  
```
echo "0 10 */4 * * cd ~/Dev/jira-backup-py && source venv/bin/activate && python backup.py > backup_script.log 2>&1" | crontab -
```  

* **Windows:** set a scheduled task with task scheduler  
``` 
schtasks /create /tn "%task name%" /sc DAILY /mo %number of days% /tr "%full path to win_task_wrapper.bat%" /st %start time%
```  
Example for adding a scheduled task which will run every 4 days, at 10:00  
``` 
schtasks /create /tn "jira-backup" /sc DAILY /mo 4 /tr "C:\jira-backup-py\win_task_wrapper.bat" /st 10:00
```  
# Changelog:
* 24 JUN 2025 - Added automated scheduling support for cron/scheduled tasks
* 24 JUN 2025 - Added support for Google Cloud Storage and Azure Blob Storage
* 04 SEP 2020 - Support Confluence backup  
* 16 JAN 2019 - Updated script to work w/ [API token](https://confluence.atlassian.com/cloud/api-tokens-938839638.html), instead personal Jira user name and password  

# Resources:
:heavy_plus_sign: [JIRA support - How to Automate Backups for JIRA Cloud applications](https://confluence.atlassian.com/jirakb/how-to-automate-backups-for-jira-cloud-applications-779160659.html)  
:heavy_plus_sign: [Atlassian Labs' automatic-cloud-backup script](https://bitbucket.org/atlassianlabs/automatic-cloud-backup/src/d43ca5f33192e78b2e1869ab7c708bb32bfd7197/backup.ps1?at=master&fileviewer=file-view-default)  
:heavy_plus_sign: [A more maintainable version of Atlassian Labs' script](https://github.com/mattock/automatic-cloud-backup)  
