import os
import json


def create_config():
    jira_host = raw_input("What is your jira host name? ")
    user = raw_input("What is your jira user name? ")
    password = raw_input("What is your jira password? ")
    attachments = raw_input("Do you want to include attachments? (true / false) ")
    download_locally = raw_input("Do you want to download the backup file locally? (true / false) ")
    custom_config = {
        'JIRA_HOST': jira_host,
        'INCLUDE_ATTACHMENTS': attachments.lower(),
        'JIRA_USER': user,
        'JIRA_PASS': password,
        'DOWNLOAD_LOCALLY': download_locally.lower(),
        'UPLOAD_TO_S3': {
            'S3_BUCKET': "",
            'AWS_ACCESS_KEY': "",
            'AWS_SECRET_KEY': ""
        }
    }
    upload_backup = raw_input("Do you want to upload the backup file to S3? (true / false) ")
    if upload_backup.lower() == 'true':
        custom_config['UPLOAD_TO_S3']['S3_BUCKET'] = raw_input("What is the S3 bucket name? ")
        custom_config['UPLOAD_TO_S3']['AWS_ACCESS_KEY'] = raw_input("What is your AWS access key? ")
        custom_config['UPLOAD_TO_S3']['AWS_SECRET_KEY'] = raw_input("What is your AWS secret key? ")

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    with open(config_path, 'w+') as config_file:
        json.dump(custom_config, config_file)
