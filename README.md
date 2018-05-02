# Introduction
JIRA are not (officially) supporting the option of creating automatic backups for their cloud instance.
This project was created to provide a fully automated infrastructure for backing up Atlassian Cloud JIRA instance on a periodic basis. 

There are shell and bash scripts out there, which were created in order to download the backup file locally without the use of the "backup manager" UI, 
but most of them are not maintained and throwing errors. So, this project is aiming for full backup automation, and therefore this is the features road map: 

:white_check_mark: Create a script in python  
:white_check_mark: Support creating config.json from user input ('wizard')   
:white_check_mark: Download backup file locally  
:white_check_mark: Add an option to stream backup file to S3  
:white_check_mark: Check how to create a cron task on OS X  
:black_square_button: Check how to create a cron task on windows  
:black_square_button: Add some tests  
:black_square_button: Support serveless function  

# Installation
### Prerequisite:  
:heavy_plus_sign: python 2.7.x  
:heavy_plus_sign: [virtualenv](https://virtualenv.pypa.io/en/stable/) installed globally  

### Instructions:
* Create [virtual environment](https://python-guide-cn.readthedocs.io/en/latest/dev/virtualenvs.html) (in this example, the virtualenv will be called "venv")  
* Install requirements  
```
pip install -r requirements.txt
```  
* Fill the details at the config.json file or run the backup.py script with '-w' flag  
* Run backup.py script  
```
$(venv) python backup.py 
```  

### What's next?
It depends on your needs. I, for example, use this script together with [serverless](https://serverless.com/) to create a periodic [AWS lambda](https://aws.amazon.com/lambda/) which triggered every 4 days, creating a backup and upload it directly to S3.  
There is a more "stupid" option to get the same result - by creating a cron task on your local machine:  
* set crontab task on OS X: 
``` 
echo "[* * * * *](https://crontab.guru/) cd %script_dir% && %activate_virtualenv% && python backup.py > backup_script.log 2>&1" | crontab -
```  
```
echo "0 10 */4 * * cd ~/Dev/jira-backup-py && source venv/bin/activate && python backup.py > backup_script.log 2>&1" | crontab -
``` 

# Resources:
:heavy_plus_sign: [JIRA support - How to Automate Backups for JIRA Cloud applications](https://confluence.atlassian.com/jirakb/how-to-automate-backups-for-jira-cloud-applications-779160659.html)  
:heavy_plus_sign: [Atlassian Labs' automatic-cloud-backup script](https://bitbucket.org/atlassianlabs/automatic-cloud-backup/src/d43ca5f33192e78b2e1869ab7c708bb32bfd7197/backup.ps1?at=master&fileviewer=file-view-default)  
:heavy_plus_sign: [A more maintainable version of this script](https://github.com/mattock/automatic-cloud-backup)  

