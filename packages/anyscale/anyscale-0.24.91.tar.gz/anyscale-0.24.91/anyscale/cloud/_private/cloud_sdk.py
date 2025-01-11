from typing import List

from anyscale._private.sdk.base_sdk import BaseSDK
from anyscale.client.openapi_client.models import (
    CreateCloudCollaborator as CreateCloudCollaboratorModel,
)
from anyscale.cloud.models import CreateCloudCollaborator


class PrivateCloudSDK(BaseSDK):
    def add_collaborators(
        self, cloud: str, collaborators: List[CreateCloudCollaborator]
    ) -> str:
        cloud_id = self.client.get_cloud_id(cloud_name=cloud, compute_config_id=None)

        return self.client.add_cloud_collaborators(
            cloud_id=cloud_id,
            collaborators=[
                CreateCloudCollaboratorModel(
                    email=collaborator.email,
                    permission_level=collaborator.permission_level.lower(),
                )
                for collaborator in collaborators
            ],
        )
