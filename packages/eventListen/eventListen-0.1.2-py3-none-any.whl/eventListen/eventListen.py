from typing import Callable
from types import MethodType
from copy import copy

from proto import proto

with proto("Events") as Events:
    @Events
    def new(self) -> None:
        self.obj = {}
        self.events = []
        self.priority = None
        return
    
    @Events
    def observe(self, callback: Callable[[], None]) -> Callable[[], None]:
        self.events.append({"name": callback.__name__, "callback": callback})
        return callback

    @Events
    def trigger(self, event: str, *args, **kwargs) -> None:
        for obj in copy(self.obj):
            if not obj in self.obj: return
            o = self.obj[obj]
            if event in o:
                o[event](*args, **kwargs)
        for e in self.events:
            if e["name"] == event:
                e["callback"](*args, **kwargs)
        return 
    
    @Events
    def setEvent(self, obj: object, name: str, event: Callable[[object], None]) -> None:
        if obj not in self.obj:
            self.obj[obj] = {}
        self.obj[obj].update({name: MethodType(event, obj)})
        return

    @Events
    def group(self, obj: object, events: dict):
        self.obj[obj] = events
        return

    @Events
    def stopObserving(self, obj: object) -> None:
        del self.obj[obj]
        return
    