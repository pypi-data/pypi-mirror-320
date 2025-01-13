from prettytable import PrettyTable
from .utils import sizeof_fmt


class ContainerRegistry:
    def __init__(self, client):
        self.client = client

    def get_images(self, repo_name, account_id):
        if repo_name != '':
            response = self.client.list_images(
                registryId=account_id,
                repositoryName=repo_name,
                maxResults=123,
                filter={
                    'tagStatus': 'ANY'
                }
            )

            table = PrettyTable()
            table.field_names = ['Tag', 'Digest', 'Size']
            table.align['Tag'] = 'l'
            table.align['Digest'] = 'l'

            for img in response['imageIds']:
                data = self.get_image_metadata(repo_name, account_id, img['imageDigest'])

                table.add_row([
                    img['imageTag'],
                    img['imageDigest'],
                    sizeof_fmt(data['imageSizeInBytes'])
                ])

            print(table.get_string())

    def get_image_metadata(self, repo_name, account_id, image_digest):
        response = self.client.describe_images(
            registryId=account_id,
            repositoryName=repo_name,
            imageIds=[
                {
                    'imageDigest': image_digest,
                },
            ],
            filter={
                'tagStatus': 'ANY'
            }
        )

        return response['imageDetails'][0]

    def get_repositories(self):
        response = self.client.describe_repositories()

        table = PrettyTable()
        table.field_names = ['Name', 'Url']
        table.align['Name'] = 'r'
        table.align['Url'] = 'l'

        for repo in response['repositories']:
            table.add_row([
                repo['repositoryName'],
                repo['repositoryUri']
            ])

        print(table.get_string())
