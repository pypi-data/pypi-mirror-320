A small package to fill missing values using Bezier Interpolation.

Installation:

```
pip install BezierInterpolate
```

Usage:

```python
from BezierInterpolate.interpolate import bezier

imputed = bezier(df) #df is pandas DataFrame or pandas Series
```