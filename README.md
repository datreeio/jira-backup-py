[![datree-badge](https://s3.amazonaws.com/catalog.static.datree.io/datree-badge-28px.svg)](https://datree.io/?src=badge)
# Introduction
Jira and Confluence are not (officially) supporting the option of creating automatic backups for their cloud instance.
This project was created to provide a fully automated infrastructure for backing up Atlassian Cloud Jira or Confluence instances on a periodic basis. 

There are shell and bash scripts out there, which were created in order to download the backup file locally without the use of the "backup manager" UI, 
but most of them are not maintained and throwing errors. So, this project is aiming for full backup automation, and therefore this is the features road map: 

:white_check_mark: Create a script in python  
:white_check_mark: Support creating config.json from user input ('wizard')   
:white_check_mark: Download backup file locally  
:white_check_mark: Add an option to stream backup file to S3  
:white_check_mark: Check how to manually create a cron task on OS X / Linux  
:white_check_mark: Check how to manually create a schedule task on windows  
:black_square_button: Support adding cron / scheduled task from script    

# Installation
## Prerequisite:  
:heavy_plus_sign: python 2.7.x or python 3.x.x  
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
5. Run backup.py script with the flag '-j' to backup Jira or '-c' to backup Confluence  
```
$(venv) python backup.py 
```  
![Screenshot](https://github.com/datreeio/jira-backup-py/blob/master/screenshots/terminal.png)  

## What's next?
It depends on your needs. I, for example, use this script together with [serverless](https://serverless.com/) to create a periodic [AWS lambda](https://aws.amazon.com/lambda/) which triggered every 4 days, creating a backup and upload it directly to S3.  

There is a more "stupid" option to get the same result - by creating a cron / scheduled task on your local machine:  
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
* 04 SEP 2020 - Support Confluence backup  
* 16 JAN 2019 - Updated script to work w/ [API token](https://confluence.atlassian.com/cloud/api-tokens-938839638.html), instead personal Jira user name and password  

# Resources:
:heavy_plus_sign: [JIRA support - How to Automate Backups for JIRA Cloud applications](https://confluence.atlassian.com/jirakb/how-to-automate-backups-for-jira-cloud-applications-779160659.html)  
:heavy_plus_sign: [Atlassian Labs' automatic-cloud-backup script](https://bitbucket.org/atlassianlabs/automatic-cloud-backup/src/d43ca5f33192e78b2e1869ab7c708bb32bfd7197/backup.ps1?at=master&fileviewer=file-view-default)  
:heavy_plus_sign: [A more maintainable version of Atlassian Labs' script](https://github.com/mattock/automatic-cloud-backup)  
