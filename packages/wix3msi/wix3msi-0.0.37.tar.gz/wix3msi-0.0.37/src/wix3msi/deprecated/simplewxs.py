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
from enum import Enum
import os
import re
import uuid
from xml.dom import minidom as Minidom
from xml.dom.minidom import Document as MinidomDocument
from xml.etree import ElementTree as XMLDocument
from xml.etree.ElementTree import Element as XMLElement


#--------------------------------------------------------------------------------
# 전역 상수 목록.
#--------------------------------------------------------------------------------
FILE_READTEXT: str = "rt"
FILE_WRITETEXT: str = "wt"
UTF8: str = "utf-8"
WIX: str = "wix"
WIX_NAMESPACE: str = "http://schemas.microsoft.com/wix/2006/wi"
EMPTY: str = ""
RE_REMOVE_NS0: str = "(ns0:|ns0|:ns0)"
LINEFEED: str = "\n"


#--------------------------------------------------------------------------------
# Simple Windows installer XML Schema.
#--------------------------------------------------------------------------------
class SimpleWXS:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	__namespaces: dict
	__wxsFilePath: str
	__document: Document


	#--------------------------------------------------------------------------------
	# 네임스페이스 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Namespaces(self) -> dict:
		return self.__namespaces
	

	#--------------------------------------------------------------------------------
	# WXS XML 파일 경로 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def FilePath(self) -> dict:
		return self.__wxsFilePath
	

	#--------------------------------------------------------------------------------
	# WXS XML 트리 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Document(self) -> Document:
		return self.__document


	#--------------------------------------------------------------------------------
	# WXS XML 루트 요소 프로퍼티.
	#--------------------------------------------------------------------------------
	@property
	def Root(self) -> XMLElement:
		rootElement: XMLElement = self.Document.getroot()
		return rootElement


	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		self.__namespaces = dict()
		self.__namespaces[WIX] = WIX_NAMESPACE
		# Document.register_namespace(WIX, WIX_NAMESPACE)
		self.__wxsFilePath = str()
		self.__document = None


	#--------------------------------------------------------------------------------
	# 초기화.
	#--------------------------------------------------------------------------------
	def Clear(self):
		self.__wxsFilePath = str()
		self.__document = None


	#--------------------------------------------------------------------------------
	# 파일을 불러왔는지 여부.
	#--------------------------------------------------------------------------------
	def IsLoaded(self) -> bool:
		if not self.FilePath or not self.Document:
			return False
		return True


	#--------------------------------------------------------------------------------
	# 파일 불러오기.
	#--------------------------------------------------------------------------------
	def LoadFromWXSFile(self, wxsFilePath: str) -> bool:
		if not wxsFilePath:
			return False
		if not os.path.isfile(wxsFilePath):
			return False
		
		self.__wxsFilePath = wxsFilePath
		self.__document = XMLDocument.parse(self.__wxsFilePath)
		return True

	#--------------------------------------------------------------------------------
	# 파일 저장하기.
	#--------------------------------------------------------------------------------
	def SaveToWXSFile(self, wxsFilePath: Optional[str] = None) -> bool:
		if not self.IsLoaded():
			return False

		if not wxsFilePath:
			wxsFilePath = self.__wxsFilePath

		# XML 데이터를 문자열로 변환.
		xmlBytes: bytes = XMLDocument.tostring(self.Root, xml_declaration = False, encoding = UTF8)
		xmlString = xmlBytes.decode(UTF8)

		# 문자열을 미니돔 도큐먼트로 변환.
		xmlDocument: MinidomDocument = Minidom.parseString(xmlString)
		xmlString = xmlDocument.toprettyxml()

		# NS0이 붙어있거나, 탭만 있는 라인은 제거.
		xmlString = re.sub(RE_REMOVE_NS0, EMPTY, xmlString)
		xmlString = re.sub("^\t+$\n", EMPTY, xmlString, flags = re.MULTILINE)
		xmlString = re.sub("^\n", EMPTY, xmlString, flags = re.MULTILINE)
		xmlString = xmlString.replace("&lt;", "<")
		xmlString = xmlString.replace("&gt;", ">")

		# 마지막 개행문자 제거.
		if xmlString.endswith(LINEFEED):
			xmlString = xmlString[:-1]

		# 저장.
		with builtins.open(wxsFilePath, mode = FILE_WRITETEXT, encoding = UTF8) as outputFile:
			outputFile.write(xmlString)
		

	#--------------------------------------------------------------------------------
	# 찾기.
	# - 예: ComponentRef, PythonDirectoryComponent
	# - xpath: ".//wix:Wix/wix:Product/wix:Condition[{AttributeName}='{AttributeValue}']"
	#--------------------------------------------------------------------------------
	def Find(self, xpath: str) -> XMLElement:
		if not self.IsLoaded():
			return None
		return self.Root.find(xpath, namespaces = self.Namespaces)


	#--------------------------------------------------------------------------------
	# 검색.
	#--------------------------------------------------------------------------------
	def FindAll(self, xpath: str) -> List[XMLElement]:
		if not self.IsLoaded():
			return list()
		else:
			return self.Root.findall(xpath, namespaces = self.Namespaces)


	#--------------------------------------------------------------------------------
	# 유효한 요소인지 여부.
	#--------------------------------------------------------------------------------
	@staticmethod
	def IsValidElement(targetElement: XMLElement) -> bool:
		try:
			tag: str = targetElement.tag
			return True
		except Exception as exception:
			return False

	
	#--------------------------------------------------------------------------------
	# 대상 요소의 자식 갯수를 반환.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetChildCount(wxs: SimpleWXS, targetElement: XMLElement) -> int:
		if not wxs:
			return -1
		if not wxs.IsLoaded():
			return -1
		if not SimpleWXS.IsValidElement(targetElement):
			return -1
		children = targetElement.findall("*")
		if not children:
			return 0
		return builtins.len(children)