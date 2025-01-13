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
from .schema import Product
from ...xml import Document, Element, Path


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
		wix: Element = Element.Create("Wix")

		product: Element = Element.Create("Product")
		wix.AddChild(product)
		package: Element = Element.Create("Package")
		product.AddChild(package)
		property: Element = Element.Create("Property", { "Id": "WIXUI_INSTALLDIR", "Value": "AltavaMaxPluginDirectory" })
		product.AddChild(property)
		mediaTemplate: Element = Element.Create("MediaTemplate", { "EmbedCab": "yes" })
		product.AddChild(mediaTemplate)
		feature: Element = Element.Create("Feauture", { "Id": "MainComponents" })
		product.AddChild(feature)
		componentGroupRef: Element = Element.Create("ComponentGroupRef", { "Id": "MainComponents" })
		feature.AddChild(componentGroupRef)
		wixVariable: Element = Element.Create("WixVariable", { "Id": "WixUILicenseRtf", "Value": "" })
		product.AddChild(wixVariable)
		ui: Element = Element.Create("UI")
		product.AddChild(ui)
		uiRef: Element = Element.Create("UIRef", { "Id": "WixUI_InstallDir" })
		ui.AddChild(uiRef)


		fragment: Element = Element.Create("Fragment")
		wix.AddChild(fragment)
		directroy: Element = Element.Create("Directory", { "Id": "TARGETDIR", "Name": "SourceDir" })
		fragment.AddChild(directroy)
		componentGroup = Element.Create("ComponentGroup", { "Id": "MainComponents" })
		fragment.AddChild(componentGroup)

		document: Document = Document.Create(wix)
		wxsDocument: WXSDocument = WXSDocument(document)
		return wxsDocument
	

	#--------------------------------------------------------------------------------
	# 불러오기.
	#--------------------------------------------------------------------------------
	@staticmethod
	def LoadFromWXSFile(wxsFilePath: str) -> WXSDocument:
		wxsDocument = WXSDocument()
		if not wxsDocument.LoadFromWXSFile(wxsFilePath):
			raise Exception()
		return wxsDocument


	#--------------------------------------------------------------------------------
	# 프로덕트 설정.
	#--------------------------------------------------------------------------------
	def SetProduct(self, product: Product) -> None:
		productElement: Element = self.RootElement.Find(".//wix:Product", self.Namespaces)
		if productElement:
			productElement.AddOrSetAttribute("Id", product.Id)
			productElement.AddOrSetAttribute("Name", product.Name)
			productElement.AddOrSetAttribute("Manufacturer", product.Manufacturer)
			productElement.AddOrSetAttribute("UpgradeCode", product.UpgradeCode)
			productElement.AddOrSetAttribute("Version", product.Version)
			productElement.AddOrSetAttribute("Language", product.Language)
		else:
			raise Exception("[wix3msi] Not found Product")