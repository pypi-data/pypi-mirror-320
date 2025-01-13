from .aws_ec2 import AwsResourceQuery
from prettytable import PrettyTable


class VpcManager:
    def __init__(self, session):
        self.session = session

    def get_vpc_list(self, client):
        vpcs = client.describe_vpcs()

        table = PrettyTable()
        table.field_names = ['VPC Id', 'Name', 'Cidr']
        table.align['Name'] = 'l'

        for item in vpcs['Vpcs']:
            table.add_row([
                item['VpcId'],
                AwsResourceQuery.get_instance_name_from_tags(item['Tags']) if 'Tags' in item else '-',
                item['CidrBlock']
            ])

        print(table.get_string())

    def get_vpc_subnets(self, vpc_id):
        ec2 = self.session.client('ec2')

        subnets = ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [
                        vpc_id,
                    ],
                },
            ],
        )

        table = PrettyTable()
        table.field_names = ['Subnet ID', 'Name', 'Cidr', 'Free IPs', 'AZ']
        table.align['Subnet ID'] = 'l'
        table.align['Cidr'] = 'r'
        table.align['Freep IPs'] = 'r'

        for sn in subnets['Subnets']:
            table.add_row([
                sn['SubnetId'],
                AwsResourceQuery.get_instance_name_from_tags(sn['Tags']) if 'Tags' in sn else '-',
                sn['CidrBlock'],
                sn['AvailableIpAddressCount'],
                sn['AvailabilityZone']
            ])

        print(table.get_string())
