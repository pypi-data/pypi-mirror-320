from .utils import Output, expand_filters, calculate_age
from prettytable import PrettyTable


class AwsResourceQuery:
    def __init__(self, client):
        self.client = client

    def list_ec2(self, name_filter=None):
        table = PrettyTable()
        table.field_names = self.get_table_header()
        table.align['PrivateIP'] = 'r'
        table.align['PublicIP'] = 'r'
        table.align['Name'] = 'r'
        table.align['Age'] = 'r'

        ec2_instances = self.list_ec2_instances(name_filter)
        if len(ec2_instances) > 0:
            table.add_rows(ec2_instances)
            print(table.get_string())

    @staticmethod
    def get_table_header():
        return ["ID", "Name", "Type", "PublicIP", "PrivateIP", "Age", "State"]

    @staticmethod
    def get_instance_name_from_tags(tags):
        for item in tags:
            if item['Key'] == 'Name':
                return item['Value']

        return '---'

    def list_ec2_instances(self, name_filter=None):
        query_filters = expand_filters(name_filter)
        instances = []
        try:
            resp = self.client.describe_instances()
        except Exception as e:
            Output.error(e)
            return []

        for reservation in resp['Reservations']:
            for instance in reservation['Instances']:
                instance_name = ''
                if 'Tags' in instance:
                    instance_name = self.get_instance_name_from_tags(instance['Tags'])

                instance_state = instance['State']['Name']

                if name_filter:
                    # search by instance name
                    if 'name' in query_filters and query_filters['name'] not in instance_name.lower():
                        continue
                    if 'state' in query_filters and query_filters['state'] not in instance_state.lower():
                        continue

                data = {
                    'Id': instance['InstanceId'],
                    'Name': instance_name,
                    'Type': instance['InstanceType'],
                    'PublicIp': instance['PublicIpAddress'] if 'PublicIpAddress' in instance else '',
                    'PrivateIp': instance['PrivateIpAddress'] if 'PrivateIpAddress' in instance else '',
                    'Age': calculate_age(instance['LaunchTime']),
                    'State': instance_state,
                }

                instances.append(data.values())

        return instances
