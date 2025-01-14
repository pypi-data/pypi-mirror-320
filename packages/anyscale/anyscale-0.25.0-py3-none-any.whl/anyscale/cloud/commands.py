from typing import List

from anyscale._private.sdk import sdk_command
from anyscale.cloud._private.cloud_sdk import PrivateCloudSDK
from anyscale.cloud.models import CreateCloudCollaborator


_CLOUD_SDK_SINGLETON_KEY = "cloud_sdk"

_ADD_COLLABORATORS_EXAMPLE = """
import anyscale
from anyscale.cloud.models import CloudPermissionLevel, CreateCloudCollaborator

anyscale.cloud.add_collaborators(
    cloud="cloud_name",
    collaborators=[
        CreateCloudCollaborator(
            email="test1@anyscale.com",
            permission_level=CloudPermissionLevel.WRITE,
        ),
        CreateCloudCollaborator(
            email="test2@anyscale.com",
            permission_level=CloudPermissionLevel.READONLY,
        ),
    ],
)
"""

_ADD_COLLABORATORS_ARG_DOCSTRINGS = {
    "cloud": "The cloud to add users to.",
    "collaborators": "The list of collaborators to add to the cloud.",
}


@sdk_command(
    _CLOUD_SDK_SINGLETON_KEY,
    PrivateCloudSDK,
    doc_py_example=_ADD_COLLABORATORS_EXAMPLE,
    arg_docstrings=_ADD_COLLABORATORS_ARG_DOCSTRINGS,
)
def add_collaborators(
    cloud: str, collaborators: List[CreateCloudCollaborator], *, _sdk: PrivateCloudSDK
) -> str:
    """Batch add collaborators to a cloud."""
    return _sdk.add_collaborators(cloud, collaborators)
