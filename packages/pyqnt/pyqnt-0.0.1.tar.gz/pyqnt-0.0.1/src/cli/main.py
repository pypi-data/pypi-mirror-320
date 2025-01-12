import click
import yaml
import requests

API_URL = "http://127.0.0.1:8000/portfolio"

@click.group()
def pyqnt():
    """pyqnt CLI for portfolio optimization."""
    pass

@pyqnt.command()
@click.option('--file', type=click.Path(exists=True), required=True, help="Path to the YAML file containing stock symbols.")
@click.option('--method', type=click.Choice(['gmv', 'msr']), default='gmv', help="Optimization method: 'gmv' (Global Minimum Variance) or 'msr' (Maximum Sharpe Ratio)")
@click.option('--risk-free-rate', default=0.2, help="Annual risk-free rate (default: 0.2)")
@click.option('--budget', default=0, help="Total budget allocation for the portfolio (default: 0, meaning percentage-based weights only)")
def optimize(file, method, risk_free_rate, budget):
    """
    Optimize a portfolio using the specified method and input symbols from a YAML file.
    """

    # Load symbols from YAML file
    try:
        with open(file, 'r', encoding='utf-8') as f:
            symbols_data = yaml.safe_load(f)

        # Validate the YAML structure
        if not symbols_data or not isinstance(symbols_data, dict):
            click.echo("Error: Invalid YAML format. Expected a dictionary with 'tse' and/or 'crypto' keys.", err=True)
            return

        # Ensure at least one of 'tse' or 'crypto' is present
        if "tse" not in symbols_data and "crypto" not in symbols_data:
            click.echo("Error: YAML file must contain at least one of 'tse' or 'crypto' keys.", err=True)
            return

        # Validate that 'tse' and 'crypto' are lists (if they exist)
        if "tse" in symbols_data and not isinstance(symbols_data["tse"], list):
            click.echo("Error: 'tse' must be a list of symbols.", err=True)
            return
        if "crypto" in symbols_data and not isinstance(symbols_data["crypto"], list):
            click.echo("Error: 'crypto' must be a list of symbols.", err=True)
            return

    except Exception as e:
        click.echo(f"Error reading YAML file: {e}", err=True)
        return

    # Prepare API request payload
    payload = {
        "symbols": symbols_data,
        "risk_free_rate": risk_free_rate,
        "method": method,
        "budget": budget
    }

    try:
        # Send request to the API
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()

        # Display results
        click.echo("\nOptimized Portfolio Weights:")
        for item in data.get("portfolio", []):
            click.echo(f"Ticker: {item['ticker']}, Weight: {item['weight']:.2f}")
            if "amount" in item:
                click.echo(f"  Amount: {item['amount']:.2f}")

    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Unable to connect to API. {e}", err=True)

if __name__ == "__main__":
    pyqnt()