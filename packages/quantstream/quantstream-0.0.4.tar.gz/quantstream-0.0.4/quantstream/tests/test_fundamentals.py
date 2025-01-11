from quantstream.modules.fundamentals import get_balance_sheet_statement, get_cash_flow_statement, get_company_profile, get_historical_market_capitalization, get_income_statement, get_key_executives, get_market_capitalization
from quantstream.datasets.findataset import FinDataset
from quantstream.config import set_fmp_api_key
import pytest
import datetime

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

@pytest.fixture
def set_api_key():
    from quantstream.config import set_fmp_api_key
    set_fmp_api_key("test_key")

def test_get_company_profile():
    data = get_company_profile("AAPL")
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["symbol"] == "AAPL"

# skip this test
@pytest.mark.skip(reason="Premium API key required")
def test_get_key_executives():
    data = get_key_executives("AAPL")
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_income_statement():
    data = get_income_statement("AAPL")
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_balance_sheet_statement():
    data = get_balance_sheet_statement("AAPL")
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_cash_flow_statement():
    data = get_cash_flow_statement("AAPL")
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_market_capitalization():
    data = get_market_capitalization("AAPL")
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_historical_market_capitalization():
    data = get_historical_market_capitalization("AAPL")
    assert isinstance(data, list)
    assert len(data) > 0
