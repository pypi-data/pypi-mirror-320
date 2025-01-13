from prettytable import PrettyTable


class AwsLb(object):
    def __init__(self, client):
        self.client = client

    def get_load_balancers(self):
        response = self.client.describe_load_balancers(
            PageSize=400
        )

        table = PrettyTable()
        table.field_names = ['LoadBalancerName', 'VPC Id', 'State', 'Type', 'DNS Name']
        table.align['LoadBalancerName'] = 'l'
        table.align['DNS Name'] = 'r'

        for lb in response['LoadBalancers']:
            table.add_row([
                lb['LoadBalancerName'],
                lb['VpcId'],
                lb['State']['Code'],
                lb['Type'],
                lb['DNSName'],
            ])
        print(table)
