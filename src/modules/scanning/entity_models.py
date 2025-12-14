from typing import Literal

from pydantic import BaseModel, Field


class ScanningOptions(BaseModel):
    sides: Literal["false", "true"] = Field(default="false")
    "Scan from one side ('false') or both sides ('true'). Only applicable for Auto Scan mode."
    crop: Literal["false", "true"] = Field(default="false")
    "Fit ('true') or don't fit ('false') the pdf canvas with the scanned object."
    quality: Literal["200", "300", "400", "600"] = Field(default="300")
    "Quality of the scan in DPI (200, 300, 400, 600)"
    input_source: Literal["Platen", "Adf"] = Field(default="Platen")
    "Input source to scan from (Platen for scanner glass, Adf for scanner automatic feeder)."


class ScanningResult(BaseModel):
    filename: str
    page_count: int
