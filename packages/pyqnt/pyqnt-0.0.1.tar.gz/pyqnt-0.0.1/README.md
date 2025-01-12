<h1 align="center">
    <a href="https://github.com/s06a/pyqnt"><img alt="PyQnt Logo" src="https://github.com/user-attachments/assets/5191a09c-4c00-40ab-92af-b5defa7835af" width="120"></a><br>PyQnt
</h1>

PyQnt is a Python-based tool for constructing optimal investment portfolios and performing quantitative financial analysis. The name combines **Py** (from Python) with **Qnt** (short for "quant," symbolizing quantitative analysis). PyQnt currently supports two portfolio optimization techniques: **Global Minimum Variance (GMV)** and **Maximum Sharpe Ratio (MSR)**.

## **Vision**

PyQnt aims to:
1. **Empower Financial Decisions**: Deliver tools for data-driven portfolio optimization.  
2. **Foster Exploration**: Expand into advanced quantitative techniques, risk management, and financial modeling.  

PyQnt embraces the uncertainty of markets, focusing on the journey of exploration and continuous learning.

## **Features**

- **Data Retrieval**: Access historical data from multiple markets.  
- **Portfolio Optimization**: Calculate optimal portfolio weights using GMV and MSR methods.  
- **Reporting (Upcoming)**: Generate detailed portfolio summaries and performance metrics.  

## **Installation**

To install PyQnt, clone the repository and install the package using `pip`:
```bash
git clone https://github.com/s06a/pyqnt.git
cd pyqnt
docker-compose up --build -d # to install and run backend and api on localhost:8000
pip install --user . # to install cli app
```

## **Usage Examples**

Create a portfolio YAML file (portfolio.yml):
```yml
tse:
  - "وبصادر"
  - "فولاد"
  - "طلا"
  - "عیار"
  - "کساپا"

crypto:
  - BTCUSDT
  - ETHUSDT
  - ONEUSDT
```

Run the CLI app:
```bash
pyqnt optimize --file portfolio.yml --method gmv
```

## **Fix the Persian Character Display in Terminal**

Change the terminal's font to DejaVu Sans Mono, which supports Persian script.

## **Acknowledgments**

PyQnt is a work in progress—an experiment, a learning journey, and a tool to improve financial decision-making. The future is uncertain, but this project begins with curiosity, hope, and determination.

## **Disclaimer**

PyQnt is provided for scientific and educational purposes only. It is not intended as financial advice or a guarantee of financial outcomes. The author assumes no responsibility for any misuse, legal issues, or financial losses resulting from the use of this software.