GET = 'GET'
POST = 'POST'
PUT = 'PUT'
PATCH = 'PATCH'
DELETE = 'DELETE'
HEAD = 'HEAD'
OPTIONS = 'OPTIONS'

LOCATION = 'Location'
RETRY_AFTER = 'Retry-After'

EQUITY = 'EQUITY'

Alpha = object
MultiAlpha = object

Region = object
Delay = object
Universe = object
InstrumentType = object
Category = object
FieldType = object
DatasetsOrder = object
FieldsOrder = object
Status = object
AlphaType = object
Language = object
Color = object
Neutralization = object
UnitHandling = object
NanHandling = object
Pasteurization = object
AlphasOrder = object

from . import auto_auth_session
from . import filter_range
from . import wqb_session
from . import wqb_urls

__all__ = (
    auto_auth_session.__all__
    + filter_range.__all__
    + wqb_session.__all__
    + wqb_urls.__all__
)

from .auto_auth_session import *
from .filter_range import *
from .wqb_session import *
from .wqb_urls import *
