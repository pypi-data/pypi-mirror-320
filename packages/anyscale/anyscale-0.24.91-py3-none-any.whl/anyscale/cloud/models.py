from dataclasses import dataclass, field
from typing import Any, Dict, List

from anyscale._private.models import ModelBase, ModelEnum


class CloudPermissionLevel(ModelEnum):
    WRITE = "WRITE"
    READONLY = "READONLY"

    __docstrings__ = {
        WRITE: "Write permission level for the cloud",
        READONLY: "Readonly permission level for the cloud",
    }


@dataclass(frozen=True)
class CreateCloudCollaborator(ModelBase):
    """User to be added as a collaborator to a cloud.
    """

    __doc_py_example__ = """\
import anyscale
from anyscale.cloud.models import CloudPermissionLevel, CreateCloudCollaborator

create_cloud_collaborator = CreateCloudCollaborator(
   # Email of the user to be added as a collaborator
    email="test@anyscale.com",
    # Permission level for the user to the cloud (CloudPermissionLevel.WRITE, CloudPermissionLevel.READONLY)
    permission_level=CloudPermissionLevel.READONLY,
)
"""

    def _validate_email(self, email: str):
        if not isinstance(email, str):
            raise TypeError("Email must be a string.")

    email: str = field(
        metadata={"docstring": "Email of the user to be added as a collaborator."},
    )

    def _validate_permission_level(
        self, permission_level: CloudPermissionLevel
    ) -> CloudPermissionLevel:
        if isinstance(permission_level, str):
            return CloudPermissionLevel.validate(permission_level)
        elif isinstance(permission_level, CloudPermissionLevel):
            return permission_level
        else:
            raise TypeError(
                f"'permission_level' must be a 'CloudPermissionLevel' (it is {type(permission_level)})."
            )

    permission_level: CloudPermissionLevel = field(  # type: ignore
        default=CloudPermissionLevel.READONLY,  # type: ignore
        metadata={
            "docstring": "Permission level the added user should have for the cloud"  # type: ignore
            f"(one of: {','.join([str(m.value) for m in CloudPermissionLevel])}",  # type: ignore
        },
    )


@dataclass(frozen=True)
class CreateCloudCollaborators(ModelBase):
    """List of users to be added as collaborators to a cloud.
    """

    __doc_py_example__ = """\
import anyscale
from anyscale.cloud.models import CloudPermissionLevel, CreateCloudCollaborator, CreateCloudCollaborators

create_cloud_collaborator = CreateCloudCollaborator(
   # Email of the user to be added as a collaborator
    email="test@anyscale.com",
    # Permission level for the user to the cloud (CloudPermissionLevel.WRITE, CloudPermissionLevel.READONLY)
    permission_level=CloudPermissionLevel.READONLY,
)
create_cloud_collaborators = CreateCloudCollaborators(
    collaborators=[create_cloud_collaborator]
)
"""

    collaborators: List[Dict[str, Any]] = field(
        metadata={
            "docstring": "List of users to be added as collaborators to a cloud."
        },
    )

    def _validate_collaborators(self, collaborators: List[Dict[str, Any]]):
        if not isinstance(collaborators, list):
            raise TypeError("Collaborators must be a list.")
