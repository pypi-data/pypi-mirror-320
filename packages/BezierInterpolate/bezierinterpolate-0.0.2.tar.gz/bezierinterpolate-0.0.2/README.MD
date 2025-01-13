A small package to fill missing values using Bezier Interpolation.

Installation:

```
pip install BezierInterpolate
```

Usage:

```python
from BezierInterpolate.interpolate import bezier

imputed = bezier(data=data, degree=3) #data is pandas DataFrame or pandas Series
```