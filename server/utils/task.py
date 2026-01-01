from datetime import datetime, timedelta
import json
import os
from typing import Optional, List
from .utils import logger, READY, PENDING, COMPLETED


class TaskManager:
    def __init__(self, file_dir="tasks"):
        """
        初始化任务管理器
        :param file_dir: 任务文件存储的目录
        """
        self.file_dir = file_dir
        if not os.path.exists(self.file_dir):
            os.makedirs(self.file_dir)

    def add_task(self, task_id: str, client_id: str, commands: list, status=READY, is_chunked=False) -> None:
        """
        添加任务
        :param task_id: 任务ID
        :param client_id: 客户ID
        :param commands: 命令列表
        :param status: 任务状态，默认状态为READY
        :param is_chunked: 是否为分块上传的任务
        """
        task_data = {
            'client_id': client_id,
            'commands': commands,
            'status': status,
            'chunked': is_chunked,  # 标识是否为分块任务
            'created_time': datetime.now().isoformat(),  # 任务创建时间
            'pending_time': None,  # Pending状态的时间
            'completed_time': None,  # 任务结束时间
            'history': []  # 历史记录列表
        }
        file_path = os.path.join(self.file_dir, f"{task_id}.json")
        with open(file_path, "w") as file:
            json.dump(task_data, file)
        logger.debug('Add task: %s %s %s %s', task_id, client_id, commands, status)

    def update_task(self, task_id, status=None, results=None):
        """
        更新任务的状态和结果
        :param task_id: 任务ID
        :param status: 新的任务状态
        :param results: 任务的结果
        """
        logger.debug('Update task: %s %s %s', task_id, status, results)
        task = self.get_task(task_id)
        if not task:
            return False  # 如果任务不存在，则返回 False

        if status:
            task['status'] = status
            if status == READY:
                task['created_time'] = datetime.now().isoformat()  # 记录创建状态的时间（使用缓存时）
            elif status == PENDING:
                task['pending_time'] = datetime.now().isoformat()  # 记录Pending状态的时间
            elif status == COMPLETED:
                task['completed_time'] = datetime.now().isoformat()  # 记录任务结束的时间
        if results:
            task['results'] = results

        # 将更新后的任务重新保存到文件中
        file_path = os.path.join(self.file_dir, f"{task_id}.json")
        with open(file_path, "w") as file:
            json.dump(task, file)
        return True

    def save_to_history(self, task_id: str, results, history_days: int = 7) -> bool:
        """
        将当前结果保存到历史记录中
        :param task_id: 任务ID
        :param results: 任务执行结果
        :param history_days: 历史记录最大保存天数
        :return: True 如果保存成功，False 如果任务不存在
        """
        task = self.get_task(task_id)
        if not task:
            return False

        # 初始化 history 字段（兼容旧数据）
        if 'history' not in task:
            task['history'] = []

        # 创建历史记录项
        history_item = {
            'results': results,
            'created_time': task.get('created_time'),
            'pending_time': task.get('pending_time'),
            'completed_time': datetime.now().isoformat()
        }

        # 追加到历史记录
        task['history'].append(history_item)

        # 清理过期历史记录
        self._clean_expired_history(task, history_days)

        # 保存任务
        file_path = os.path.join(self.file_dir, f"{task_id}.json")
        with open(file_path, "w") as file:
            json.dump(task, file)

        logger.debug('Saved to history: %s, total history count: %d', task_id, len(task['history']))
        return True

    def _clean_expired_history(self, task: dict, history_days: int) -> None:
        """
        清理过期的历史记录
        :param task: 任务数据
        :param history_days: 历史记录最大保存天数
        """
        if history_days <= 0:
            return

        cutoff_time = datetime.now() - timedelta(days=history_days)
        original_count = len(task.get('history', []))

        task['history'] = [
            item for item in task.get('history', [])
            if item.get('completed_time') and datetime.fromisoformat(item['completed_time']) > cutoff_time
        ]

        removed_count = original_count - len(task['history'])
        if removed_count > 0:
            logger.debug('Cleaned %d expired history items', removed_count)

    def get_task_history(
        self,
        task_id: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Optional[List[dict]]:
        """
        获取任务的历史记录，支持时间范围过滤
        :param task_id: 任务ID
        :param start_time: 开始时间（Unix时间戳，秒），可选
        :param end_time: 结束时间（Unix时间戳，秒），可选
        :return: 历史记录列表，如果任务不存在则返回None
        """
        task = self.get_task(task_id)
        if not task:
            return None

        history = task.get('history', [])

        # 时间范围过滤
        if start_time or end_time:
            filtered_history = []
            start_dt = datetime.fromtimestamp(start_time) if start_time else None
            end_dt = datetime.fromtimestamp(end_time) if end_time else None

            for item in history:
                completed_time = item.get('completed_time')
                if not completed_time:
                    continue

                item_dt = datetime.fromisoformat(completed_time)

                if start_dt and item_dt < start_dt:
                    continue
                if end_dt and item_dt > end_dt:
                    continue

                filtered_history.append(item)

            return filtered_history

        return history

    def get_task(self, task_id) -> dict | None:
        """
        获取任务
        :param task_id: 任务ID
        :return: 任务数据（字典形式），如果任务不存在则返回None
        """
        # logger.debug('Get task: %s', task_id)
        file_path = os.path.join(self.file_dir, f"{task_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        return None

    def remove_task(self, task_id) -> None:
        """
        删除任务
        :param task_id: 任务ID
        """
        logger.debug('Remove task: %s', task_id)
        file_path = os.path.join(self.file_dir, f"{task_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)

    def task_exists(self, task_id) -> bool:
        """
        检查任务是否存在
        :param task_id: 任务ID
        :return: True 如果任务存在，False 如果任务不存在
        """
        logger.debug('Task Exists: %s', task_id)
        file_path = os.path.join(self.file_dir, f"{task_id}.json")
        return os.path.exists(file_path)

    def list_tasks(self) -> list:
        """
        列出所有任务ID
        :return: 任务ID列表
        """
        task_list = [file_name.replace(".json", "") for file_name in os.listdir(self.file_dir) if file_name.endswith(".json")]
        logger.debug('Get task list: %s', task_list)
        return task_list


task_manager = TaskManager()