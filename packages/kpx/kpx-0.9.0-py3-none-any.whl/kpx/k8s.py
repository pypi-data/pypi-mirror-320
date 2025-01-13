import json
import base64
import urllib3

from .utils import expand_filters, calculate_age
from prettytable import PrettyTable


def get_allocatable_gpus(nod):
    if 'nvidia.com/gpu' in nod.status.capacity:
        return nod.status.capacity['nvidia.com/gpu']

    return ''


def format_bytes(size):
    # 2**10 = 1024
    if 'Ki' in size:
        size = int(str(size).replace('Ki', '')) * 1024

    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return '{0} {1}'.format(round(size, 2), power_labels[n]+'B')


def get_instance_type(metadata):
    if 'node.kubernetes.io/instance-type' in metadata.labels.keys():
        return metadata.labels['node.kubernetes.io/instance-type']

    return ''


def get_node_group_name(metadata):
    if 'node.kubernetes.io/nodegroup' in metadata.labels.keys():
        return metadata.labels['node.kubernetes.io/nodegroup']

    return ''


def get_node_taints(node_spec):
    taints = []
    if node_spec.taints is None:
        return ''

    for taint in node_spec.taints:
        taints.append('{0}={1}:{2}'.format(taint.key, taint.value, taint.effect))

    return ','.join(taints)


def list_nodes_info(k8sapi, filter_criteria):
    try:
        ret = k8sapi.list_node()
    except urllib3.exceptions.MaxRetryError:
        return None

    table = PrettyTable()
    table.field_names = ['Name', 'Type', 'Group Name', 'GPUs', 'CPUs', 'Memory', 'SSD', 'Age', 'Taints']
    table.align['Name'] = 'l'
    table.align['Group Name'] = 'l'
    table.align['Memory'] = 'r'
    table.align['SSD'] = 'r'
    table.align['GPUs'] = 'r'
    table.align['CPUs'] = 'r'
    table.align['Age'] = 'r'
    table.align['Taints'] = 'l'

    query_filters = expand_filters(filter_criteria)

    for nod in ret.items:
        # print(nod)
        # exit(0)
        instance_group_name = get_node_group_name(nod.metadata)
        instance_type = get_instance_type(nod.metadata)
        instance_taints = get_node_taints(nod.spec)

        if query_filters:
            if 'name' in query_filters and query_filters['name'] not in nod.metadata.name.lower():
                continue
            if 'group' in query_filters and query_filters['group'] not in instance_group_name.lower():
                continue
            if 'type' in query_filters and query_filters['type'] not in instance_type.lower():
                continue
            if 'taints' in query_filters and query_filters['taints'] not in instance_taints.lower():
                continue

        table.add_row([
            nod.metadata.name,
            instance_type,
            instance_group_name,
            get_allocatable_gpus(nod),
            nod.status.capacity['cpu'],
            format_bytes(nod.status.capacity['memory']),
            format_bytes(nod.status.capacity['ephemeral-storage']),
            calculate_age(nod.metadata.creation_timestamp),
            instance_taints
        ])

    print(table.get_string())


class SecretsQuery(object):
    def list_secrets(self, subprocess, extra_options):
        output = subprocess.Popen([f"kubectl get secrets -o json {extra_options}"], shell=True,
                                  stdout=subprocess.PIPE).stdout.read().decode('utf-8')

        if output == '' or output is None:
            print('Could not retrieve secrets')
            exit(1)

        data = json.loads(output)

        table = PrettyTable()
        table.field_names = ['Name', 'Namespace', 'Type', 'Data']
        table.align['Name'] = 'l'
        table.align['Namespace'] = 'l'
        table.align['Type'] = 'l'
        table.align['Data'] = 'l'

        for item in data['items']:
            item_secrets = self.get_secrets_data(item)
            table.add_row([
                item['metadata']['name'],
                item['metadata']['namespace'],
                item['type'],
                str(', '.join(item_secrets))[:150],
            ])

        print(table.get_string())

    def show_secret(self, subprocess, secret_name, extra_options):
        output = subprocess.Popen([f"kubectl get -o json {secret_name} {extra_options}"], shell=True,
                                  stdout=subprocess.PIPE).stdout.read().decode('utf-8')

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            print("No secret found")
            return None

        secret_data = self.get_secrets_data(data, True)

        table = PrettyTable()
        table.field_names = ['Key', 'Value']
        table.align['Key'] = 'l'
        table.align['Value'] = 'l'

        table.add_rows([
            ['name', data['metadata']['name']],
            ['namespace', data['metadata']['namespace']],
            ['type', data['type']],
            ['---------', '---------']
        ])

        for item in secret_data:
            table.add_row([item, secret_data[item]])

        print(table.get_string())

    @staticmethod
    def get_secrets_data(item, show_values=False):
        output = {}
        if 'stringData' in item:
            for key, value in item['stringData'].items():
                if show_values:
                    output.update({key: value})
                else:
                    output.update({key: '***'})

        if 'data' in item:
            for key, value in item['data'].items():
                if show_values:
                    output.update({key: base64.b64decode(value).decode('utf-8').replace('\n', '')})
                else:
                    output.update({key: '***'})

        return output
