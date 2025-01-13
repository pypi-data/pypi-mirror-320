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
from enum import Enum, auto



#--------------------------------------------------------------------------------
# 메뉴 아이템 종류.
#--------------------------------------------------------------------------------
class MenuItemType(Enum):
	#--------------------------------------------------------------------------------
	# 멤버 요소 목록.
	#--------------------------------------------------------------------------------
	HIERARCHY = auto()
	SEPERATOR = auto()
	PYTHON = auto()