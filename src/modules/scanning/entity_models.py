from typing import Literal

from pydantic import BaseModel, Field


class ScanningOptions(BaseModel):
    sides: Literal["false", "true"] = Field(default="false")
    "Scan from one side ('false') or both sides ('true'). Only applicable for Auto Scan mode."
    quality: Literal["200", "300", "400", "600"] = Field(default="300")
    "Quality of the scan in DPI (200, 300, 400, 600)"
