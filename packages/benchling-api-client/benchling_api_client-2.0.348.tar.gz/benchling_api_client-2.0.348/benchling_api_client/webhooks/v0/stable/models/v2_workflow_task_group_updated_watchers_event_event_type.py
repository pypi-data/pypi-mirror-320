from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class V2WorkflowTaskGroupUpdatedWatchersEventEventType(Enums.KnownString):
    V2_WORKFLOWTASKGROUPUPDATEDWATCHERS = "v2.workflowTaskGroup.updated.watchers"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "V2WorkflowTaskGroupUpdatedWatchersEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of V2WorkflowTaskGroupUpdatedWatchersEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("V2WorkflowTaskGroupUpdatedWatchersEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(V2WorkflowTaskGroupUpdatedWatchersEventEventType, getattr(newcls, "_UNKNOWN"))
