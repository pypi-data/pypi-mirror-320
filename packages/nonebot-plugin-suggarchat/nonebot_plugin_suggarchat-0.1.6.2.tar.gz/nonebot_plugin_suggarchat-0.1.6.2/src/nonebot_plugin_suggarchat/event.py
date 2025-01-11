from nonebot.adapters import Event as BaseEvent
from typing import override
from nonebot.adapters.onebot.v11 import MessageSegment,Message,MessageEvent,GroupMessageEvent,PokeNotifyEvent
from .on_event import EventType
class SuggarEvent:
    """
    事件基类
    """
    def __init__(self,model_response:str,nbevent:BaseEvent,user_id:int):
        self.__event_type = EventType().none()
        self.__nbevent = nbevent
        self.__modelResponse:str = model_response
        self.__user_id:int = user_id
    def get_event_type(self)->str:
        raise NotImplementedError
    def get_model_response(self)->str:
        raise NotImplementedError
    def get_nonebot_event(self)->BaseEvent:
        raise NotImplementedError
    def get_user_id(self)->int:
        raise NotImplementedError
class ChatEvent(SuggarEvent):
    def __init__(self,nbevent:MessageEvent,send_message:MessageSegment,model_response:str,user_id:int):
        self.__modelResponse:str = model_response
        self.__nbevent:MessageEvent = nbevent
        self.__send_message:MessageSegment = send_message
        self.__user_id:int = user_id
    @override
    def get_event_type(self)->str:
        return EventType().chat()
    @override
    def get_model_response(self)->str:
        return self.__modelResponse
    @override
    def get_nonebot_event(self)->BaseEvent:
        return self.__nbevent
    @override
    def get_send_message(self)->MessageSegment:
        return self.__send_message
    
    @override
    def get_user_id(self):
        return self.__user_id
    
    def get_event_on_location(self):
        if isinstance(self.__nbevent,GroupMessageEvent):
            return "group"
        else:
            return "private"
        
class PokeEvent(SuggarEvent):
    def __init__(self,nbevent:PokeNotifyEvent,send_message:MessageSegment,model_response:str,user_id:int):
        self.__modelResponse:str = model_response
        self.__nbevent:PokeNotifyEvent = nbevent
        self.__send_message:MessageSegment = send_message
        self.__user_id:int = user_id
    @override
    def get_event_type(self)->str:
        return EventType().chat()
    @override
    def get_model_response(self)->str:
        return self.__modelResponse
    @override
    def get_nonebot_event(self)->BaseEvent:
        return self.__nbevent
    @override
    def get_send_message(self)->MessageSegment:
        return self.__send_message
    
    @override
    def get_user_id(self):
        return self.__user_id
    
    def get_event_on_location(self):
        if PokeNotifyEvent.group_id:
            return "group"
        else:
            return "private"
        