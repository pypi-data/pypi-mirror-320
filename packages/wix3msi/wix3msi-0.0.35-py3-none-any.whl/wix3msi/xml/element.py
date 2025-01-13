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
from xml.etree.ElementTree import Element as XMLElement
from .path import Path


#--------------------------------------------------------------------------------
# 요소.
#--------------------------------------------------------------------------------
class Element:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	__xmlElement: XMLElement


	#--------------------------------------------------------------------------------
	# 엘리먼트 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def XMLElement(self) -> XMLElement:
		return self.__xmlElement


	#--------------------------------------------------------------------------------
	# 자식 요소 목록 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Children(self) -> List[Element]:
		children = list()
		for xmlElement in list(self):
			xmlElement = cast(XMLElement, xmlElement)
			element = Element.Create(xmlElement)
			children.append(element)
		return children
	

	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	def __init__(self, xmlElement: XMLElement = None) -> None:
		self.__xmlElement = xmlElement


	#--------------------------------------------------------------------------------
	# 속성 설정.
	#--------------------------------------------------------------------------------
	def AddOrSetAttribute(self, name: str, value: Any) -> None:
		# self.__xmlElement.attrib[name] = value
		self.__xmlElement.set(name, value)


	#--------------------------------------------------------------------------------
	# 속성 제거.
	#--------------------------------------------------------------------------------
	def RemoveAttribute(self, name: str) -> bool:
		if not self.HasAttribute(name):
			return False
		del self.__xmlElement.attrib[name]
		return True


	#--------------------------------------------------------------------------------
	# 속성 존재 여부 반환.
	#--------------------------------------------------------------------------------
	def HasAttribute(self, name: str) -> bool:
		if name not in self.__xmlElement.attrib:
			return False
		return True


	#--------------------------------------------------------------------------------
	# 속성 가져오기.
	#--------------------------------------------------------------------------------
	def GetAttribute(self, name: str, default: Optional[Any] = None) -> Any:
		return self.__xmlElement.attrib.get(name, default)

	#--------------------------------------------------------------------------------
	# 자식 요소 추가.
	#--------------------------------------------------------------------------------
	def AddChild(self, element: Element) -> None:
		self.XMLElement.append(element.XMLElement)
	

	#--------------------------------------------------------------------------------
	# 자식 요소 삭제.
	#--------------------------------------------------------------------------------
	def RemoveChild(self, element: Element) -> None:
		self.XMLElement.remove(element)


	#--------------------------------------------------------------------------------
	# 자식 요소 전체 삭제.
	#--------------------------------------------------------------------------------
	def RemoveAllChildren(self) -> None:
		self.XMLElement.clear()


	#--------------------------------------------------------------------------------
	# 요소 검색하여 단일 개체 반환.
	#--------------------------------------------------------------------------------
	def Find(self, path: Union[Path, str], namespaces: Optional[Dict[str, str]] = None) -> Element:
		if path is Path:
			path = cast(Path, path)
			path = str(path)
			xmlElement: XMLElement = self.__xmlElement.find(path, namespaces)
			return Element.Create(xmlElement)
		elif path is str:
			path = cast(str, path)
			xmlElement: XMLElement = self.__xmlElement.find(path, namespaces)
			return Element.Create(xmlElement)
		return None


	#--------------------------------------------------------------------------------
	# 요소 검색하여 목록으로 반환.
	#--------------------------------------------------------------------------------
	def FindAll(self, path: Union[Path, str], namespaces: Optional[Dict[str, str]] = None) -> List[Element]:
		elements = list()
		if path is Path:
			path = cast(Path, path)
			path = str(path)
			for xmlElement in self.__xmlElement.findall(path, namespaces):
				xmlElement: XMLElement = cast(XMLElement, xmlElement)
				element: Element = Element.Create(xmlElement)
				elements.append(element)
		elif path is str:
			path = cast(str, path)
			for xmlElement in self.__xmlElement.findall(path, namespaces):
				xmlElement: XMLElement = cast(XMLElement, xmlElement)
				element: Element = Element.Create(xmlElement)
				elements.append(element)
		return elements


	#--------------------------------------------------------------------------------
	# 새 객체 생성.
	#--------------------------------------------------------------------------------
	@staticmethod
	def Create(tag: str, attributes: dict, **extraAttributes) -> Element:
		xmlElement = XMLElement(tag, attributes, **extraAttributes)
		return Element.CreateFromXMLElement(xmlElement)
	

	#--------------------------------------------------------------------------------
	# 새 객체 생성.
	#--------------------------------------------------------------------------------
	@staticmethod
	def CreateFromXMLElement(xmlElement: XMLElement = None) -> Element:
		return Element(xmlElement)