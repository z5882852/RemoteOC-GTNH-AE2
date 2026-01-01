from pydantic import BaseModel, Field
from typing import List, Optional, Any

# 定义标准化响应模型
class StandardResponseModel(BaseModel):
    code: int = Field(..., description="状态码，200 表示成功")
    message: str = Field(..., description="返回的状态信息，用于描述操作结果")
    data: Optional[Any] = Field(None, description="包含具体返回数据的字段，根据不同接口内容不同")

# 定义命令执行结果的模型
class CommandResultModel(BaseModel):
    task_id: str = Field(..., description="任务的唯一标识符")
    results: List[str] = Field(..., description="任务执行的结果，通常是输出的文本或数据")

# 分块上报内容
class CommandChunkedResultModel(BaseModel):
    task_id: str = Field(..., description="任务的唯一标识符")
    results: List = Field(..., description="任务执行的结果，通常是输出的文本或数据")

# 定义添加命令的请求模型
class AddCommandModel(BaseModel):
    task_id: Optional[str] = Field(None, description="任务的唯一标识符，如果未提供，则系统会生成新的 UUID")
    commands: List[str] = Field(..., description="要执行的命令列表，多个命令可以并行执行")
    client_id: Optional[str] = Field(None, description="客户端 ID，用于标识发出请求的客户端（可选）")

# 定义任务状态响应模型
class TaskStatusResponseModel(BaseModel):
    task_id: str = Field(..., description="任务的唯一标识符")
    status: str = Field(..., description="当前任务的状态（例如 READY、PENDING 或 COMPLETED）")
    results: List[str] = Field(None, description="如果任务已完成，此字段包含任务执行的结果")

# 定义根据任务名添加任务的请求模型
class AddTaskByNameModel(BaseModel):
    task_id: str = Field(..., description="任务的名称，用于从 `task_config` 中查找对应的任务配置")
    client_id: Optional[str] = Field(None, description="客户端 ID，标识发起请求的客户端（可选）")

# 定义添加任务的响应模型
class AddTaskResponseModel(BaseModel):
    task_id: str = Field(..., description="任务的唯一标识符，成功添加任务后由系统生成")
    message: str = Field(..., description="任务添加成功后的确认消息，通常描述任务名和命令数")

# 定义触发器添加请求模型
class AddTriggerModel(BaseModel):
    name: str = Field(..., description="触发器的名称")
    action: str = Field(..., description="触发器的操作名称")
    trigger_kwargs: dict = Field(..., description="触发器的参数")
    action_kwargs: dict = Field(..., description="操作的参数")
    interval: Optional[int] = Field(None, description="触发器的间隔时间")

# 定义触发器请求模型，用于触发器的查询和删除
class TriggerRequestModel(BaseModel):
    trigger_task_id: str = Field(..., description="触发器任务 ID")

# 定义定时器添加请求模型
class AddTimerModel(BaseModel):
    name: str = Field(..., description="定时器的名称")
    action: str = Field(..., description="定时器的操作名称")
    trigger_kwargs: dict = Field(..., description="定时器的参数")
    action_kwargs: dict = Field(..., description="操作的参数")

# 定义定时器请求模型，用于定时器的查询和删除
class TimerRequestModel(BaseModel):
    timer_id: str = Field(..., description="定时器 ID")


# 定义历史记录项模型
class TaskHistoryItemModel(BaseModel):
    results: Any = Field(None, description="任务执行的结果")
    created_time: Optional[str] = Field(None, description="任务创建时间")
    pending_time: Optional[str] = Field(None, description="任务开始执行时间")
    completed_time: Optional[str] = Field(None, description="任务完成时间")


# 定义历史记录响应模型
class TaskHistoryResponseModel(BaseModel):
    task_id: str = Field(..., description="任务的唯一标识符")
    total: int = Field(..., description="历史记录总数")
    history: List[TaskHistoryItemModel] = Field(..., description="历史记录列表")