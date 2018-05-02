import json
import time
import os
import argparse
import requests
from requests.auth import HTTPBasicAuth
import boto
from boto.s3.key import Key
import wizard


def read_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    with open(config_path, 'r') as config_file:
        return json.load(config_file)


class Jira:
    def __init__(self, config):
        self.config = config
        self.__auth = HTTPBasicAuth(self.config['JIRA_USER'], self.config['JIRA_PASS'])
        self.URL_run_backup = 'https://{}/rest/backup/1/export/runbackup'.format(self.config['JIRA_HOST'])
        self.URL_download = 'https://{}/plugins/servlet'.format(self.config['JIRA_HOST'])
        self.backup_status = {}
        self.wait = 30

    def create_backup(self):
        print('-> Starting backup; include attachments: {}'.format(self.config['INCLUDE_ATTACHMENTS']))
        payload = {"cbAttachments": self.config['ATTACHMENTS'], "exportToCloud": "true"}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        
        backup = requests.post(self.URL_run_backup, data=json.dumps(payload), headers=headers, auth=self.__auth)
        if backup.status_code != 200:
            raise Exception(backup, backup.text)
        else:
            task_id = json.loads(backup.text)['taskId']
            print('Backup process successfully started: taskId={}'.format(task_id))
            URL_backup_progress = 'https://{jira_host}/rest/backup/1/export/getProgress?taskId={task_id}'.format(
                jira_host=self.config['JIRA_HOST'], task_id=task_id)
            time.sleep(self.wait)
            while 'result' not in self.backup_status.keys():
                self.backup_status = json.loads(requests.get(URL_backup_progress, auth=self.__auth).text)
                print('Current status: {status} {progress}; {description}'.format(
                    status=self.backup_status['status'], 
                    progress=self.backup_status['progress'], 
                    description=self.backup_status['description']))
                time.sleep(self.wait)
            return '{prefix}/{resultId}'.format(prefix=self.URL_download, resultId=self.backup_status['result'])

    def download_file(self, url, local_filename):
        print('-> Downloading file from URL: {}'.format(url))
        r = requests.get(url, stream=True, auth=self.__auth)
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
        r = requests.get(url, stream=True, auth=self.__auth)
        if r.status_code == 200:
            k = Key(bucket)
            k.key = remote_filename
            k.content_type = r.headers['content-type']
            k.set_contents_from_string(r.content)
            return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action='store_true', dest='wizard', help='activate config wizard')
    if parser.parse_args().wizard:
        wizard.create_config() 
    config = read_config()

    if config['JIRA_HOST'] == 'something.atlassian.net':
        raise ValueError('You forgated to edit config.json or to run the backup script with "-w" flag')

    jira = Jira(config)
    backup_url = jira.create_backup()
    file_name = '{}.zip'.format(backup_url.split('/')[-1].replace('?fileId=', ''))
    
    if config['DOWNLOAD_LOCALLY'] == 'true':
        jira.download_file(backup_url, file_name)  

    if config['UPLOAD_TO_S3']['S3_BUCKET'] != '':
        jira.stream_to_s3(backup_url, file_name)
