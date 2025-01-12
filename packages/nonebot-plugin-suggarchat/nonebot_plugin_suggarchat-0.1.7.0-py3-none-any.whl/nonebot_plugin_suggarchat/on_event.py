SuggarMatcher = None
def init():
    global SuggarMatcher
    from .matcher import SuggarMatcher as Matcher
    SuggarMatcher = Matcher

class EventType:
    
    __CHAT = "chat"
    __None = ""
    __POKE = "poke"
    def __init__(self):
        init()
        return
    def chat(self):
        return self.__CHAT
    
    def none(self):
        return self.__None
    def poke(self):
        return self.__POKE
def on_chat():
    init()
    return SuggarMatcher(event_type=EventType().chat())

def on_poke():
    init()
    return SuggarMatcher(event_type=EventType().poke())


