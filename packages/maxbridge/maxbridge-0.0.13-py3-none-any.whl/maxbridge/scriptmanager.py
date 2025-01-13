#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Awaitable, Callable, Final, Generic, Iterable, Iterator, Optional, Sequence, Type, TypeVar, Tuple, Union
from typing import ItemsView, KeysView, ValuesView
from typing import Any, List, Dict, Set
from typing import cast, overload
import builtins
import os
from xpl import BaseManager
from .pathmanager import PathManager
from .menuitem import MenuItem


#--------------------------------------------------------------------------------
# 맥스 스크립트 매니저.
# - 디버그 기능.
# - 
#--------------------------------------------------------------------------------
class ScriptManager(BaseManager):
	#--------------------------------------------------------------------------------
	# 참조 모듈 목록.
	#--------------------------------------------------------------------------------
	__textlines: list


	#--------------------------------------------------------------------------------
	# 초기화 라이프사이클 메서드.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		self.__textlines: list = list()

	
	#--------------------------------------------------------------------------------
	# 메뉴 스크립트 생성.
	#--------------------------------------------------------------------------------
	def CreateMenuScriptFile(self, outputMaxScriptFilePath: str, menuItem: MenuItem) -> None:
		return str
	

	#--------------------------------------------------------------------------------
	# 파이썬 실행 스크립트 생성.
	#--------------------------------------------------------------------------------
	def CreateExecutePythonScript(self, executablePythonScriptFilePath: str) -> str:
		# installDirectory: str = PathManager.Instance.GetAutodesk3dsMaxInstallDirectory()
		# startupDirectory: str = PathManager.Instance.GetAutodesk3dsMaxStartupDirectory()
		return f"python.ExecuteFile \"{executablePythonScriptFilePath}\""


	#--------------------------------------------------------------------------------
	# 맥스 플러그인 스크립트 생성.
	#--------------------------------------------------------------------------------
	def CreateDebuggerScriptFile(self) -> str:
		installDirectory: str = PathManager.Instance.GetAutodesk3dsMaxInstallDirectory()
		startupDirectory: str = PathManager.Instance.GetAutodesk3dsMaxStartupDirectory()
		self.CreateExecutePythonScript()
		return f"python.ExecuteFile \"{installDirectory}\\scripts\\maxbridge\\src\\maxdebugger.py\""
	

	#--------------------------------------------------------------------------------
	# 디버그 스크립트 생성.
	#--------------------------------------------------------------------------------
	def CreateDebuggerScriptFile(self) -> str:
		installDirectory: str = PathManager.Instance.GetAutodesk3dsMaxInstallDirectory()
		startupDirectory: str = PathManager.Instance.GetAutodesk3dsMaxStartupDirectory()
		self.CreateExecutePythonScript()
		return f"python.ExecuteFile \"{installDirectory}\\scripts\\maxbridge\\src\\maxdebugger.py\""