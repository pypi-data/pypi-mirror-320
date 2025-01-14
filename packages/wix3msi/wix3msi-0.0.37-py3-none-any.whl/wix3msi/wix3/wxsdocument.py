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
import re
from .data import Product
from ..xml import Document, Element, Path


#--------------------------------------------------------------------------------
# WindowsInstaller XML Schema 문서.
#--------------------------------------------------------------------------------
class WXSDocument:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	__document: Document


	#--------------------------------------------------------------------------------
	# 문서 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Document(self) -> Document:
		return self.__document
	

	#--------------------------------------------------------------------------------
	# 네임스페이스 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Namespaces(self) -> Dict[str, str]:
		return self.__namespaces


	#--------------------------------------------------------------------------------
	# WXS XML 루트 요소 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def RootElement(self) -> Element:
		element = Element.Create(self.Document.RootXMLElement)
		return element


	#--------------------------------------------------------------------------------
	# 프로덕트 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Product(self) -> Product:
		productElement: Element = self.RootElement.Find(".//wix:Product", self.Namespaces)
		if not productElement:
			raise Exception("[wix3msi] Not found Product")
		product = Product.CreateObjectFromElement(productElement)
		return product


	#--------------------------------------------------------------------------------
	# 프로덕트 프로퍼티.
	#--------------------------------------------------------------------------------
	@Product.setter
	def Product(self, value: Product) -> None:
		productElement: Element = self.RootElement.Find(".//wix:Product", self.Namespaces)
		if not productElement:
			raise Exception("[wix3msi] Not found Product")
		
		element = Product.CreateElementFromObject(value)
		productElement.RemoveAllAttributes()
		productElement.Attributes.update(element.Attributes)


	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	def __init__(self, document: Document = None) -> None:
		self.__document = document
		self.__namespaces = dict()
		self.__namespaces["wix"] = "http://schemas.microsoft.com/wix/2006/wi"


	#--------------------------------------------------------------------------------
	# 불러오기.
	#--------------------------------------------------------------------------------
	def LoadFromWXSFile(self, wxsFilePath: str) -> bool:
		if not self.__document.LoadFromFile(wxsFilePath):
			return False
		return True


	#--------------------------------------------------------------------------------
	# 저장하기.
	#--------------------------------------------------------------------------------
	def SaveToWXSFile(self, wxsFilePath: str) -> bool:
		xmlString: str = self.Document.SaveToString()
		with builtins.open(wxsFilePath, mode = "wt", encoding = "utf-8") as outputFile:
			outputFile.write(xmlString)


	#--------------------------------------------------------------------------------
	# 생성.
	#--------------------------------------------------------------------------------
	@staticmethod
	def Create() -> WXSDocument:
		wxsDocument: WXSDocument = WXSDocument()
		return wxsDocument
	

	#--------------------------------------------------------------------------------
	# 불러오기.
	#--------------------------------------------------------------------------------
	@staticmethod
	def CreateFromWXSFile(wxsFilePath: str) -> WXSDocument:
		wxsDocument = WXSDocument()
		if not wxsDocument.LoadFromWXSFile(wxsFilePath):
			raise Exception()
		return wxsDocument


	#--------------------------------------------------------------------------------
	# 저장하기.
	#--------------------------------------------------------------------------------
	@staticmethod
	def CreateWXSFile(wxsDocument: WXSDocument, wxsFilePath: str) -> bool:
		wxsDocument.SaveToWXSFile(wxsFilePath)