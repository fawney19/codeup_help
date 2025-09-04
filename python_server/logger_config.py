"""
日志配置模块 - 提供统一的日志格式化和管理
"""
import logging
import sys
from typing import Optional
import colorama
from colorama import Fore, Back, Style

# 初始化colorama以支持Windows的颜色输出
colorama.init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 日志级别对应的颜色
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    # 简化的日志级别标识
    LEVEL_TAGS = {
        'DEBUG': '🔍',
        'INFO': '✓',
        'WARNING': '⚠️',
        'ERROR': '✗',
        'CRITICAL': '💥',
    }
    
    def __init__(self, use_color: bool = True, show_time: bool = True):
        self.use_color = use_color
        self.show_time = show_time
        
        # 构建格式字符串
        if show_time:
            format_str = '%(asctime)s | %(levelname)-8s | %(name)s - %(message)s'
            datefmt = '%H:%M:%S'
        else:
            format_str = '%(levelname)-8s | %(name)s - %(message)s'
            datefmt = None
            
        super().__init__(format_str, datefmt=datefmt)
        
    def format(self, record):
        # 保存原始级别名称
        levelname = record.levelname
        
        if self.use_color:
            # 获取颜色和图标
            color = self.COLORS.get(levelname, '')
            icon = self.LEVEL_TAGS.get(levelname, '')
            
            # 替换级别名称为带颜色和图标的版本
            record.levelname = f"{color}{icon} {levelname}{Style.RESET_ALL}"
            
            # 根据日志级别调整消息颜色
            if levelname in ['ERROR', 'CRITICAL']:
                record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
            elif levelname == 'WARNING':
                record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
                
        # 格式化消息
        formatted = super().format(record)
        
        # 恢复原始级别名称
        record.levelname = levelname
        
        return formatted


class SimpleFormatter(logging.Formatter):
    """简洁的日志格式化器（用于生产环境）"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def setup_logger(
    name: str = None,
    level: int = logging.INFO,
    use_color: bool = True,
    show_time: bool = True,
    log_file: Optional[str] = None,
    filter_libs: bool = True
) -> logging.Logger:
    """
    设置并返回一个配置好的logger
    
    Args:
        name: logger名称，None表示root logger
        level: 日志级别
        use_color: 是否使用彩色输出（控制台）
        show_time: 是否显示时间戳
        log_file: 日志文件路径（可选）
        filter_libs: 是否过滤第三方库的日志
        
    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除现有的handlers
    logger.handlers = []
    
    # 控制台输出handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter(use_color=use_color, show_time=show_time))
    logger.addHandler(console_handler)
    
    # 文件输出handler（如果指定）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(SimpleFormatter())
        logger.addHandler(file_handler)
    
    # 过滤第三方库的日志噪音
    if filter_libs:
        # 降低第三方库的日志级别
        logging.getLogger('uvicorn').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.error').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    获取一个已配置的logger实例
    
    Args:
        name: logger名称
        
    Returns:
        logger实例
    """
    return logging.getLogger(name)


# 日志级别常量，方便使用
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL