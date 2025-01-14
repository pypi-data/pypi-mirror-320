#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Awaitable, Callable, Final, Generic, Iterable, Iterator, Optional, Sequence, Type, TypeVar, Tuple, Union
from typing import ItemsView, KeysView, ValuesView
from typing import IO, TextIO, BinaryIO
from typing import Any, List, Dict, Set
from typing import cast, overload
from ..common.booleanattribute import BooleanAttribute
from ..common.guidattribute import GuidAttribute
from ..common.idattribute import IdAttribute



#--------------------------------------------------------------------------------
# 파일 요소.
#--------------------------------------------------------------------------------
class File:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	Id: IdAttribute
	Guid: GuidAttribute
	Directory: str
	Win64: BooleanAttribute