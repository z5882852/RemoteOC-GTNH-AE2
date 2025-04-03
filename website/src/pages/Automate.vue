<template>
    <el-container style="height: 100%;">
        <el-header class="control-header-task">
            <el-card class="control-card" shadow="hover">
                <div class="control-bar">
                    <span>最近更新时间: {{ lastUpdate }}</span>
                    <div style="text-align: right;">
                        <el-button type="primary" :size="isMobile ? 'small' : ''"
                            @click="showAutoTaskDialog">添加自动化任务</el-button>
                        <el-button type="primary" :size="isMobile ? 'small' : ''"
                            @click="loadAutoTasks">刷新任务列表</el-button>
                    </div>
                </div>
            </el-card>
        </el-header>
        <el-main style="width: 100%; overflow: hidden;" v-loading="mainLoading" element-loading-text="loading">
            <el-card class="table-box-card">
                <el-table :data="tasks" border stripe style="width: 100%; height: 100%;">
                    <el-table-column type="index" label="序号" width="80"  align="center"></el-table-column>
                    <el-table-column prop="id" label="ID" width="320" align="center"></el-table-column>
                    <el-table-column prop="type" label="类型" min-width="120" align="center"></el-table-column>
                    <el-table-column prop="name" label="触发条件" min-width="120" align="center"></el-table-column>
                    <el-table-column prop="action.name" label="执行操作" min-width="100" align="center"></el-table-column>
                    <el-table-column prop="status" label="状态" min-width="85" align="center">
                        <template #default="{ row }">
                            <el-tag :type="statusMap[row.status].type">{{ statusMap[row.status].text }}</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="120" align="center" fixed="right">
                        <template #default="{ row }">
                            <div class="op-button-grid">
                                <el-button type="success" size="small" plain
                                    @click="handleStart(row)" :disabled="row.running || row.status === 'completed'">
                                    启动
                                </el-button>
                                <el-button type="warning" size="small" plain
                                    @click="handleStop(row)" :disabled="!row.running || row.status === 'completed'">
                                    停止
                                </el-button>
                                <el-button size="small" plain @click="handleInfo(row)">详情</el-button>
                                <el-button type="danger" size="small" plain @click="handleRemove(row)">移除</el-button>
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
            </el-card>
        </el-main>
        <!-- 任务详情 -->
        <el-dialog v-model="showInfoDialog" class="task-dialog" title="自动化任务详情" fullscreen align-center>
            <el-scrollbar>
                <div class="info-container">
                    <el-space alignment="normal" direction="vertical" style="width: 100%; margin-bottom: 20px;">
                        <el-descriptions title="基本信息" :column="1" border label-width="80px">
                            <el-descriptions-item label="ID">{{ info.id }}</el-descriptions-item>
                            <el-descriptions-item label="类型">{{ info.type }}</el-descriptions-item>
                            <el-descriptions-item label="状态">
                                <el-tag :type="statusMap[info.status].type">{{ statusMap[info.status].text }}</el-tag>
                            </el-descriptions-item>
                            <el-descriptions-item v-if="info.type === '触发器'" label="检测间隔">
                                {{ info.interval }} 秒
                            </el-descriptions-item>

                        </el-descriptions>

                        <el-divider></el-divider>
                        <el-text size="large">生命周期</el-text>

                        <el-timeline style="margin-top: 20px; width: 100%;">
                            <el-timeline-item :timestamp="info.time.created" size="large" color="#409EFF">
                                任务创建
                            </el-timeline-item>
                            <el-timeline-item v-if="info.time.last_start" :timestamp="info.time.last_start" size="large"
                                color="#67C23A">
                                上一次启动
                            </el-timeline-item>
                            <el-timeline-item v-if="info.time.last_monitor" :timestamp="info.time.last_monitor"
                                size="large" color="#E6A23C">
                                最近检测
                            </el-timeline-item>
                            <el-timeline-item v-if="info.time.excuted" :timestamp="info.time.excuted" size="large"
                                :color="info.time.completed ? '#E6A23C' : ''">
                                执行操作 {{ info.time.completed ? '' : '(预计)' }}
                            </el-timeline-item>
                            <el-timeline-item v-if="info.time.completed" :timestamp="info.time.completed" size="large"
                                color="#F56C6C">
                                任务完成
                            </el-timeline-item>
                        </el-timeline>
                        <el-divider></el-divider>
                        <el-descriptions title="触发条件" :column="1" border label-width="150px">
                            <el-descriptions-item label="类型">{{ info.name }}</el-descriptions-item>
                            <el-descriptions-item label="描述">{{ info.description }}</el-descriptions-item>
                            <el-descriptions-item v-for="arg in info.args" :key="arg.field" :label="arg.description">
                                <el-text>{{ info.kwargs[arg.field] }}</el-text>
                            </el-descriptions-item>
                        </el-descriptions>
                        <el-divider></el-divider>
                        <el-descriptions title="执行操作" :column="1" border label-width="150px">
                            <el-descriptions-item label="类型">{{ info.action.name }}</el-descriptions-item>
                            <el-descriptions-item label="描述">{{ info.action.description }}</el-descriptions-item>
                            <el-descriptions-item v-if="info.action.name === '合成物品'" label="合成目标">
                                <ItemCard class="item-card-container" :item="{
                                    name: info.action.action_kwargs.item_name,
                                    damage: info.action.action_kwargs.item_damage,
                                    amount: info.action.action_kwargs.item_amount,
                                    label: info.action.action_kwargs.label,
                                }" />
                            </el-descriptions-item>
                            <el-descriptions-item v-for="arg in info.action.args" :key="arg.field"
                                :label="arg.description">
                                <el-text>{{ info.action.action_kwargs[arg.field] }}</el-text>
                            </el-descriptions-item>
                        </el-descriptions>
                        <el-divider></el-divider>
                        <el-text size="large">
                            执行结果
                            <TaskResult v-if="info.action.name === '合成物品' && info.result" :task_id="info.result.data" />
                        </el-text>
                        <el-text size="large" v-if="info.result" style="width: 100%;">
                            <el-scrollbar>
                                <pre>{{ info.result }}</pre>
                            </el-scrollbar>
                        </el-text>
                        <el-text size="large" v-else>
                            无
                        </el-text>
                    </el-space>
                </div>
            </el-scrollbar>
        </el-dialog>
        <!-- 添加自动化任务 -->
        <el-dialog v-model="showAddTaskDialog" class="task-dialog" title="添加自动化任务" fullscreen align-center>
            <el-scrollbar>
                <div class="info-container">
                    <el-form :model="form" label-width="auto">
                        <el-form-item label="触发条件" :required="true">
                            <el-select-v2 v-model="form.name" placeholder="请选择触发条件" :options="options.name"
                                @change="resetFormAndLoadActions()">
                                <template #default="{ item }">
                                    <div
                                        style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                                        <span style="flex: 0 0 80px; text-align: left; margin-right: 8px;">
                                            {{ item.label }}
                                        </span>
                                        <span style="flex: 1; color: var(--el-text-color-secondary); font-size: 13px;">
                                            {{ item.desc }}
                                        </span>
                                    </div>
                                </template>
                            </el-select-v2>
                        </el-form-item>
                        <template v-if="form.name === 'CPU空闲时'">
                            <el-form-item label="监听CPU" :required="true">
                                <CpuSelect status="busy" footer="仅能选择已命名且繁忙的CPU" :options="options.cpuList"
                                    :onlyNamed="true" @handleCpuSelected="onTriggerCpuSelected"
                                    @handleLoadCpuList="onLoadCpuList" />
                            </el-form-item>
                            <el-form-item label="客户端ID">
                                <el-tooltip effect="dark" content="不指定则留空" placement="top">
                                    <el-input v-model="form.trigger_kwargs.client_id" placeholder="请输入客户端ID" />
                                </el-tooltip>
                            </el-form-item>
                            <el-form-item label="检测间隔" :required="true">
                                <el-input-number v-model="form.interval" placeholder="检测间隔" :min="1" :max="3600">
                                    <template #suffix>
                                        秒
                                    </template>
                                </el-input-number>
                            </el-form-item>
                        </template>
                        <template v-if="form.name === '延迟任务'">
                            <el-form-item label="延迟时间" :required="true">
                                <el-input-number v-model="form.trigger_kwargs.delay" placeholder="延迟" :min="60"
                                    :max="604800">
                                    <template #suffix>
                                        秒
                                    </template>
                                </el-input-number>
                            </el-form-item>
                        </template>
                        <template v-if="form.name === '定时任务'">
                            <el-form-item label="定时时间" :required="true">
                                <el-date-picker v-model="form.trigger_kwargs.time" type="datetime" placeholder="选择执行时间"
                                    :editable="false" value-format="YYYY-MM-DD HH:mm:ss" />
                            </el-form-item>
                        </template>

                        <!-- action -->
                        <template v-if="form.name">
                            <el-form-item label="执行操作" :required="true">
                                <el-select-v2 v-model="form.action" placeholder="请选择执行操作" :options="options.actions"
                                    @change="onActionSelected">
                                    <template #default="{ item }">
                                        <div
                                            style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                                            <span style="flex: 0 0 80px; text-align: left; margin-right: 8px;">
                                                {{ item.label }}
                                            </span>
                                            <span
                                                style="flex: 1; color: var(--el-text-color-secondary); font-size: 13px;">
                                                {{ item.desc }}
                                            </span>
                                        </div>
                                    </template>
                                </el-select-v2>
                            </el-form-item>
                            <template v-if="form.action">

                                <template v-if="form.action === 'craft'">
                                    <el-form-item label="目标物品" :required="true">
                                        <ItemSelect :options="options.itemList" :craft="true" footer="流体不支持中文搜索"
                                            @handleLoadItemList="onLoadedItemList"
                                            @handleItemSelected="onActionItemSelected" />
                                    </el-form-item>
                                    <el-form-item label="合成数量" :required="true">
                                        <el-input-number v-model="form.action_kwargs.item_amount" placeholder="合成数量"
                                            :min="1">
                                            <template #suffix>
                                                个
                                            </template>
                                        </el-input-number>
                                    </el-form-item>
                                    <el-form-item label="指定CPU">
                                        <el-tooltip effect="dark" content="如果请求合成时CPU繁忙，则合成失败" placement="top">
                                            <CpuSelect status="all" footer="" :options="options.cpuList"
                                                :onlyNamed="true" :autoSelect="true"
                                                @handleCpuSelected="onActionCpuSelected"
                                                @handleLoadCpuList="onLoadCpuList" />
                                        </el-tooltip>
                                    </el-form-item>
                                </template>

                                <template v-if="form.action === 'http_request'">
                                    <el-form-item label="请求方法" :required="true">
                                        <el-select v-model="options.action_kwargs.method" placeholder="请选择请求方法">
                                            <el-option label="GET" value="GET" />
                                            <el-option label="POST" value="POST" />
                                            <el-option label="PUT" value="PUT" />
                                            <el-option label="DELETE" value="DELETE" />
                                        </el-select>
                                    </el-form-item>
                                    <el-form-item label="请求地址" :required="true">
                                        <el-input v-model="options.action_kwargs.url" placeholder="请输入请求地址" />
                                    </el-form-item>
                                    <el-form-item label="请求头">
                                        <div class="key-value-group"
                                            v-for="(item, index) in options.key_value_group.headers">
                                            <el-input v-model="item.key" placeholder="请输入key" /> :
                                            <el-input v-model="item.value" placeholder="请输入value" />
                                            <el-button type="danger"
                                                @click="options.key_value_group.headers.splice(index, 1)">
                                                删除
                                            </el-button>
                                        </div>
                                        <el-button type="primary" size="small"
                                            @click="options.key_value_group.headers.push({ key: '', value: '' })">
                                            添加
                                        </el-button>
                                    </el-form-item>
                                    <el-form-item label="请求参数">
                                        <div class="key-value-group"
                                            v-for="(item, index) in options.key_value_group.params">
                                            <el-input v-model="item.key" placeholder="请输入key" /> :
                                            <el-input v-model="item.value" placeholder="请输入value" />
                                            <el-button type="danger"
                                                @click="options.key_value_group.params.splice(index, 1)">
                                                删除
                                            </el-button>
                                        </div>
                                        <el-button type="primary" size="small"
                                            @click="options.key_value_group.params.push({ key: '', value: '' })">
                                            添加
                                        </el-button>
                                    </el-form-item>
                                    <el-form-item label="请求体">
                                        <el-input type="textarea" :autosize="{ minRows: 2, maxRows: 6 }"
                                            v-model="options.action_kwargs.data" placeholder="请输入请求体" />
                                    </el-form-item>
                                </template>
                            </template>
                        </template>

                        <el-form-item v-if="form.name && form.action">
                            <el-button v-if="showUseTemplateButton" style="margin-right: auto;" type="primary"
                                @click="this.showUseTemplateDialog = true">使用模板</el-button>
                            <el-button style="margin-left: auto;" type="primary" @click="addAutoTask">添加</el-button>
                        </el-form-item>
                    </el-form>
                </div>
            </el-scrollbar>
        </el-dialog>
        <!-- 使用模板 -->
        <el-dialog v-model="showUseTemplateDialog" class="template-dialog" style="height: 400px;" title="使用模板"
            align-center>
            <el-table :data="this.options.action_templates.options" :height="340" width="100%">
                <el-table-column property="name" label="名称" />
                <el-table-column property="description" label="描述" />
                <el-table-column label="操作">
                    <template #default="{ row }">
                        <el-button type="primary" size="small" @click="comfirmUseTemplate(row)">使用</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-dialog>
    </el-container>
</template>

<script>
import { h, inject } from 'vue';
import { trigger, timer, getActionTemplats } from '@/utils/automate'
import ItemCard from "@/components/ItemCard.vue";
import TaskResult from "@/components/TaskResult.vue";
import CpuSelect from "@/components/CpuSelect.vue";
import ItemSelect from "@/components/ItemSelect.vue";
import { ElMessage, ElTag, ElButton } from 'element-plus'

const statusMap = {
    "ready": {
        text: "就绪",
        type: "primary"
    },
    "pending": {
        text: "运行中",
        type: "success"
    },
    "completed": {
        text: "已完成",
        type: "warning"
    },
}

export default {
    name: 'Automate',
    components: {
        ItemCard,
        TaskResult,
        CpuSelect,
        ItemSelect,
    },
    data() {
        return {
            statusMap,
            tasks: [],
            lastUpdate: "",
            mainLoading: false,
            showInfoDialog: false,
            showAddTaskDialog: false,
            showUseTemplateDialog: false,
            showUseTemplateButton: false,
            info: null,
            config: [],
            options: {
                name: [],
                cpuList: [],
                actions: [],
                itemList: [],
                action_kwargs: {},
                key_value_group: {
                    headers: [],
                    params: [],
                },
                action_templates: {
                    data: null,
                    options: [],
                }
            },
            args: {
                trigger: {},
                action: {},
            },
            form: {
                name: "",
                action: "",
                trigger_kwargs: {},
                action_kwargs: {},
            }
        };
    },
    setup() {
        const isMobile = inject('isMobile');
        return {
            isMobile,
        };
    },
    methods: {
        loadAutoTasks() {
            this.mainLoading = true;

            Promise.all([
                new Promise((resolve) => {
                    trigger.getTriggerList((data) => {
                        let triggers = [];
                        for (let key in data) {
                            data[key].id = key;
                            data[key].type = "触发器";
                            triggers.push(data[key]);
                        }
                        resolve(triggers);
                    });
                }),
                new Promise((resolve) => {
                    timer.getTimerList((data) => {
                        let timers = [];
                        for (let key in data) {
                            data[key].id = key;
                            data[key].type = "定时器";
                            timers.push(data[key]);
                        }
                        resolve(timers);
                    });
                })
            ])
                .then(([triggers, timers]) => {
                    this.tasks = [...triggers, ...timers];
                    this.mainLoading = false;
                    this.lastUpdate = new Date().toLocaleString().replace(/\//g, '-');
                    this.tasks.sort((a, b) => {
                        return new Date(b.time.created) - new Date(a.time.created);
                    });
                    this.tasks.reverse();
                })
                .catch((error) => {
                    this.mainLoading = false;
                    ElMessage.error(`加载任务失败: ${error}`);
                    console.error('Error loading tasks:', error);
                });
        },
        showAutoTaskDialog() {
            this.showAddTaskDialog = true;
            this.fetchAutoTaskConfig();
            this.fetchActionTemplates();
        },
        addAutoTask() {
            if (!this.form.name || !this.form.action) {
                ElMessage.error('请填写完整信息');
                return;
            }
            if (this.form.name === 'CPU空闲时' && !this.form.trigger_kwargs.cpu_name) {
                ElMessage.error('请选择监听的CPU');
                return;
            }
            if (this.form.action === 'craft') {
                if (!this.form.action_kwargs.item_name) {
                    ElMessage.error('请选择合成物品');
                    return;
                }
                if (!this.form.action_kwargs.item_amount) {
                    ElMessage.error('请填写合成数量');
                    return;
                }
            }
            if (this.form.action === 'http_request') {
                if (this.options.action_kwargs.data) {
                    try {
                        this.form.action_kwargs.data = JSON.parse(this.options.action_kwargs.data);
                    } catch (error) {
                        ElMessage.error('请求体必须是 JSON 格式');
                        console.error('Error parsing JSON:', error);
                        return;
                    }
                }
                if (this.options.key_value_group.headers && this.options.key_value_group.headers.length) {
                    let headers = {};
                    this.options.key_value_group.headers.forEach(item => {
                        if (item.key && item.value) {
                            headers[item.key] = item.value;
                        }
                    });
                    this.form.action_kwargs.headers = headers;
                }
                if (this.options.key_value_group.params && this.options.key_value_group.params.length) {
                    let params = {};
                    this.options.key_value_group.params.forEach(item => {
                        if (item.key && item.value) {
                            params[item.key] = item.value;
                        }
                    });
                    this.form.action_kwargs.params = params;
                }
                if (!this.options.action_kwargs.url || !this.options.action_kwargs.method) {
                    ElMessage.error('请求地址和方法不能为空');
                    return;
                }
                this.form.action_kwargs.method = this.options.action_kwargs.method;
                this.form.action_kwargs.url = this.options.action_kwargs.url;
            }
            let type = this.config.find(item => item.name === this.form.name).type;
            this.submitTask(type, this.form);
        },
        submitTask(type, form) {
            if (type === '触发器') {
                trigger.addTrigger(form, (res) => {
                    ElMessage.success('任务添加成功');
                    this.showAddTaskDialog = false;
                    this.loadAutoTasks();
                });
            } else {
                timer.addTimer(form, (res) => {
                    ElMessage.success('任务添加成功');
                    this.showAddTaskDialog = false;
                    this.loadAutoTasks();
                });
            }
        },
        fetchAutoTaskConfig() {
            Promise.all([
                new Promise((resolve) => {
                    trigger.getTriggerConfig((data) => {
                        data.forEach(item => item.type = '触发器');
                        resolve(data);
                    });
                }),
                new Promise((resolve) => {
                    timer.getTimerConfig((data) => {
                        data.forEach(item => item.type = '定时器');
                        resolve(data);
                    });
                })
            ])
                .then(([triggerConfig, timerConfig]) => {
                    this.config = [...triggerConfig, ...timerConfig];
                    this.options.name = [
                        {
                            label: '触发器',
                            options: triggerConfig.map(item => ({ label: item.name, value: item.name, desc: item.description }))
                        }, {
                            label: '定时器',
                            options: timerConfig.map(item => ({ label: item.name, value: item.name, desc: item.description }))
                        }
                    ];

                    this.args.trigger = {};
                    this.args.action = {};
                    this.config.forEach(item => {
                        this.args.trigger[item.name] = {};
                        this.args.action[item.name] = {};
                        item.args.forEach(arg => {
                            if (arg.default !== undefined && arg.default !== null) {
                                this.args.trigger[item.name][arg.field] = arg.default;
                            }
                        });
                        item.actions.forEach(action => {
                            this.args.action[item.name][action.id] = {};
                            action.args.forEach(arg => {
                                if (arg.default !== undefined && arg.default !== null) {
                                    this.args.action[item.name][action.id][arg.field] = arg.default;
                                }
                            });
                        });
                    });
                })
                .catch((error) => {
                    ElMessage.error(`加载任务配置失败: ${error}`);
                    console.error('Error loading task config:', error);
                });
        },
        fetchActionTemplates() {
            getActionTemplats((data) => {
                this.options.action_templates.data = data;
                let options = [];
                for (let trigger_name in data) {
                    for (let action_name in data[trigger_name]) {
                        options.push({
                            trigger_name,
                            action_name,
                            template_name: action_name,
                            description: data[trigger_name][action_name].description,
                        });
                    }
                }
            });


        },
        handleStart(data) {
            if (data.type === '定时器') {
                timer.startTimer(data.id, (res) => {
                    ElMessage.success('任务启动成功');
                    this.loadAutoTasks();
                });
                return;
            } else {
                trigger.startTrigger(data.id, (res) => {
                    ElMessage.success('任务启动成功');
                    this.loadAutoTasks();
                });
            }
        },
        handleStop(data) {
            if (data.type === '定时器') {
                timer.stopTimer(data.id, (res) => {
                    ElMessage.success('任务停止成功');
                    this.loadAutoTasks();
                });
                return;
            } else {
                trigger.stopTrigger(data.id, (res) => {
                    ElMessage.success('任务停止成功');
                    this.loadAutoTasks();
                });
            }
        },
        handleInfo(data) {
            Object.keys(data.time).forEach(key => {
                if (!data.time[key]) {
                    return;
                }
                data.time[key] = new Date(data.time[key]).toLocaleString().replace(/\//g, '-');
            });
            this.info = data;
            this.showInfoDialog = true;
        },
        handleRemove(data) {
            if (data.type === '定时器') {
                timer.removeTimer(data.id, (res) => {
                    ElMessage.success('任务移除成功');
                    this.loadAutoTasks();
                });
            } else {
                trigger.removeTrigger(data.id, (res) => {
                    ElMessage.success('任务移除成功');
                    this.loadAutoTasks();
                });
            }
        },
        resetFormAndLoadActions(clearName = false) {
            this.form = {
                name: clearName ? "" : this.form.name,
                action: "",
                trigger_kwargs: {},
                action_kwargs: {},
            };
            if (this.form.name) {
                if (this.config.find(item => item.name === this.form.name).type === '触发器') {
                    this.form.interval = 180;
                }
                this.loadDefaultTriggerArgs(this.form.name);
                this.options.actions = this.config.find(item => item.name === this.form.name).actions.map(action => ({
                    label: action.name,
                    value: action.id,
                    desc: action.description,
                }));
            }
            this.showUseTemplateButton = false;
        },
        loadDefaultTriggerArgs(name) {
            let defaultArg = this.args.trigger[name];
            if (defaultArg) {
                this.form.trigger_kwargs = defaultArg;
            }
        },
        onActionSelected(action) {
            this.form.action = action;
            this.loadDefaultActionArgs(this.form.name, action);
            if (!this.options.action_templates.data[this.form.name]) {
                this.showUseTemplateButton = false;
                this.options.action_templates.options = [];
                return;
            }
            let template = this.options.action_templates.data[this.form.name][action];
            if (template && template.length > 0) {
                this.showUseTemplateButton = true;
                this.options.action_templates.options = template;
            } else {
                this.showUseTemplateButton = false;
                this.options.action_templates.options = [];
            }
        },
        loadDefaultActionArgs(trigger_name, action) {
            let defaultArg = this.args.action[trigger_name];
            if (defaultArg[action]) {
                this.form.action_kwargs = defaultArg[action];
            }
        },
        onTriggerCpuSelected(cpu) {
            this.form.trigger_kwargs.cpu_name = cpu;
        },
        onActionCpuSelected(cpu) {
            this.form.action_kwargs.cpu_name = cpu;
        },
        onLoadCpuList(cpuList) {
            this.options.cpuList = cpuList;
        },
        onActionItemSelected(item) {
            this.form.action_kwargs.item_name = item.name;
            this.form.action_kwargs.item_damage = item.damage;
            if (item.name === 'ae2fc:fluid_drop') {
                this.form.action_kwargs.label = item.label;
            }
        },
        onLoadedItemList(itemList) {
            this.options.itemList = itemList;
        },
        comfirmUseTemplate(template) {
            let key_value_fields = template.args.key_values;
            // 存在则将template.action_kwargs中的key_value字段添加到options.key_value_group中
            if (key_value_fields) {
                key_value_fields.forEach(field => {
                    this.options.key_value_group[field] = [];
                    let key_value_content = template.action_kwargs[field];
                    if (key_value_content) {
                        for (let key in key_value_content) {
                            this.options.key_value_group[field].push({ key: key, value: key_value_content[key] });
                        }
                    }
                    // 去除template.action_kwargs中的key_value字段
                    delete template.action_kwargs[field];
                });
            }
            this.options.action_kwargs = template.action_kwargs;
            this.showUseTemplateDialog = false;
        },
    },
    created() {
        this.loadAutoTasks();
    },
    activated() {

    },
};
</script>

<style>
.control-header-task {
    width: 100%;
    margin-top: 10px;
}

.control-header-task .el-loading-spinner .circular {
    height: 24px;
    width: 24px;
}

.control-header-task .el-card__body {
    padding: 0;
}

.el-popper {
    max-width: 400px;
}

.el-select__popper {
    max-width: none;
}

.table-box-card {
    height: 100%;
}

.table-box-card .el-card__body {
    padding: 16px;
    height: calc(100% - 32px);
}

.task-dialog .el-dialog__body {
    width: 100%;
    height: calc(100% - 50px);
}

.info-container .el-row {
    margin-bottom: 10px;
}

@media screen and (max-width: 768px) {
    .template-dialog {
        width: 100% !important;
        max-width: 400px;
    }
}

.op-button-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px; 
}

.op-button-grid > .el-button+.el-button {
    margin-left: 0;
}
</style>

<style scoped>
.el-container {
    height: 100%;
}

.card-container {
    overflow-y: auto;
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    justify-content: flex-start;
    height: calc(100% - 50px);
}

.control-card {
    padding: 10px;
    margin-bottom: 10px;
}

.control-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

@media screen and (max-width: 768px) {
    .control-bar {
        height: 46px;
        flex-direction: column;
        align-items: flex-start;
    }


}

.words {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
}

.info-container {
    height: 100%;
    margin: 10px auto;
    /* overflow-y: auto; */
    /* background-color: black; */
}

.key-value-group {
    display: flex;
    gap: 5px;
    margin-bottom: 5px;
    width: 100%;
}

@media screen and (min-width: 768px) {
    .info-container {
        width: 50%;
        min-width: 768px;
    }

    .item-card-container {
        width: calc(50vw - 200px);
        min-width: 548px;
    }
}

@media screen and (max-width: 768px) {
    .info-container {
        width: 100%;
        max-width: 768px;
    }

    .item-card-container {
        width: calc(100vw - 200px);
    }
}
</style>
