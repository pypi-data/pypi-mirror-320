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
from .nodemetaclass import NodeMetaClass
from .nodetype import NodeType


#--------------------------------------------------------------------------------
# 인터페이스.
#--------------------------------------------------------------------------------
class Node(metaclass = NodeMetaClass):
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	__parent: Node
	__isDirty: bool

	def __instancecheck__(self, instance):
		import inspect
		stack = [frame.function for frame in inspect.stack()]
		if stack.count("__instancecheck__") > 1:
			raise RuntimeError("Recursive __instancecheck__ detected!")
		return hasattr(instance, "some_method")


	#--------------------------------------------------------------------------------
	# 생성 오퍼레이터.
	#--------------------------------------------------------------------------------
	def __new__(classType, *argumentList, **argumentDictionary) -> Any:
		if classType is Node:
			raise TypeError("Node Instantiate Failed. (Node is Interface)")
		if not argumentDictionary.get("_from_manager", False):
			raise ValueError("Node Instantiate Failed. (Try to NodeManager)")
		base = super()
		return base.__new__(classType)


	#--------------------------------------------------------------------------------
	# 생성됨 오퍼레이터.
	#--------------------------------------------------------------------------------
	def __init__(self, targetPath: str) -> None:
		self.__parent = None
		self.__isDirty = False


	#--------------------------------------------------------------------------------
	# 동일 여부 비교 오퍼레이터.
	#--------------------------------------------------------------------------------
	def __eq__(self, targetPath: Union[Node, str]) -> bool:
		from .nodemanager import NodeManager
		return NodeManager.Equals(self, targetPath)


	# #--------------------------------------------------------------------------------
	# # 문자열 변환 오퍼레이터.
	# #--------------------------------------------------------------------------------
	# def __str__(self) -> str:
	# 	return self.Value
	

	#--------------------------------------------------------------------------------
	# 부모 디렉토리 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Parent(self) -> Node:
		if not self.Path:
			return None
		if self.__parent:
			return self.__parent
		
		from .nodemanager import NodeManager
		self.__parent = NodeManager.Instance.CreateNode(self.Path)
		return self.__parent


	#--------------------------------------------------------------------------------
	# 캐시 갱신.
	#--------------------------------------------------------------------------------
	def Dirty(self) -> None:
		if self.__isDirty:
			return

		self.OnDirty()
		self.__isDirty = True


	#--------------------------------------------------------------------------------
	# 캐시 갱신 여부.
	#--------------------------------------------------------------------------------
	def IsDirty(self) -> bool:
		return self.__isDirty


	#--------------------------------------------------------------------------------
	# 파일/디렉토리 이름 프로퍼티. (파일의 경우 확장자 제외)
	#--------------------------------------------------------------------------------
	@property
	def Name(self) -> str:
		raise NotImplementedError()


	#--------------------------------------------------------------------------------
	# 노드 타입 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def NodeType(self) -> NodeType:
		raise NotImplementedError()


	#--------------------------------------------------------------------------------
	# 현재 파일/디렉토리 이름을 제외한 경로 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Path(self) -> str:
		raise NotImplementedError()


	#--------------------------------------------------------------------------------
	# 생성시 입력받았던 파일/디렉토리 전체 경로 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Value(self) -> str:
		raise NotImplementedError()

	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	def OnCreate(self, targetPath: str) -> None:
		raise NotImplementedError()


	#--------------------------------------------------------------------------------
	# 파괴됨.
	#--------------------------------------------------------------------------------
	def OnDestroy(self) -> None:
		raise NotImplementedError()


	#--------------------------------------------------------------------------------
	# 캐시 갱신됨.
	#--------------------------------------------------------------------------------
	def OnDirty(self) -> None:
		raise NotImplementedError()