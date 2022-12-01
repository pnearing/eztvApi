#!/usr/bin/env python3
from typing import Any, NoReturn

################################
# Type checking helper:
###############################
def __typeError__(varName:str, validTypeName:str, var:Any) -> NoReturn:
    errorMessage = "%s must be of type %s, not: %s" % (varName, validTypeName, str(type(var)))
    raise TypeError(errorMessage)
