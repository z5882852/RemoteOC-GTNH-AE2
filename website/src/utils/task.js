import Requests from './requests';
import { ElMessage, ElNotification } from 'element-plus';
import Setting from '@/utils/setting';
import pako from "pako";


// 轮询获取任务状态
const fetchStatus = async (task_id, handleResult, handleUploading, handleComplete, interval = 1000, pollingController = createPollingController()) => {
    try {
        if (!Setting.get('backendUrl') || Setting.get('backendUrl') === '') {
            ElMessage.error(`请先设置后端地址！`)
            return
        }
        const response = await Requests.get('/api/task/status', { task_id, remove: false, use_gzip: Setting.get('useTaskGzip') });
        const data = response.data;
        if (data.code === 200) {
            if (data.data.result && data.data.status !== 'uploading') {
                if (data.data.gzip) {
                    // 解压缩
                    let binaryString = atob(data.data.result);
                    let binaryData = new Uint8Array(binaryString.length);
                    for (let i = 0; i < binaryString.length; i++) {
                        binaryData[i] = binaryString.charCodeAt(i);
                    }
                    let result = pako.inflate(binaryData, { to: 'string' });
                    data.data.result = JSON.parse(result);
                }
                if (handleResult) handleResult(data.data);
            }
            if (data.data.status === 'uploading') {
                if (handleUploading) handleUploading(data.data);
            }
            if (data.data.status === 'completed') {
                if (handleComplete) handleComplete(data.data);
                if (pollingController) {
                    pollingController.stop();
                }
            } else {
                if (pollingController && pollingController.running) {
                    pollingController.timeoutId = setTimeout(() => {
                        fetchStatus(task_id, handleResult, handleUploading, handleComplete, interval, pollingController);
                    }, interval);
                }
            }
        } else {
            if (pollingController) {
                pollingController.stop();
            }
            ElMessage.error(`查询任务失败: ${data.code}, ${data.message ? data.message : data}`);
            console.error(data);
        }
    } catch (error) {
        if (pollingController) {
            pollingController.stop();
        }
        ElMessage.error(`查询任务失败: ${error}`);
        console.error(`Error fetching task status: ${error}`);
    }
};

// 获取任务状态，不轮询
const fetchStatusOnce = async (task_id, handleResult) => {
    try {
        if (!Setting.get('backendUrl') || Setting.get('backendUrl') === '') {
            ElMessage.error(`请先设置后端地址！`)
            return
        }
        const response = await Requests.get('/api/task/status', { task_id, remove: false, use_gzip: Setting.get('useTaskGzip') });
        const data = response.data;
        if (data.code === 200) {
            if (data.data.result && data.data.gzip) {
                // 解压缩
                let binaryString = atob(data.data.result);
                let binaryData = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    binaryData[i] = binaryString.charCodeAt(i);
                }
                let result = pako.inflate(binaryData, { to: 'string' });
                data.data.result = JSON.parse(result);
            }
            if (handleResult) handleResult(data.data);
        } else {
            ElMessage.error(`查询任务失败: ${data.code}, ${data.message ? data.message : data}`);
            console.error(data);
        }
    }
    catch (error) {
        ElMessage.error(`查询任务失败: ${error}`);
        console.error(`Error fetching task status: ${error}`);
    }
}

const addTask = async (task_id, client_id, handleResult) => {
    try {
        if (!task_id) {
            ElMessage.error(`提交任务失败: task_id: ${task_id}`);
            return
        }
        const response = await Requests.post('/api/task/task', {
            task_id: task_id,
            client_id: client_id,
        });
        const { code, data } = response.data;
        if (code === 200) {
            console.log(`Task '${data.taskId}' added successfully.`);
            if (handleResult) handleResult(data);
        } else {
            ElMessage.error(`提交任务失败: ${data.code}, ${data.message ? data.message : data}`);

        }
    } catch (error) {
        ElMessage.error(`提交任务失败: ${error}`);
        console.error('Error adding task:', error);
    }
};

const addCommands = async (task_id, client_id, commands, handleResult) => {
    try {
        const response = await Requests.post('/api/task/add', {
            task_id: task_id,
            client_id: client_id,
            commands: commands,
        });
        const { code, data } = response.data;
        if (code === 200) {
            console.log(`Task '${data.taskId}' added successfully.`);
            if (handleResult) handleResult(data);
        } else {
            ElMessage.error(`提交任务失败: ${data.code}, ${data.message ? data.message : data}`);

        }
    } catch (error) {
        ElMessage.error(`提交任务失败: ${error}`);
        console.error('Error adding task:', error);
    }
}

const createPollingController = () => {
    return {
        running: true,
        timeoutId: null,
        stop() {
            this.running = false;
            if (this.timeoutId) {
                clearTimeout(this.timeoutId);
                this.timeoutId = null;
            }
        },
    };
};

const localTask = {
    saveTaskId: (taskId, taskType, data) => {
        let tasks = JSON.parse(localStorage.getItem('tasks')) || [];
        const task = {
            id: taskId,
            type: taskType,
            data: data,
        };
        tasks.push(task);
        localStorage.setItem('tasks', JSON.stringify(tasks));
    },
    getTasks: () => {
        const tasks = JSON.parse(localStorage.getItem('tasks')) || [];
        return tasks;
    },
    getTask: (taskId) => {
        const tasks = JSON.parse(localStorage.getItem('tasks')) || [];
        const task = tasks.find(task => task.id === taskId);
        return task || null;
    },
    removeTask: (taskId) => {
        let tasks = JSON.parse(localStorage.getItem('tasks')) || [];
        tasks = tasks.filter(task => task.id !== taskId);
        localStorage.setItem('tasks', JSON.stringify(tasks));
    },
    updateTaskData: (taskId, newData) => {
        let tasks = JSON.parse(localStorage.getItem('tasks')) || [];
        let taskIndex = tasks.findIndex(task => task.id === taskId);
        if (taskIndex !== -1) {
            tasks[taskIndex].data = newData;
            localStorage.setItem('tasks', JSON.stringify(tasks));
        } else {
            console.error(`Task with ID ${taskId} not found.`);
        }
    }
}

const createCraftTask = (itemName, ItemDamage, amount = 1, cpuName, label, callback, cpuCallback) => {
    let command = undefined;
    // ae.requestItem(name, damage, amount, cpuName, label) lua
    if (cpuName) {
        if (label) {
            command = `return ae.requestItem('${itemName}', ${ItemDamage}, ${amount}, '${cpuName}', '${label}')`
        } else {
            command = `return ae.requestItem('${itemName}', ${ItemDamage}, ${amount}, '${cpuName}')`
        }
    } else {
        if (label) {
            command = `return ae.requestItem('${itemName}', ${ItemDamage}, ${amount}, nil, '${label}')`
        } else {
            command = `return ae.requestItem('${itemName}', ${ItemDamage}, ${amount})`
        }
    }

    let commands = [command];

    let refreshCPU = Setting.get('refreshCPU');
    if (refreshCPU) {
        commands.push("return ae.getCpuList(true)");  // 刷新CPU
    }

    addCommands(null, null, commands, (data) => {
        if (callback) callback(data);
        let task_id = data.taskId;
        localTask.saveTaskId(task_id, '下单')
        ElNotification({
            title: '下单',
            dangerouslyUseHTMLString: true,
            message: `下单请求已提交<br/>详情请前往任务列表查看<br/>task id: ${task_id}`,
            type: 'info',
            duration: 6000,
        });
        const showErrorNotification = (mes = "") => {
            ElNotification({
                title: '下单',
                dangerouslyUseHTMLString: true,
                message: `下单失败，${mes}<br/>详情请前往任务列表查看<br/>task id: ${task_id}`,
                type: 'warning',
                duration: 6000,
            });
        }
        fetchStatus(task_id, null, null, (taskData) => {
            // console.log(taskData)
            try {
                if (taskData && taskData.result && taskData.result[0]) {
                    let result = JSON.parse(taskData.result[0])
                    if (result.message && result.message === "success" && result.data) {
                        if (result.data.failed) {
                            if (result.data.done.why === "request failed (missing resources?)") {
                                showErrorNotification("材料缺失或CPU不足，");
                            } else {
                                showErrorNotification("未知错误，");
                            }
                        } else {
                            ElNotification({
                                title: '下单',
                                dangerouslyUseHTMLString: true,
                                message: `下单成功<br/>详情请前往任务列表查看<br/>task id: ${task_id}`,
                                type: 'success',
                                duration: 6000,
                            });
                        }
                    } else {
                        showErrorNotification("未知错误，");
                    }
                } else {
                    showErrorNotification("未知错误，");
                }
                if (refreshCPU && taskData && taskData.result && taskData.result.length > 1 && taskData.result[1]) {
                    try {
                        if (cpuCallback) cpuCallback({
                            // 传递taskData中除了result的其他数据
                            ...taskData,
                            result: [taskData.result[1]],
                        })
                    } catch (error) {
                        console.error(error)
                        ElMessage.error(`刷新CPU失败: ${error}`);
                    }
                }
            } catch (error) {
                console.error(error)
                showErrorNotification("未知错误，");
            }
        }, 1000, createPollingController());
    });
}

/**
 * 获取任务历史数据
 * @param {string} task_id - 任务 ID
 * @param {object} options - 可选参数
 * @param {number} options.start_time - 开始时间（Unix 时间戳，秒）
 * @param {number} options.end_time - 结束时间（Unix 时间戳，秒）
 * @param {boolean} options.use_gzip - 是否启用 gzip 压缩
 * @returns {Promise<object>} 返回历史数据
 */
const fetchHistory = async (task_id, options = {}) => {
    try {
        if (!Setting.get('backendUrl') || Setting.get('backendUrl') === '') {
            ElMessage.error('请先设置后端地址！');
            return null;
        }

        const params = { task_id, ...options };
        const response = await Requests.get('/api/task/history', params);
        const { code, data, message } = response.data;

        if (code === 200) {
            // 处理 gzip 压缩的响应
            if (data.gzip && data.result) {
                let binaryString = atob(data.result);
                let binaryData = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    binaryData[i] = binaryString.charCodeAt(i);
                }
                let result = pako.inflate(binaryData, { to: 'string' });
                return JSON.parse(result);
            }
            return data;
        } else if (code === 404) {
            ElMessage.warning('任务不存在或暂无历史数据');
            return null;
        } else {
            ElMessage.error(`获取历史数据失败: ${message}`);
            return null;
        }
    } catch (error) {
        console.error('Error fetching history data:', error);
        ElMessage.error(`获取历史数据失败: ${error}`);
        return null;
    }
};

export {
    fetchStatus,
    fetchStatusOnce,
    fetchHistory,
    addTask,
    createPollingController,
    localTask,
    createCraftTask,
};
