from .matcher import SuggarMatcher
class EventType:
    __CHAT = "chat"
    __None = ""
    __POKE = "poke"
    def __init__(self):
        return
    def chat(self):
        return self.__CHAT
    
    def none(self):
        return self.__None
    def poke(self):
        return self.__POKE
def on_chat()-> SuggarMatcher:
    return SuggarMatcher(event_type=EventType().chat())

def on_poke() -> SuggarMatcher:
    return SuggarMatcher(event_type=EventType().poke())


