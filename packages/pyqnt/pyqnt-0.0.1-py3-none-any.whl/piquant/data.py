import pytse_client as tse
import pandas as pd

def history(symbols: dict) -> pd.DataFrame:
    """
    This function returns historical data of tickers as a dataframe.

    Parameters:
    ----------
        - symbols : dict
            provided symbols

    Returns:
    ----------
        - df : dataframe
            historical data of tickers
    """
    df = pd.DataFrame()

    if symbols['tsetmc']:
        tickers = tse.download(symbols=symbols['tsetmc'], adjust=True)
        for ticker in tickers:
            # adjusting the price to make the time series continuous
            temp = tickers[ticker][['date', 'close', 'adjClose', 'yesterday']].copy()
            temp.rename(columns={'close': ticker}, inplace=True)
            temp.set_index('date', inplace=True)
            temp['ratio'] = (temp['yesterday'].shift(-1) / temp['adjClose']).fillna(1.0)
            temp['ratio'] = temp.iloc[::-1]['ratio'].cumprod().iloc[::-1]
            temp[ticker] = temp[ticker].mul(temp['ratio'], axis=0)
            temp.drop(['ratio', 'adjClose', 'yesterday'], inplace=True, axis=1)
            df = pd.concat([df, temp], ignore_index = False)

    return df