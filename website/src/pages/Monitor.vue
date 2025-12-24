<template>
    <div class="statistic-container">
        <div class="statistic-card">
            <el-statistic :value="statisticTransition.EUStored" suffix="EU" :formatter="(value) => formatNumber(value)">
                <template #title>
                    <div class="statistic-title" style="display: inline-flex; align-items: center">
                        兰波顿存储电量
                    </div>
                </template>
            </el-statistic>
            <div class="statistic-footer">
                <div class="footer-item">
                    <span>相较于上一次数据</span>
                    <span v-if="statistic.EUStored.change >= 0" class="green">
                        {{ (Math.abs(statistic.EUStored.change) * 100).toFixed(2) }}%
                        <el-icon>
                            <CaretTop />
                        </el-icon>
                    </span>
                    <span v-else class="red">
                        {{ (Math.abs(statistic.EUStored.change) * 100).toFixed(2) }}%
                        <el-icon>
                            <CaretBottom />
                        </el-icon>
                    </span>
                </div>
            </div>
        </div>
        <div class="statistic-card">
            <el-statistic :value="statisticTransition.totalWirelessEU" suffix="EU"
                :formatter="(value) => formatNumber(value)">
                <template #title>
                    <div class="statistic-title" style="display: inline-flex; align-items: center">
                        无线电网电量
                        <el-tooltip effect="dark" content="该信息来源为兰波顿电容" placement="top">
                            <el-icon style="margin-left: 4px" :size="12">
                                <Warning />
                            </el-icon>
                        </el-tooltip>
                    </div>
                </template>
            </el-statistic>
            <div class="statistic-footer">
                <div class="footer-item">
                    <span>相较于上一次数据</span>
                    <span v-if="statistic.totalWirelessEU.change >= 0" class="green">
                        {{ (Math.abs(statistic.totalWirelessEU.change) * 100).toFixed(2) }}%
                        <el-icon>
                            <CaretTop />
                        </el-icon>
                    </span>
                    <span v-else class="red">
                        {{ (Math.abs(statistic.totalWirelessEU.change) * 100).toFixed(2) }}%
                        <el-icon>
                            <CaretBottom />
                        </el-icon>
                    </span>
                </div>
            </div>
        </div>

    </div>

    <el-button class="refresh-button" size="large" :loading="loading" circle @click="fetchData">
        <template #loading>
            <div class="custom-loading">
                <el-icon size="large">
                    <i class="el-icon is-loading"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
                            <path fill="currentColor"
                                d="M512 64a32 32 0 0 1 32 32v192a32 32 0 0 1-64 0V96a32 32 0 0 1 32-32m0 640a32 32 0 0 1 32 32v192a32 32 0 1 1-64 0V736a32 32 0 0 1 32-32m448-192a32 32 0 0 1-32 32H736a32 32 0 1 1 0-64h192a32 32 0 0 1 32 32m-640 0a32 32 0 0 1-32 32H96a32 32 0 0 1 0-64h192a32 32 0 0 1 32 32M195.2 195.2a32 32 0 0 1 45.248 0L376.32 331.008a32 32 0 0 1-45.248 45.248L195.2 240.448a32 32 0 0 1 0-45.248zm452.544 452.544a32 32 0 0 1 45.248 0L828.8 783.552a32 32 0 0 1-45.248 45.248L647.744 692.992a32 32 0 0 1 0-45.248zM828.8 195.264a32 32 0 0 1 0 45.184L692.992 376.32a32 32 0 0 1-45.248-45.248l135.808-135.808a32 32 0 0 1 45.248 0m-452.544 452.48a32 32 0 0 1 0 45.248L240.448 828.8a32 32 0 0 1-45.248-45.248l135.808-135.808a32 32 0 0 1 45.248 0z">
                            </path>
                        </svg></i>
                </el-icon>
            </div>
        </template>
        <el-icon v-if="!loading" size="large">
            <RefreshRight />
        </el-icon>
    </el-button>
</template>

<script>
import { fetchStatus, addTask, createPollingController } from '@/utils/task'
import { useTransition, useDark } from '@vueuse/core'
import { ref } from 'vue'

export default {
    name: 'Monitor',
    components: {
    },
    data() {
        return {
            loading: true,
            statistic: {
                EUStored: {
                    change: 0,
                },
                totalWirelessEU: {
                    change: 0,
                },
            },

        };
    },
    setup() {
        const EUStoredValue = ref(0)
        const totalWirelessEUValue = ref(0)

        const statisticTransition = {
            EUStored: useTransition(EUStoredValue, { duration: 800, }),
            totalWirelessEU: useTransition(totalWirelessEUValue, { duration: 800, }),
        }

        const formatNumber = (num) => {
            return parseInt(num.value).toLocaleString()
        }

        const isDark = useDark()

        return {
            EUStoredValue,
            totalWirelessEUValue,
            statisticTransition,
            formatNumber,
            isDark,
        }
    },
    methods: {

        fetchData() {
            this.loading = true;
            addTask("monitor", null, () => {
                this.startPolling("monitor")
            })
        },
        startPolling(taskId) {
            this.pollingController = createPollingController();
            fetchStatus(taskId, this.handleTaskResult, null, this.handleTaskComplete, 1000, this.pollingController);
        },
        stopPolling() {
            if (this.pollingController) {
                this.pollingController.stop();
                console.log('Polling stopped.');
            }
        },
        handleTaskResult(data) {
            if (data.result) {
                try {
                    // 将列表转换为对象的函数
                    function parseDataToObject(dataArray) {
                        const parsedObject = {};
                        dataArray.forEach((item) => {
                            const splitIndex = item.indexOf(':');
                            if (splitIndex !== -1) {
                                const key = item.slice(0, splitIndex).trim();
                                const value = item.slice(splitIndex + 1).trim();
                                parsedObject[key] = value;
                            }
                        });
                        return parsedObject;
                    }
                    // 使用正则提取纯数字
                    function extractNumber(str) {
                        return parseInt(str.replace(/[^0-9]/g, ''));
                    }

                    let { last, current } = data.result;

                    // 解析 current 和 last 数据为对象
                    const currentObj = parseDataToObject(current[0]);
                    const lastObj = last ? parseDataToObject(last[0]) : null;

                    // 提取 current 数据
                    const currentEUStored = extractNumber(currentObj["EU Stored (exact)"].replace(/,/g, ''));
                    const currentTotalWirelessEU = extractNumber(currentObj["Total wireless EU (exact)"].replace(/,/g, ''));

                    // 计算 EUStored 的变化
                    if (lastObj && lastObj["EU Stored (exact)"]) {
                        const lastEUStored = extractNumber(lastObj["EU Stored (exact)"].replace(/,/g, ''));
                        this.statistic.EUStored.change = (currentEUStored - lastEUStored) / lastEUStored;
                    } else {
                        this.statistic.EUStored.change = 0; // 如果没有 last 数据，change 设为 0
                    }
                    this.EUStoredValue = currentEUStored;

                    // 计算 totalWirelessEU 的变化
                    if (lastObj && lastObj["Total wireless EU (exact)"]) {
                        const lastTotalWirelessEU = extractNumber(lastObj["Total wireless EU (exact)"].replace(/,/g, ''));
                        this.statistic.totalWirelessEU.change = (currentTotalWirelessEU - lastTotalWirelessEU) / lastTotalWirelessEU;
                    } else {
                        this.statistic.totalWirelessEU.change = 0;
                    }
                    this.totalWirelessEUValue = currentTotalWirelessEU;




                } catch (e) {
                    console.error(e, data);
                    this.$message.warning(e);
                }
            } else {
                this.$message.warning(`返回数据为空!`);
            }
        },
        handleTaskComplete() {
            this.loading = false;
        },
    },
    mounted() {
        this.startPolling("monitor");
    },
};
</script>

<style scoped>
.refresh-button {
    position: absolute !important;
    right: 36px;
    top: 75px;
}

.statistic-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    gap: 20px;
}

.statistic-container .el-statistic {
    flex: 1 1 20%;
    min-width: 300px;
    /* text-align: center; */
}

@media (max-width: 1400px) {
    .statistic-container .el-statistic {
        flex: 1 1 45%;
    }
}

@media (max-width: 900px) {
    .statistic-container .el-statistic {
        flex: 1 1 100%;
    }
}


:global(h2#card-usage ~ .example .example-showcase) {
    background-color: var(--el-fill-color) !important;
}

.el-statistic {
    --el-statistic-content-font-size: 28px;
}

.statistic-card {
    height: 100%;
    padding: 40px;
    border-radius: 4px;
    background-color: var(--el-bg-color-overlay);
}

.statistic-title {
    font-size: 16px;
}

.statistic-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    font-size: 12px;
    color: var(--el-text-color-regular);
    margin-top: 16px;
}

.statistic-footer .footer-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.statistic-footer .footer-item span:last-child {
    display: inline-flex;
    align-items: center;
    margin-left: 4px;
}

.green {
    color: var(--el-color-success);
}

.red {
    color: var(--el-color-error);
}
</style>

<style>
html.dark {
    .statistic-card {
        background: none;
    }
}
</style>