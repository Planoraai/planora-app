"""Currency conversion tool."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from tools.tool_runtime import BaseTool

_FX_RATES: dict[tuple[str, str], float] = {
    ("USD", "USD"): 1.0,
    ("USD", "JPY"): 150.0,
    ("JPY", "USD"): 0.0067,
    ("USD", "EUR"): 0.92,
    ("EUR", "USD"): 1.09,
    ("EUR", "JPY"): 163.0,
    ("JPY", "EUR"): 0.0061,
}


class FxConvertRequest(BaseModel):
    amount: float = Field(gt=0)
    from_currency: str = Field(min_length=3, max_length=3)
    to_currency: str = Field(min_length=3, max_length=3)

    @field_validator("from_currency", "to_currency")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return value.upper()


class FxConvertResponse(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    rate: float = Field(gt=0)
    converted_amount: float = Field(gt=0)


class FxConvertTool(BaseTool[FxConvertRequest, FxConvertResponse]):
    name = "fx_convert"
    request_model = FxConvertRequest
    response_model = FxConvertResponse

    def _run_mock(self, request: FxConvertRequest) -> FxConvertResponse:
        pair = (request.from_currency, request.to_currency)
        rate = _FX_RATES.get(pair)
        if rate is None:
            rate = 1.0 if request.from_currency == request.to_currency else 1.2
        converted_amount = round(request.amount * rate, 2)
        return FxConvertResponse(
            amount=request.amount,
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            rate=rate,
            converted_amount=converted_amount,
        )
