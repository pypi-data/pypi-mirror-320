from constructs import Construct
from terrajinja.imports.commvault.plan_backupdestination import PlanBackupdestination  # noqa: E501
from cdktf import Token


class SbpCommvaultPlanBackupdestination(PlanBackupdestination):
    def __init__(self, scope: Construct, ns: str, **kwargs):

        super().__init__(
            scope=scope,
            id_=ns,
            **kwargs,
        )

    @property
    def id(self) -> str:
        return Token().as_number(super().id)
