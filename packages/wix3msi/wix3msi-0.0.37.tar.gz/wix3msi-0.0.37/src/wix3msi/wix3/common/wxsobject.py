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
from ...xml import Element
from pydantic import BaseModel, Field


#--------------------------------------------------------------------------------
# WXS 문서의 요소로 쓰이는 오브젝트.
#--------------------------------------------------------------------------------
T = TypeVar("T", bound = "WXSObject")
class WXSObject(BaseModel):
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	Children: Optional[List[WXSObject]] = Field(default_factory = list)


	#--------------------------------------------------------------------------------
	# 오브젝트를 엘리먼트로 변경.
	#--------------------------------------------------------------------------------
	def CreateElementFromObject(wxsObject: WXSObject) -> Element:
		element = Element.Create(__class__.__name__, wxsObject.__dict__)
		return element
	

	#--------------------------------------------------------------------------------
	# 엘리먼트를 오브젝트로 변경.
	#--------------------------------------------------------------------------------
	@classmethod
	def CreateObjectFromElement(classType: Type[T], element: Element) -> T:
		globals: dict = builtins.globals()
		
		obj = classType()
		obj.__dict__.update(element.Attributes)

		argumentDictionary = dict(element.Attributes)
		childObjects = list()
		for childElement in element.Children:
			childClassType = globals.get(childElement.Name)
			if not childClassType:
				continue
			if not issubclass(childClassType, WXSObject):
				continue
			childObject = childClassType.CreateObjectFromElement(childElement)
			childObjects.append(childClassType.CreateObjectFromElement(childElement))
		argumentDictionary["Children"] = childObjects
		return classType(**argumentDictionary)
