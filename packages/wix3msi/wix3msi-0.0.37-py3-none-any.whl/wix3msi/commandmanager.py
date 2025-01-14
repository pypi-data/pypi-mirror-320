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
from xpl import Console


#--------------------------------------------------------------------------------
# 커맨드 매니저.
#--------------------------------------------------------------------------------
class CommandManager:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	value: str


	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		self.value = "VALUE!!"


	#--------------------------------------------------------------------------------
	# 실행.
	#--------------------------------------------------------------------------------
	@staticmethod
	def Run() -> None:
		Console.Print(f"CommandManager.Run()")