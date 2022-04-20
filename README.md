# QuantFin
A library for research on asset pricing.
Working........

### Installation
```
pip install QuantFin
```

### Get started
Assign the universe equities to deciles:

```Python

from QuantFin import Deciles
import pandas as pd

# Read CRSP dataset, which can be obtained from WRDS
crsp = pd.read_pickle('crsp.pkl') 

# Assign stocks to 10 deciles based on me_comp, the market cap of a company.
crsp = port().method_ranking(crsp, on='me_comp')
```

Show performance summary of a portfolio, including mean returns and alphas(FF3):

```python
from Quantfin import Portformance

rets = pd.read_pickle('rets.pkl') # Assume rets is a dataframe of your portfolio monthly returns with column names of portfolio labels and an index of datetime (if model is specified).
print(Portformance(rets, model='FF5').summary())
```
