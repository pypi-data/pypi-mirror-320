from pydantic import BaseModel


class ExecutorPosition(BaseModel):
    instrument: str
    number_of_actions: float = 0
    position_size_in_usd: float = 0
    last_instrument_price: float = 0
