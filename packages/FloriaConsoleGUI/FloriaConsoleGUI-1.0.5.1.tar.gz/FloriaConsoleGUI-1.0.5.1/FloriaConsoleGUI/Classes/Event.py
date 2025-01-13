import asyncio
from typing import Callable, Iterable

from ..Log import Log

class Event:
    def __init__(self, funcs: list[Callable[[], None]] = [], error_ignored: bool = False):
        self._funcs: dict[str, Callable[[any], None]] = {}
        if isinstance(funcs, Iterable):
            for func in funcs:
                self.add(func)
        else:
            self.add(funcs)
            
        self._error_ignored = error_ignored
        
    def add(self, func: Callable[[], None]):
        self._funcs[f'{func.__module__}.{func.__name__}_{tuple(func.__annotations__.keys())}'] = func
        
    def invoke(self, *args, **kwargs):
        for func in self._funcs.values():
            try:
                res = func(*args, **kwargs)
                if asyncio.iscoroutine(res):
                    raise 
                
            except Exception as ex:
                if not self._error_ignored:
                    raise ex
                Log.writeError()
                
                
    async def invokeAsync(self, *args, **kwargs):
        for func in self._funcs.values():
            try:
                res = func(*args, **kwargs)
                if asyncio.iscoroutine(res):
                    await res
                    
            except Exception as ex:
                if not self._error_ignored:
                    raise ex
                Log.writeError()


class EventKwargs(Event):
    def add(self, func: Callable[[any], None]):
        super().add(func)
    
    def invoke(self, **kwargs):
        super().invoke(**kwargs)
                
    async def invokeAsync(self, **kwargs):
        super().invokeAsync(**kwargs)