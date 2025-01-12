import asyncio
from asyncio import AbstractEventLoop
from json import dumps, loads
from os import _exit
from typing import Callable, Dict

import zmq
import zmq.asyncio
from pydantic import BaseModel

from backtesterrb30.libs.communication_broker.broker_base import BrokerBase
from backtesterrb30.libs.interfaces.utils.config import Config
from backtesterrb30.libs.utils.list_of_services import SERVICES


class ZMQ(BrokerBase):
    __is_running: bool
    __is_active: bool

    __commands: Dict[str, Callable]

    # override
    def __init__(self, config: Config, logger=print):
        self.config = config
        self.__is_running = False
        self.__is_active = False
        self.__log = logger
        self.__pub = None
        self.__subs = []

        self.__commands = {"start": self.start, "pause": self.pause, "stop": self.stop}

    # override
    def run(self):
        self.__init_sockets(self.config)
        self.__is_running = True
        self.__is_active = True

    # override
    async def send(self, service: SERVICES, msg: str, *args):
        if self.__is_active:
            data = [service.value.encode("utf-8"), msg.encode("utf-8")]
            for arg in args:
                if isinstance(arg, BaseModel):
                    arg = arg.dict()
                arg = dumps(arg, default=str)
                data.append(arg.encode("utf-8"))
            self.__pub.send_multipart(data)

    # @abstractmethod
    # def _handle_zmq_message(self, msg: str):
    #     pass

    # @abstractmethod
    # def _asyncio_loop(self, loop:asyncio.AbstractEventLoop):
    #     pass

    # def _loop(self):
    #     loop = asyncio.get_event_loop()
    #     self._asyncio_loop(loop)
    #     loop.run_forever()
    #     loop.close()

    def register(self, command: str, func: Callable):
        self.__commands[command] = func

    def create_listeners(self, loop: AbstractEventLoop):
        self.__log("Start main loop")
        for sub in self.__subs:
            loop.create_task(self.__listen_zmq(sub))

    async def __listen_zmq(self, sub):
        while self.__is_running:
            if self.__is_active:
                data = await sub.recv_multipart()
                if data:
                    await self.__handle(data)
                await asyncio.sleep(0.00001)
            else:
                await asyncio.sleep(0.01)
        self.__deinit()

    def __init_sockets(self, config: Config):
        sub_context = zmq.asyncio.Context()
        pub_context = zmq.Context()
        for sub in config.sub:
            s = sub_socket(
                sub_context, "tcp://" + config.ip + ":" + str(sub.port), sub.topic
            )
            self.__subs.append(s)
        self.__pub = pub_socket(pub_context, "tcp://*:" + str(config.pub.port))

    async def __handle(self, data):
        data = [x.decode("utf-8") for x in data]
        if len(data) >= 2:
            topic, cmd, *args = data
            func = self.__commands.get(cmd)
            if func:
                # self._log(f'Receive "{cmd}" command')
                if args:
                    args_loaded = []
                    for arg in args:
                        args_loaded.append(loads(arg))
                    await func(*args_loaded)
                else:
                    await func()
            else:
                self.__log(f"Command '{cmd}' not registered")
        # self._handle_zmq_message(data)

    def __deinit(self):
        self.__pub.close()

    def stop(self):
        self.__log("Service stoped")
        self.__is_running = False
        _exit(1)

    def start(self):
        self.__log("Service started")
        self.__is_active = True

    def pause(self):
        self.__log("Service paused")
        self.__is_active = False


def sub_socket(context: zmq.asyncio.Context(), url: str, topic: str):
    sub = context.socket(zmq.SUB)
    sub.connect(url)
    sub.subscribe(topic)
    return sub


def pub_socket(context: zmq.Context(), url: str):
    pub = context.socket(zmq.PUB)
    pub.bind(url)
    return pub
