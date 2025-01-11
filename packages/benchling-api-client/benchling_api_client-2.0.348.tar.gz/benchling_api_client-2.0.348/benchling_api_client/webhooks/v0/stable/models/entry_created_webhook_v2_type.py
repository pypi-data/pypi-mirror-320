from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntryCreatedWebhookV2Type(Enums.KnownString):
    V2_ENTRYCREATED = "v2.entry.created"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntryCreatedWebhookV2Type":
        if not isinstance(val, str):
            raise ValueError(f"Value of EntryCreatedWebhookV2Type must be a string (encountered: {val})")
        newcls = Enum("EntryCreatedWebhookV2Type", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntryCreatedWebhookV2Type, getattr(newcls, "_UNKNOWN"))
