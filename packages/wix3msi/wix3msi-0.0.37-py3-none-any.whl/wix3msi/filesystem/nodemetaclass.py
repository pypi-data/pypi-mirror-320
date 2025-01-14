#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Awaitable, Callable, Final, Generic, Iterable, Iterator, Optional, Sequence, Type, TypeVar, Tuple, Union
from typing import ItemsView, KeysView, ValuesView
from typing import IO, TextIO, BinaryIO
from typing import Any, List, Dict, Set
from typing import cast, overload
import builtins
from xpl import BaseMetaClass


#--------------------------------------------------------------------------------
# 클래스 생성을 막는 메타 클래스.
#--------------------------------------------------------------------------------
class NodeMetaClass(BaseMetaClass):
	#--------------------------------------------------------------------------------
	# 객체를 함수로 호출 해주는 오퍼레이터.
	#--------------------------------------------------------------------------------
	def __call__(classType, *argumentList, **argumentDictionary) -> None:
		raise ValueError("Node Instantiate Failed. (Try to NodeManager)")