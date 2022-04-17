# QuantFin
A library for research on asset pricing.

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

crsp = port().method_ranking(crsp, on='me_comp')

```