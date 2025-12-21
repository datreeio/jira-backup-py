import json
import yaml
import time
import os
import argparse
import requests
import boto3
from boto3.s3.transfer import TransferConfig
from google.cloud import storage
from azure.storage.blob import BlobServiceClient
import wizard
import platform
import subprocess
import sys


def read_config(path=''):
    if path == '':
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(path, 'r') as config_file:
        return yaml.full_load(config_file)


class Atlassian:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.auth = (config['USER_EMAIL'], config['API_TOKEN'])
        self.session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})
        self.payload = {"cbAttachments": self.config['INCLUDE_ATTACHMENTS'], "exportToCloud": "true"}
        self.start_confluence_backup = 'https://{}/wiki/rest/obm/1.0/runbackup'.format(self.config['HOST_URL'])
        self.start_jira_backup = 'https://{}/rest/backup/1/export/runbackup'.format(self.config['HOST_URL'])
        self.backup_status = {}
        self.wait = 10

    def create_confluence_backup(self):
        backup = self.session.post(self.start_confluence_backup, data=json.dumps(self.payload))

        if backup.status_code not in (200, 406):
            raise Exception(backup, backup.text)

        print('-> Backup process successfully started')
        confluence_backup_status = 'https://{}/wiki/rest/obm/1.0/getprogress'.format(self.config['HOST_URL'])
        time.sleep(self.wait)
        while 'fileName' not in self.backup_status.keys():
            self.backup_status = json.loads(self.session.get(confluence_backup_status).text)
            print('Current status: {progress}; {description}'.format(
                progress=self.backup_status['alternativePercentage'],
                description=self.backup_status['currentStatus']))
            time.sleep(self.wait)
        return 'https://{url}/wiki/download/{file_name}'.format(
            url=self.config['HOST_URL'], file_name=self.backup_status['fileName'])

    def create_jira_backup(self):
        backup = self.session.post(self.start_jira_backup, data=json.dumps(self.payload))
        if backup.status_code != 200:
            raise Exception(backup, backup.text)
        else:
            task_id = json.loads(backup.text)['taskId']
            print('-> Backup process successfully started: taskId={}'.format(task_id))
            jira_backup_status = 'https://{jira_host}/rest/backup/1/export/getProgress?taskId={task_id}'.format(
                jira_host=self.config['HOST_URL'], task_id=task_id)
            time.sleep(self.wait)
            while 'result' not in self.backup_status.keys():
                self.backup_status = json.loads(self.session.get(jira_backup_status).text)
                print('Current status: {status} {progress}; {description}'.format(
                    status=self.backup_status['status'],
                    progress=self.backup_status['progress'],
                    description=self.backup_status['description']))
                time.sleep(self.wait)
            return '{prefix}/{result_id}'.format(
                prefix='https://' + self.config['HOST_URL'] + '/plugins/servlet', result_id=self.backup_status['result'])

    def download_file(self, url, local_filename):
        print('-> Downloading file from URL: {}'.format(url))
        r = self.session.get(url, stream=True)
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups', local_filename)
        with open(file_path, 'wb') as file_:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    file_.write(chunk)
        print(file_path)

    def stream_to_s3(self, url, remote_filename):
        print('-> Streaming to S3')

        if self.config['UPLOAD_TO_S3']['AWS_ACCESS_KEY'] == '':
            s3_client = boto3.client('s3')
        else:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config['UPLOAD_TO_S3']['AWS_ACCESS_KEY'],
                aws_secret_access_key=self.config['UPLOAD_TO_S3']['AWS_SECRET_KEY'],
                region_name=self.config['UPLOAD_TO_S3']['AWS_REGION'],
                endpoint_url=self.config['UPLOAD_TO_S3']['AWS_ENDPOINT_URL'],
                use_ssl=self.config['UPLOAD_TO_S3']['AWS_IS_SECURE']
            )

        bucket_name = self.config['UPLOAD_TO_S3']['S3_BUCKET']
        r = self.session.get(url, stream=True)
        if r.status_code == 200:
            key = "{s3_bucket}{s3_filename}".format(
                s3_bucket=self.config['UPLOAD_TO_S3']['S3_DIR'],
                s3_filename=remote_filename
            )

            content_length = int(r.headers.get('Content-Length', 0))

            config = TransferConfig(
                multipart_threshold=content_length + 1,
                max_concurrency=1,
                use_threads=False
            )

            s3_client.upload_fileobj(
                Fileobj=r.raw,
                Bucket=bucket_name,
                Key=key,
                ExtraArgs={'ContentType': r.headers['content-type']},
                Config=config
            )

    def stream_to_gcs(self, url, remote_filename):
        print('-> Streaming to GCS')
        
        if self.config['UPLOAD_TO_GCP']['GCP_SERVICE_ACCOUNT_KEY']:
            client = storage.Client.from_service_account_json(
                self.config['UPLOAD_TO_GCP']['GCP_SERVICE_ACCOUNT_KEY'],
                project=self.config['UPLOAD_TO_GCP']['GCP_PROJECT_ID']
            )
        else:
            client = storage.Client(project=self.config['UPLOAD_TO_GCP']['GCP_PROJECT_ID'])
        
        bucket_name = self.config['UPLOAD_TO_GCP']['GCS_BUCKET']
        bucket = client.bucket(bucket_name)
        
        r = self.session.get(url, stream=True)
        if r.status_code == 200:
            blob_name = "{gcs_dir}{filename}".format(
                gcs_dir=self.config['UPLOAD_TO_GCP']['GCS_DIR'],
                filename=remote_filename
            )
            
            blob = bucket.blob(blob_name)
            blob.content_type = r.headers.get('content-type', 'application/zip')
            
            blob.upload_from_file(r.raw, content_type=blob.content_type)

    def stream_to_azure(self, url, remote_filename):
        print('-> Streaming to Azure Blob Storage')
        
        if self.config['UPLOAD_TO_AZURE']['AZURE_CONNECTION_STRING']:
            blob_service_client = BlobServiceClient.from_connection_string(
                self.config['UPLOAD_TO_AZURE']['AZURE_CONNECTION_STRING']
            )
        else:
            account_url = f"https://{self.config['UPLOAD_TO_AZURE']['AZURE_ACCOUNT_NAME']}.blob.core.windows.net"
            blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=self.config['UPLOAD_TO_AZURE']['AZURE_ACCOUNT_KEY']
            )
        
        container_name = self.config['UPLOAD_TO_AZURE']['AZURE_CONTAINER']
        
        r = self.session.get(url, stream=True)
        if r.status_code == 200:
            blob_name = "{azure_dir}{filename}".format(
                azure_dir=self.config['UPLOAD_TO_AZURE']['AZURE_DIR'],
                filename=remote_filename
            )
            
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(
                r.raw,
                content_type=r.headers.get('content-type', 'application/zip'),
                overwrite=True
            )


def setup_scheduled_task(frequency_days=4, time_hour=10, time_minute=0, service_type='jira'):
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    system = platform.system().lower()
    
    if system in ['linux', 'darwin']:
        return setup_cron_task(script_path, script_dir, frequency_days, time_hour, time_minute, service_type)
    elif system == 'windows':
        return setup_windows_task(script_path, script_dir, frequency_days, time_hour, time_minute, service_type)
    else:
        raise Exception(f"Unsupported operating system: {system}")


def setup_cron_task(script_path, script_dir, frequency_days, time_hour, time_minute, service_type):
    python_path = sys.executable
    service_flag = '-j' if service_type == 'jira' else '-c'
    
    cron_command = f"{time_minute} {time_hour} */{frequency_days} * * cd {script_dir} && {python_path} {script_path} {service_flag}"
    
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing_cron = result.stdout if result.returncode == 0 else ""
        
        # Remove only the cron entry for the same service type
        lines = existing_cron.strip().split('\n') if existing_cron.strip() else []
        updated_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
            
            # Check if this is a comment line for jira-backup-py
            if 'jira-backup-py automated backup' in line and f'({service_type})' in line:
                # Check if the next line contains the cron command for this service
                if i + 1 < len(lines) and service_flag in lines[i + 1]:
                    skip_next = True  # Skip both the comment and the command
                    print(f"-> Updating existing {service_type} backup schedule...")
                    continue
            
            updated_lines.append(line)
        
        existing_cron = '\n'.join(updated_lines) + '\n' if updated_lines else ""
        new_cron = existing_cron + f"# jira-backup-py automated backup ({service_type})\n{cron_command}\n"
        
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_cron)
        
        if process.returncode == 0:
            print(f"-> Successfully scheduled {service_type} backup to run every {frequency_days} days at {time_hour:02d}:{time_minute:02d}")
            return True
        else:
            print("-> Failed to create cron job")
            return False
            
    except Exception as e:
        print(f"-> Error setting up cron job: {e}")
        return False


def setup_windows_task(script_path, script_dir, frequency_days, time_hour, time_minute, service_type):
    python_path = sys.executable
    service_flag = '-j' if service_type == 'jira' else '-c'
    task_name = f"jira-backup-py-{service_type}"
    
    cmd = [
        'schtasks', '/create',
        '/tn', task_name,
        '/sc', 'DAILY',
        '/mo', str(frequency_days),
        '/tr', f'"{python_path}" "{script_path}" {service_flag}',
        '/st', f'{time_hour:02d}:{time_minute:02d}',
        '/f'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"-> Successfully scheduled {service_type} backup to run every {frequency_days} days at {time_hour:02d}:{time_minute:02d}")
            return True
        else:
            print(f"-> Failed to create scheduled task: {result.stderr}")
            return False
    except Exception as e:
        print(f"-> Error setting up scheduled task: {e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', type=str, dest='config_file', default='', help='path to config file')
    parser.add_argument('-w', action='store_true', dest='wizard', help='activate config wizard')
    parser.add_argument('-c', action='store_true', dest='confluence', help='activate confluence backup')
    parser.add_argument('-j', action='store_true', dest='jira', help='activate jira backup')
    parser.add_argument('-s', '--schedule', action='store_true', dest='schedule', help='setup automated scheduled backup')
    parser.add_argument('--schedule-days', type=int, default=4, help='frequency in days for scheduled backup (default: 4)')
    parser.add_argument('--schedule-time', type=str, default='10:00', help='time for scheduled backup in HH:MM format (default: 10:00)')
    parser.add_argument('--schedule-service', type=str, choices=['jira', 'confluence'], default='jira', help='service type for scheduled backup (default: jira)')
    args = parser.parse_args()
    # print('debug command-line: {}'.format(args))
    
    if args.wizard:
        wizard.create_config()
    
    if args.schedule:
        try:
            time_parts = args.schedule_time.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError("Invalid time format")
                
            setup_scheduled_task(
                frequency_days=args.schedule_days,
                time_hour=hour,
                time_minute=minute,
                service_type=args.schedule_service
            )
            print("-> Scheduled task setup completed")
            exit(0)
        except ValueError as e:
            print(f"-> Error: Invalid time format. Use HH:MM format (e.g., 10:30)")
            exit(1)
        except Exception as e:
            print(f"-> Error setting up scheduled task: {e}")
            exit(1)
    
    config = read_config(args.config_file)

    if config['HOST_URL'] == 'something.atlassian.net':
        raise ValueError('You forgot to edit config.yaml or to run the backup script with "-w" flag')

    print('-> Starting backup; include attachments: {}'.format(config['INCLUDE_ATTACHMENTS']))
    atlass = Atlassian(config)
    if args.confluence: backup_url = atlass.create_confluence_backup()
    else: backup_url = atlass.create_jira_backup()

    print('-> Backup URL: {}'.format(backup_url))
    file_name = '{timestemp}_{uuid}.zip'.format(
        timestemp=time.strftime('%d%m%Y_%H%M'), uuid=backup_url.split('/')[-1].replace('?fileId=', ''))

    if config['DOWNLOAD_LOCALLY'] == 'true':
        atlass.download_file(backup_url, file_name)

    if 'UPLOAD_TO_S3' in config and config['UPLOAD_TO_S3'].get('S3_BUCKET', '') != '':
        atlass.stream_to_s3(backup_url, file_name)
    
    if 'UPLOAD_TO_GCP' in config and config['UPLOAD_TO_GCP'].get('GCS_BUCKET', '') != '':
        atlass.stream_to_gcs(backup_url, file_name)
    
    if 'UPLOAD_TO_AZURE' in config and config['UPLOAD_TO_AZURE'].get('AZURE_CONTAINER', '') != '':
        atlass.stream_to_azure(backup_url, file_name)
