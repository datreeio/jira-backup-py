import json
import yaml
import time
import os
import argparse
import requests
import boto
from boto.s3.key import Key
import wizard
from time import gmtime, strftime


def read_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_config.yaml')
    with open(config_path, 'r') as config_file:
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
        if backup.status_code != 200:
            raise Exception(backup, backup.text)
        else:
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
            connect = boto.connect_s3()
        else:
            connect = boto.connect_s3(
                aws_access_key_id=self.config['UPLOAD_TO_S3']['AWS_ACCESS_KEY'], 
                aws_secret_access_key=self.config['UPLOAD_TO_S3']['AWS_SECRET_KEY']
                )

        bucket = connect.get_bucket(self.config['UPLOAD_TO_S3']['S3_BUCKET'])
        r = self.session.get(url, stream=True)
        if r.status_code == 200:
            k = Key(bucket)
            k.key = remote_filename
            k.content_type = r.headers['content-type']
            k.set_contents_from_string(r.content)
            return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action='store_true', dest='wizard', help='activate config wizard')
    parser.add_argument('-c', action='store_true', dest='confluence', help='activate confluence backup')
    parser.add_argument('-j', action='store_true', dest='jira', help='activate jira backup')
    # print('debug command-line: {}'.format(parser.parse_args()))
    if parser.parse_args().wizard:
        wizard.create_config()
    config = read_config()

    if config['HOST_URL'] == 'something.atlassian.net':
        raise ValueError('You forgated to edit config.json or to run the backup script with "-w" flag')

    print('-> Starting backup; include attachments: {}'.format(config['INCLUDE_ATTACHMENTS']))
    atlass = Atlassian(config)
    if parser.parse_args().confluence: backup_url = atlass.create_confluence_backup()
    else: backup_url = atlass.create_jira_backup()

    print('-> Backup URL: {}'.format(backup_url))
    file_name = '{timestemp}_{uuid}.zip'.format(
        timestemp=time.strftime('%d%m%Y_%H%M'), uuid=backup_url.split('/')[-1].replace('?fileId=', ''))

    if config['DOWNLOAD_LOCALLY'] == 'true':
        atlass.download_file(backup_url, file_name)

    if config['UPLOAD_TO_S3'][0]['S3_BUCKET'] != '':
        atlass.stream_to_s3(backup_url, file_name)