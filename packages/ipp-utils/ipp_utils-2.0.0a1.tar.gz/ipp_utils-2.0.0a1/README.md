## Utils for Intel Integrated Performance Primitives
```python
from ipp_utils import interpolation, rfft, rfft_fwd, rwelch

with interpolation(...) as ret:
    print(ret)

with rfft(...) as ret:
    print(ret)

with rfft_fwd(...) as buf:
    print(buf(...))

with rwelch(...) as buf:
    print(buf(...))
```