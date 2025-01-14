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
from .wxsdocument import WXSDocument


#--------------------------------------------------------------------------------
# WindowsInstaller XML Schema 문서 템플릿.
#--------------------------------------------------------------------------------
class WXSDocumentTemplate:
	#--------------------------------------------------------------------------------
	# 기본.
	# - wxsDocument: WXSDocument = WXSDocument(WXSDocumentTemplate.Default())
	#--------------------------------------------------------------------------------
	@staticmethod
	def Default() -> Document:
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
		return document