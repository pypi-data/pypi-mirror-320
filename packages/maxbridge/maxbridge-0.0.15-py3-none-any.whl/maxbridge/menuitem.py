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
from .menuitemtype import MenuItemType


#--------------------------------------------------------------------------------
# 메뉴 아이템.
#--------------------------------------------------------------------------------
class MenuItem:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	__name: str
	__type: MenuItemType
	__children: List[MenuItem]


	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	@property
	def Name(self) -> str:
		return self.__name
	

	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	@property
	def Type(self) -> MenuItemType:
		return self.__type


	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	def __init__(self, name: str, type: MenuItemType, children: List[MenuItem] = None) -> None:
		self.__name = name
		self.__type = type
		self.__children = list(children) if children else list()


	#--------------------------------------------------------------------------------
	# 추가.
	#--------------------------------------------------------------------------------
	def AddChild(self, menuItem: MenuItem) -> MenuItem:
		if not menuItem:
			return None
		if menuItem in self.__children:
			return None
		self.__children.append(menuItem)
		return menuItem


	#--------------------------------------------------------------------------------
	# 제거.
	#--------------------------------------------------------------------------------
	def RemoveChild(self, menuItem: MenuItem) -> None:
		if not menuItem:
			return
		if menuItem not in self.__children:
			return
		self.__children.remove(menuItem)


	#--------------------------------------------------------------------------------
	# 제거.
	#--------------------------------------------------------------------------------
	def RemoveAllChildren(self) -> None:
		self.__children.clear()