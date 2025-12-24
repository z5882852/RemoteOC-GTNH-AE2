import uvicorn
import argparse
from app import app
from utils.scheduler import start_scheduler, stop_scheduler
from utils.utils import LOG_LEVEL, COMPLETED, logger
from utils.task import task_manager
from utils.trigger import trigger_manager
from config import task_config, timer_task_config


def parse_args():
    parser = argparse.ArgumentParser(description="启动 RemoteOC 服务端")
    parser.add_argument("--host", "-H", default="0.0.0.0", help="服务器监听的主机地址，默认 0.0.0.0")
    parser.add_argument("--port", "-P", type=int, default=8080, help="服务器监听的端口，默认 8080")
    
    # 解析参数
    return parser.parse_args()


def init_task_manager():
    """初始化任务"""
    for task_id, task_cfg in task_config.items():
        if not task_manager.task_exists(task_id):
            task_manager.add_task(
                task_id, 
                client_id=task_cfg.get("client_id", None), 
                commands=task_cfg.get("commands", []), 
                status=COMPLETED, 
                is_chunked=task_cfg.get("chunked", False)
            )
    for task_id, task_cfg in timer_task_config.items():
        if not task_manager.task_exists(task_id):
            task_manager.add_task(
                task_id, 
                client_id=task_cfg.get("client_id", None), 
                commands=task_cfg.get("commands", []), 
                status=COMPLETED, 
                is_chunked=task_cfg.get("chunked", False)
            )
    logger.debug("task init success.")


if __name__ == "__main__":
    args = parse_args()

    # 配置日志格式
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"

    # 启动调度器
    start_scheduler()
    # 初始化任务
    init_task_manager()
    
    try:
        # 使用解析后的 host 和 port 启动 Uvicorn
        uvicorn.run(app, host=args.host, port=args.port, log_config=log_config, log_level=LOG_LEVEL)
    except KeyboardInterrupt:
        pass
    finally:
        # 停止调度器
        stop_scheduler()
        # 停止触发器
        trigger_manager.stop_all()

