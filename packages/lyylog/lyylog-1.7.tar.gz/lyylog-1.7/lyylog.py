import logging
import os
import sys
import inspect
from datetime import datetime
from colorama import init, Fore, Style
from logging.handlers import RotatingFileHandler
import threading
import glob
import time

# 初始化 colorama
init(autoreset=True)

class LyyLogger:
    _instance = None
    _lock = threading.Lock()
    _handlers = {}

    def __new__(cls, log_dir="lyylog2"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize(log_dir)
            return cls._instance

    def _initialize(self, log_dir):
        """初始化logger配置"""
        self.logger = logging.getLogger("lyylog")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        
        # 确保日志目录存在
        self.log_dir = os.path.abspath(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)

        # 颜色映射
        self.color_map = {
            "debug": Fore.BLUE,
            "info": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "critical": Fore.MAGENTA
        }

        # 清理过期日志
        self._clean_old_logs()

    def _clean_old_logs(self):
        """清理过期日志文件"""
        now = time.time()
        for log_file in glob.glob(os.path.join(self.log_dir, "*.log")):
            if os.path.getmtime(log_file) < now - 7 * 86400:  # 保留7天
                os.remove(log_file)

    def _get_handler(self, module_name, level):
        """获取或创建handler"""
        current_date = datetime.now().strftime("%Y%m%d")
        handler_key = f"{module_name}_{level}_{current_date}"
        
        # 清理旧的handler
        old_handlers = [k for k in self._handlers.keys() if k.startswith(f"{module_name}_{level}_")]
        for old_key in old_handlers:
            if old_key != handler_key:
                old_handler = self._handlers.pop(old_key)
                if old_handler in self.logger.handlers:
                    self.logger.removeHandler(old_handler)
                old_handler.close()

        # 创建新的handler
        if handler_key not in self._handlers:
            log_file = os.path.join(self.log_dir, f"{module_name}_lyylog2_{level}_{current_date}.log")
            handler = RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,
                backupCount=5,
                encoding='utf-8'
            )
            log_level = getattr(logging, level.upper(), logging.INFO)
            handler.setLevel(log_level)
            
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self._handlers[handler_key] = handler
            
        return self._handlers[handler_key]

    def log(self, msg, level="info", console=True, **kwargs):
        """记录日志"""
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if level.lower() not in valid_levels:
            raise ValueError(f"Invalid log level: {level}. Valid levels are {valid_levels}")

        try:
            # 获取调用信息
            frame = inspect.currentframe().f_back
            filename = os.path.basename(frame.f_code.co_filename)
            module_name = os.path.splitext(filename)[0]
            
            # 处理日志级别
            level = level.lower()
            log_level = getattr(logging, level.upper(), logging.INFO)
            
            # 移除所有现有的handlers
            with self._lock:
                for handler in self.logger.handlers[:]:
                    self.logger.removeHandler(handler)
                
                # 添加新的handler
                handler = self._get_handler(module_name, level)
                self.logger.addHandler(handler)
                
                # 记录日志
                self.logger.log(log_level, msg)
                
            # 控制台输出
            if console and os.isatty(sys.stdout.fileno()):
                color = self.color_map.get(level, Fore.WHITE)
                print(f"{color}{msg}{Style.RESET_ALL}")
            elif console:
                print(msg)
                
        except Exception as e:
            print(f"Logging error: {str(e)}")

# 创建全局logger实例
_logger = LyyLogger()

def _log_helper(level, *args, **kwargs):
    """通用日志记录方法"""
    msg = ' '.join(map(str, args))
    if kwargs:
        msg += ' ' + ' '.join(f"{k}={v}" for k, v in kwargs.items())
    _logger.log(msg, level=level, **kwargs)

def log(*args, **kwargs):
    """记录info级别的日志"""
    _log_helper("info", *args, **kwargs)

def logerr(*args, **kwargs):
    """记录error级别的日志"""
    _log_helper("error", *args, **kwargs)

def logwarn(*args, **kwargs):
    """记录warning级别的日志"""
    _log_helper("warning", *args, **kwargs)

def logdebug(*args, **kwargs):
    """记录debug级别的日志"""
    _log_helper("debug", *args, **kwargs)

logerror = logerr

if __name__ == "__main__":
    list1 = [1, 2, 3]
    log("这是一条info级别的日志信息。", "太好了", list1)
    logerr("这是一条error级别的日志信息。")
    logwarn("这是一条warning级别的日志信息。")
    logdebug("这是一条debug级别的日志信息。")
