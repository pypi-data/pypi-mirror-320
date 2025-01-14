import os
from typing import Literal, Callable, Any, Optional, Union, TypeVar
from pydantic import BaseModel
import aiohttp
import logging
import asyncio
import requests
import time
from logging.handlers import RotatingFileHandler


def model_to_dict(model: Optional[Union[BaseModel, dict]], **kwargs) -> dict:
    """
    Convert a Pydantic model to a dictionary, compatible with both Pydantic 1.x and 2.x.
    """
    if isinstance(model, (dict, type(None))):
        return model
    try:
        # Try using Pydantic 2.x method
        return model.model_dump(**kwargs)
    except AttributeError:
        # Fallback to Pydantic 1.x method
        return model.dict(**kwargs)


def setup_logger(name, log_file, level=logging.INFO, max_bytes=10*1024*1024, backup_count=1):
    """
    Function to setup a logger with a specific name, log file, and log level.
    
    Args:
    - name (str): The name of the logger.
    - log_file (str): The file to which logs should be written.
    - level: The logging level. Default is logging.INFO.
    - max_bytes (int): The maximum file size in bytes before rotating. Default is 10MB.
    - backup_count (int): The number of backup files to keep. Default is 1.
    
    Returns:
    - logger: Configured logger object.
    """
    # Ensure the parent directory of log_file exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create a custom logger
    logger = logging.getLogger(name)
    
    # Set the log level
    logger.setLevel(level)
    
    # Create handlers
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setLevel(level)
    
    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    
    return logger


def get_model_info(model: Union[type[BaseModel], BaseModel]) -> dict[str, dict[str, Any]]:
    """获取 Pydantic 模型的字段信息
    
    Args:
        model (Union[type[BaseModel], BaseModel]): Pydantic 模型
        
    Returns:
        dict[str, dict[str, Any]]: 字段信息
    """
    info = {}
    try:
        fields = model.__fields__
    except AttributeError:
        fields = model.model_fields  # Pydantic 2.x 的字段属性
    
    for field_name, field_info in fields.items():
        if isinstance(model, BaseModel):
            value = getattr(model, field_name)
        else:
            value = ...
        description = field_info.field_info.description if hasattr(field_info, 'field_info') else field_info.description
        field_type = field_info.outer_type_ if hasattr(field_info, 'outer_type_') else field_info.annotation
        default_value = field_info.default if field_info.default is not None else None  # 默认值

        info[field_name] = {
            'value': value,  # 字段值, 如果是未实例化的 BaseModel 则为 ...
            'default_value': default_value,  # 默认值
            'description': description,  # 字段描述
            'type': field_type,  # 字段类型
        }
    return info


async def async_request(
    url: Optional[str] = None,
    headers: Optional[dict] = None,
    body: Union[dict, BaseModel, None] = None,
    token: Optional[str] = None,
    try_times: int = 2,
    try_sleep: Union[float, int] = 1,
    method: Literal['get', 'post'] = 'post',
    timeout: Union[float, int] = None,
    session: Optional[aiohttp.ClientSession] = None,
    **kwargs,
) -> dict:
    """异步请求

    Args:
        url (Optional[str], optional): 请求的 url
        headers (Optional[dict], optional): 请求头
        body (Union[dict, BaseModel, None], optional): 请求体
        token (Optional[str], optional): token，自动添加到 headers
        try_times (int, optional): 尝试次数
        try_sleep (Union[float, int], optional): 尝试间隔秒
        method (Literal['get', 'post'], optional): 请求方法
        timeout (Union[float, int], optional): 超时时间
        session (Optional[aiohttp.ClientSession], optional): 自定义 session
        kwargs (dict): 其他 session 支持的参数

    Returns:
        dict: 请求结果
            message (str): 返回信息
            status (int): 状态码
    """
    body = model_to_dict(body)
    if token:
        if not headers:
            headers = {'Content-Type': 'application/json'}
        headers['Authorization'] = f'Bearer {token}'
    
    async def _async_request(session: aiohttp.ClientSession) -> dict:
        timeout_ = aiohttp.ClientTimeout(total=timeout)
        for i in range(try_times):
            try:
                if method == 'get':
                    req = session.get(url, headers=headers, params=body, timeout=timeout_, **kwargs)
                else:
                    req = session.post(url, headers=headers, json=body, timeout=timeout_, **kwargs)
                async with req as res:
                    if res.status == 200:
                        ret = await res.json()
                    else:
                        ret = {'message': (await res.text()), 'status': res.status}
                    return ret
            except BaseException as e:
                logging.warning(f'{url} post failed ({i+1}/{try_times}): {e}')
                if i + 1 < try_times:
                    await asyncio.sleep(try_sleep)
                else:
                    return {'message': str(e), 'status': -1}
    
    if session:
        return await _async_request(session)
    else:
        async with aiohttp.ClientSession() as session:
            return await _async_request(session)


def sync_request(
    url: str = None,
    headers: Optional[dict] = None,
    body: Union[dict, BaseModel, None] = None,
    token: Optional[str] = None,
    try_times: int = 2,
    try_sleep: Union[float, int] = 1,
    method: Literal['get', 'post'] = 'post',
    **kwargs,
) -> dict:
    """同步请求

    Args:
        url (Optional[str], optional): 请求的 url
        headers (Optional[dict], optional): 请求头
        body (Union[dict, BaseModel, None], optional): 请求体
        token (Optional[str], optional): token，自动添加到 headers
        try_times (int, optional): 尝试次数
        try_sleep (Union[float, int], optional): 尝试间隔秒
        method (Literal['get', 'post'], optional): 请求方法
        kwargs (dict): 其他 session 支持的参数，例如 timeout

    Returns:
        dict: 请求结果
            message (str): 返回信息
            status (int): 状态码
    """
    body = model_to_dict(body)
    if token:
        if not headers:
            headers = {'Content-Type': 'application/json'}
        headers['Authorization'] = f'Bearer {token}'
    for i in range(try_times):
        try:
            if method == 'get':
                res = requests.get(url, headers=headers, params=body, **kwargs)
            else:
                res = requests.post(url, headers=headers, json=body, **kwargs)
            if res.status_code == 200:
                ret = res.json()
            else:
                ret = {'message': res.text, 'status': res.status_code}
            return ret
        except BaseException as e:
            logging.warning(f'{url} post failed ({i+1}/{try_times}): {e}')
            if i + 1 < try_times:
                time.sleep(try_sleep)
            else:
                return {'message': str(e), 'status': -1}


def get_log_config(
    log_level: Literal['debug', 'info', 'warn', 'error', 'critical'] = 'info',
):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "generic": {
                "format": "%(asctime)s %(levelname)s [%(process)d] %(message)s",
                # "format": "%(asctime)s %(levelname)s [%(process)d] %(name)s: %(message)s",
                "datefmt": "[%Y-%m-%d %H:%M:%S]",
                "class": "logging.Formatter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "root": {
                "level": log_level.upper(),
                "handlers": ["console"],
            },
        },
    }
