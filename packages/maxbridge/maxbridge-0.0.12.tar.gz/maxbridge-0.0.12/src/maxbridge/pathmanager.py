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
import os
from xpl import BaseManager
from .supportversiontype import SupportVersionType


#--------------------------------------------------------------------------------
# 경로 매니저.
#--------------------------------------------------------------------------------
class PathManager(BaseManager["PathManager"]):
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	__autodeskDirectory: str
	__installDirectory: str
	__maxbridgeDirectory: str
	__startupDirectory: str


	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		self.__autodeskDirectory = str()
		self.__installDirectory = str()
		self.__maxbridgeDirectory = str()
		self.__startupDirectory = str()
		self.SetSupportVersion(SupportVersionType.MAX2023)


	#--------------------------------------------------------------------------------
	# 지원 버전 설정. (기본값 2023)
	#--------------------------------------------------------------------------------
	def SetSupportVersion(self, supportVersionType: SupportVersionType = SupportVersionType.MAX2023) -> None:
		self.__autodeskDirectory = os.path.join("C:\\", "Program Files", "Autodesk")
		self.__installDirectory = os.path.join(self.__autodeskDirectory, "3ds Max 2023")
		self.__maxbridgeDirectory = os.path.join(self.__installDirectory, "scripts", "maxbridge")
		self.__startupDirectory = os.path.join(self.__installDirectory, "scripts", "Startup")


	#--------------------------------------------------------------------------------
	# 맥스 설치 경로 반환.
	#--------------------------------------------------------------------------------
	def GetAutodesk3dsMaxInstallDirectory(self) -> str:
		return self.__installDirectory
	
	#--------------------------------------------------------------------------------
	# 맥스 실행시 시작 스크립트가 동작하는 경로 반환.
	#--------------------------------------------------------------------------------
	def GetAutodesk3dsMaxStartupDirectory(self) -> str:
		return self.__startupDirectory