# QuantFin
A library for research on asset pricing.
Working........

### Get started
Assign the universe equities to deciles:

```Python

from QuantFin import Deciles
import pandas as pd

# Read CRSP dataset, which can be obtained from WRDS
crsp = pd.read_pickle('crsp.pkl') 

# Assign stocks to 10 deciles based on me_comp, the market cap of a company.
crsp = Deciles().method_ranking(crsp, on='me_comp')
```

Show summary of portfolios, including mean returns and alphas(FF3):

```python
from Quantfin import Portformance
# Assume rets is a dataframe of your portfolio monthly returns with 
# column names of portfolio labels and an index of datetime (if model is specified).
rets = pd.read_pickle('rets.pkl') 
print(Portformance(rets, model='FF5').summary())
```
