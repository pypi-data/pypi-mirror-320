from typing import Literal
from pydantic import BaseModel


class GenericConnectionGlueJobArgs(BaseModel):
    """
    Arguments for a glue job that uses a generic connection.
    """

    connection_type: Literal["jdbc"]
    required_iam_policies: dict[str, str] = {}
