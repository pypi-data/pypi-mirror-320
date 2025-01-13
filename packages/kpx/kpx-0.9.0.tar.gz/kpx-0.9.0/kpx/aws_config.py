import configparser
import os
import boto3

from os.path import expanduser
from .utils import Output, IniUtils


class AwsConfigManager:
    def __init__(self, file_credentials, file_config):
        self.file_credentials = file_credentials
        self.file_config = file_config

        self.creds = configparser.ConfigParser()
        self.creds.read(file_credentials)

        self.cfg = configparser.ConfigParser()
        self.cfg.read(file_config)

    @staticmethod
    def aws_region():
        return os.getenv('AWS_REGION', 'us-east-1')

    @staticmethod
    def account_id():
        client = boto3.client('sts')
        accId = client.get_caller_identity()['Account']

        return accId

    def update_credentials(self, profile, access_key, secret_key):
        if profile not in self.creds:
            self.creds.update({profile: {
                'aws_access_key_id': '',
                'aws_secret_access_key': '',
            }})

        for key in self.creds[profile]:
            new_value = ''
            if key == 'aws_access_key_id' and access_key is not None:
                new_value = access_key
            if key == 'aws_secret_access_key' and secret_key is not None:
                new_value = secret_key

            self.creds[profile][key] = new_value

        return self

    def update_config(self, profile, region, output):
        if profile != 'default':
            profile = f'profile {profile}'

        self.cfg.update({
            profile: {
                'region': region,
                'output': output,
            }
        })

    def get_credentials(self, profile_name):
        data = {}
        if profile_name in self.creds:
            for key in self.creds[profile_name]:
                data.update({key: self.creds[profile_name][key]})

        return data

    def get_config(self, profile_name):
        data = {}
        profile_string = f'profile {profile_name}' if profile_name != 'default' else 'default'
        if profile_string in self.cfg:
            for key in self.cfg[profile_string]:
                data.update({key: self.cfg[profile_string][key]})

        return data

    def write_credentials_file(self):
        with open(self.file_credentials, 'w') as file:
            self.creds.write(file)

        return self

    def write_config_file(self):
        with open(self.file_config, 'w') as file:
            self.cfg.write(file)

        return self

    @staticmethod
    def generate_config(aws_profile, region, output):
        Output.header('Updating ~/.aws/config file')
        user_home_directory = expanduser('~')

        awc = AwsConfigManager(
            f'{user_home_directory}/.aws/credentials',
            f'{user_home_directory}/.aws/config',
        )

        IniUtils.check_directory_exists(f'{user_home_directory}/.aws/')

        awc.update_config(aws_profile, region, output)
        awc.write_config_file()

    @staticmethod
    def generate_credentials(aws_profile, key, secret):
        Output.header('Updating ~/.aws/credentials file')
        user_home_directory = expanduser('~')

        awc = AwsConfigManager(
            f'{user_home_directory}/.aws/credentials',
            f'{user_home_directory}/.aws/config',
        )

        IniUtils.check_directory_exists(f'{user_home_directory}/.aws/')

        awc.update_credentials(aws_profile, key, secret)
        awc.write_credentials_file()
