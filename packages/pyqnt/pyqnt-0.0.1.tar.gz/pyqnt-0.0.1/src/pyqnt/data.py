import pytse_client as tse
import pandas as pd
import ccxt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def fetch_historical_data(symbols: dict, exchange_id: str = 'binance', timeframe: str = '1d') -> pd.DataFrame:
    """
    Fetches and processes historical market data for the provided symbols from the Tehran Stock Exchange (TSE)
    and/or cryptocurrency exchanges using a SOCKS5 proxy for crypto data.

    Parameters:
    ----------
    symbols : dict
        A dictionary containing lists of symbols under the keys 'tse' and/or 'crypto'.
    exchange_id : str, optional
        The ID of the cryptocurrency exchange to use for fetching crypto data (default: 'binance').
    timeframe : str, optional
        The timeframe for cryptocurrency data (default: '1d' for daily).

    Returns:
    ----------
    pd.DataFrame
        A DataFrame containing the historical data for the provided symbols.
    """
    dfs = []

    # Fetch TSE data without proxy
    if 'tse' in symbols and symbols['tse']:
        tickers = tse.download(symbols=symbols['tse'], adjust=True)
        for ticker in symbols['tse']:
            temp = tickers[ticker][['date', 'close', 'adjClose', 'yesterday']].copy()
            temp.rename(columns={'close': ticker}, inplace=True)
            temp.set_index('date', inplace=True)
            temp['ratio'] = (temp['yesterday'].shift(-1) / temp['adjClose']).fillna(1.0)
            temp['ratio'] = temp.iloc[::-1]['ratio'].cumprod().iloc[::-1]
            temp[ticker] = temp[ticker].mul(temp['ratio'], axis=0)
            temp.drop(['ratio', 'adjClose', 'yesterday'], inplace=True, axis=1)
            dfs.append(temp)

    # Fetch cryptocurrency data using SOCKS5 proxy
    if 'crypto' in symbols and symbols['crypto']:
        # Set up requests session with SOCKS5 proxy
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.proxies = {
            'http': 'socks5://localhost:10808',
            'https': 'socks5://localhost:10808',
        }

        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({'session': session})

        for symbol in symbols['crypto']:
            try:
                all_ohlcv = []
                since = None

                while True:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since)
                    if not ohlcv:
                        break
                    all_ohlcv.extend(ohlcv)
                    since = ohlcv[-1][0] + 1

                temp = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                temp['date'] = pd.to_datetime(temp['timestamp'], unit='ms')
                temp.set_index('date', inplace=True)
                temp.rename(columns={'close': symbol}, inplace=True)
                temp = temp[[symbol]]
                dfs.append(temp)

            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")

    # Concatenate all DataFrames on the 'date' index
    if dfs:
        df = pd.concat(dfs, axis=1, join='outer')
    else:
        df = pd.DataFrame()

    return df

if __name__ == "__main__":
    symbols = {
        "crypto": ["BTC/USDT", "ETH/USDT"]
    }

    data = fetch_historical_data(symbols)
    print(data)