from typing import Callable, List, Awaitable, Optional,override
import asyncio
import inspect
from nonebot import logger
from nonebot.exception import ProcessException
from .event import SuggarEvent
import sys
"""
suggar matcher
用于触发Suggar中间件事件
"""
event_handlers = {}
running_tasks = []

class SuggarMatcher:
  def __init__(self, event_type: str = ""):
        # 存储事件处理函数的字典
        global event_handlers,running_tasks
        self.event_handlers = event_handlers
        self.running_tasks = running_tasks
        self.event_type = event_type
  def handle(self, event_type = None):
    if event_type==None and self.event_type != "":
        event_type = self.event_type
    def decorator(func: Callable[[Optional[SuggarEvent]], Awaitable[None]]):
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(func)
        return func
    return decorator
  def stop(self):
    for task in self.running_tasks:
        try:
            task.cancel()
            
        except asyncio.CancelledError:
            logger.info(f"Task cancelled")
        except Exception as e:
            logger.error(f"cancelling task Error")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"Exception type: {exc_type.__name__}")
            logger.error(f"Exception message: {str(exc_value)}")
            import traceback
            logger.error(traceback.format_tb(exc_traceback))
    self.running_tasks.clear()
  async def trigger_event(self, event: SuggarEvent, **kwargs):
    
    """
    触发特定类型的事件，并调用该类型的所有注册事件处理程序。
    
    参数:
    - event: SuggarEvent 对象，包含事件相关数据。
    - **kwargs: 关键字参数，包含事件相关数据。
    """
    event_type = event.get_event_type()  # 获取事件类型

    # 检查是否有处理该事件类型的处理程序
    if event_type in self.event_handlers:
        # 遍历该事件类型的所有处理程序
        for handler in self.event_handlers[event_type]:
            # 获取处理程序的签名
            sig = inspect.signature(handler)
            # 获取参数类型注解
            params = sig.parameters
            # 构建传递给处理程序的参数字典
            args = {}
            for param_name, param in params.items():
                if param.annotation in kwargs:
                    args[param_name] = kwargs[param.annotation]
            # 调用处理程序
            try:
                logger.debug(f"start running suggar event: {event_type}")
                self.task = asyncio.create_task(handler(event, **args))
            except ProcessException as e:
                raise e
            except Exception as e:
                logger.error(f"Error running suggar at file {inspect.getfile(handler)}")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.error(f"Exception type: {exc_type.__name__}")
                logger.error(f"Exception message: {str(exc_value)}")
                import traceback
                logger.error(traceback.format_tb(exc_traceback))
            finally:
                
                logger.debug(f"matcher on {handler.__name__} is running......")
                logger.debug(f"Running suggar event: {event_type}")
                logger.info(f"matcher running at file {inspect.getfile(handler)} ")
                self.running_tasks.append(self.task)
                self.task.add_done_callback(self.running_tasks.remove)
                