# QuantFin
A library for research on asset pricing.
Working........

### Installation
```
pip install QuantFin
```

### Get started
How to assign an universe equities to deciles:

```Python

from QuantFin import Portfolio as port
import pandas as pd

# Read CRSP dataset, which can be obtained from WRDS
crsp = pd.read_pickle('crsp.pkl') 

# Assign stocks to 10 deciles based on me_comp, the market cap of a company.
crsp = port().method_ranking(crsp, on='me_comp')

```