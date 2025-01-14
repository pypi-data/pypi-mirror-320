import typing as t

from connector.generated.models.auth_credential import AuthCredential
from connector.generated.models.page import Page
from pydantic import BaseModel, Field, StrictBool, StrictStr


class AccioRequest(BaseModel):
    object_name: StrictStr


class AccioRequestObject(BaseModel):
    auth: AuthCredential = Field(description="The authentication credentials for the request.")
    request: AccioRequest = Field(description="The main request payload")
    page: t.Optional[Page] = Field(
        default=None, description="Pagination information for the request."
    )
    include_raw_data: t.Optional[StrictBool] = Field(
        default=None, description="Whether to include raw data in the response."
    )
    settings: t.Optional[t.Dict[str, t.Any]] = Field(
        default=None,
        description=(
            "Connector-specific settings for the request. These are settings that are shared "
            "across all capabilities.  Usually contain additional required configuration "
            "options not specified by the capability schema."
        ),
    )
    __properties: t.ClassVar[t.List[str]] = ["request", "include_raw_data", "page", "settings"]


class AccioResponse(BaseModel):
    success: StrictBool


class AccioResponseObject(BaseModel):
    response: AccioResponse
    raw_data: t.Optional[t.Any] = None
