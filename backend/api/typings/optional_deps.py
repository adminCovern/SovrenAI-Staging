# Type stubs for optional dependencies
# This helps with import resolution when packages are not installed

from typing import TYPE_CHECKING, Any, Optional, Union, List, Dict

if TYPE_CHECKING:
    # Import type stubs for optional dependencies
    import asyncpg
    import redis
    import pandas as pd
    import sklearn
    from sklearn.metrics.pairwise import cosine_similarity
else:
    # Runtime fallbacks - these will be None if packages aren't installed
    asyncpg = None
    redis = None
    pd = None
    sklearn = None
    cosine_similarity = None

# Type aliases for better type checking
RedisClient = Optional[Any]  # redis.Redis
DatabasePool = Optional[Any]  # asyncpg.Pool
DataFrame = Optional[Any]  # pd.DataFrame 