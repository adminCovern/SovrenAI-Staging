# Type stubs for optional dependencies
# This helps with import resolution when packages are not installed

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncpg
    import redis
    import pandas
    import sklearn
else:
    # Runtime fallbacks
    asyncpg = None
    redis = None
    pandas = None
    sklearn = None 