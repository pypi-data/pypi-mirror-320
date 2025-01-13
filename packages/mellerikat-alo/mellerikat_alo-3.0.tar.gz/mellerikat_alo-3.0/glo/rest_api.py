import socket
import random
from contextlib import closing
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi import FastAPI, APIRouter
import logging

from glo.glo_api import UpdateAPI  # 새로 추가된 import

logger=logging.getLogger()


class PortManager:
    def __init__(self, preferred_ports, min_port=8000, max_port=9000):
        self.preferred_ports = preferred_ports
        self.min_port = min_port
        self.max_port = max_port

    def is_port_available(self, port):
        """특정 포트의 사용 가능 여부 확인"""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                sock.bind(('', port))
                return True
            except OSError:
                return False

    def get_available_port(self):
        """사용 가능한 포트 반환"""
        # 선호하는 포트 시도
        for port in self.preferred_ports:
            if self.is_port_available(port):
                return port

        # 랜덤 포트 시도
        used_ports = set()
        while len(used_ports) < (self.max_port - self.min_port):
            port = random.randint(self.min_port, self.max_port)
            if port in used_ports:
                continue

            used_ports.add(port)
            if self.is_port_available(port):
                return port

        raise RuntimeError("No available ports found in the specified range")

def dict_merge(source, target):
    for k, v in target.items():
        if (k in source and isinstance(source[k], dict) and isinstance(target[k], dict)):
            dict_merge(source[k], target[k])
        else:
            source[k] = target[k]

def run(api):
    app = FastAPI()

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    update_api = UpdateAPI()
    app.include_router(update_api.get_router())

    router = APIRouter()
    for rule, method_handler in api.path.items():
        for method, handler in method_handler.items():
            router.add_api_route(rule, endpoint=handler.get_handler(), methods=[method])
    app.include_router(router)

    port_manager = PortManager(preferred_ports=[80, api.port])
    try:
        port = port_manager.get_available_port()
        logger.info(f"Server starting on port: {port}")
        log_config = uvicorn.config.LOGGING_CONFIG
        dict_merge(log_config, api.config.get('logging', {}))
        uvicorn.run(app, host=api.host, port=port, log_config=log_config)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise