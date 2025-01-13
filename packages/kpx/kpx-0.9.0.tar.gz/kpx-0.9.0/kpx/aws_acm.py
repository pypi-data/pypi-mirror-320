from prettytable import PrettyTable


class CertificateManager:
    def __init__(self, client):
        self.client = client

    def get_certificates(self):
        response = self.client.list_certificates()

        table = PrettyTable()
        table.field_names = ['DomainName', 'Status', 'Type', 'KeyAlgorithm', 'InUse', 'RenewalEligibility', 'CreatedAt', 'Expiration']
        table.align['DomainName'] = 'r'

        for cert in response['CertificateSummaryList']:
            table.add_row([
                '\n'.join(cert['SubjectAlternativeNameSummaries']),
                cert['Status'],
                cert['Type'],
                cert['KeyAlgorithm'],
                cert['InUse'],
                cert['RenewalEligibility'],
                cert['CreatedAt'].strftime('%Y-%m-%d'),
                cert['NotAfter'].strftime('%Y-%m-%d'),
            ])

        return table
