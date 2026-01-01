<template>
    <div class="trend-card">
        <div class="trend-header">
            <h3 class="trend-title">
                历史趋势
                <el-tooltip effect="dark" placement="top">
                    <template #content>
                        <div style="line-height: 1.8;">
                            <div><b>数字单位说明：</b></div>
                            <div>K = 千 (10³)</div>
                            <div>M = 百万 (10⁶)</div>
                            <div>G = 十亿 (10⁹)</div>
                            <div>T = 万亿 (10¹²)</div>
                            <div>P = 千万亿 (10¹⁵)</div>
                            <div>E = 百京 (10¹⁸)</div>
                            <div>Z = 十垓 (10²¹)</div>
                            <div>Y = 千穰 (10²⁴)</div>
                        </div>
                    </template>
                    <el-icon style="margin-left: 6px; cursor: help;" :size="14">
                        <QuestionFilled />
                    </el-icon>
                </el-tooltip>
            </h3>
            <div class="trend-controls">
                <div class="control-item">
                    <span class="control-label">时间范围</span>
                    <el-select v-model="timeRangeValue" size="small" @change="handleTimeRangeChange">
                        <el-option label="近1小时" :value="1" />
                        <el-option label="近4小时" :value="4" />
                        <el-option label="近12小时" :value="12" />
                        <el-option label="近1天" :value="24" />
                        <el-option label="近3天" :value="72" />
                        <el-option label="近7天" :value="168" />
                        <el-option label="自定义" value="custom" />
                    </el-select>
                </div>
                <div class="control-item date-picker-item" v-if="timeRangeValue === 'custom'">
                    <el-date-picker
                        v-model="customTimeRangeLocal"
                        type="datetimerange"
                        range-separator="至"
                        start-placeholder="开始时间"
                        end-placeholder="结束时间"
                        size="small"
                        :teleported="true"
                        :shortcuts="dateShortcuts"
                        popper-class="custom-date-picker-popper"
                        :popper-options="{
                            placement: 'bottom-start',
                            modifiers: [
                                { name: 'flip', options: { fallbackPlacements: ['top-start', 'bottom-end', 'top-end'] } },
                                { name: 'preventOverflow', options: { boundary: 'viewport', padding: 8, altAxis: true } },
                                { name: 'offset', options: { offset: [0, 4] } }
                            ]
                        }"
                        @change="handleCustomTimeChange"
                    />
                </div>
                <div class="control-item">
                    <span class="control-label">时间粒度</span>
                    <el-select v-model="granularityValue" size="small" @change="handleGranularityChange">
                        <el-option label="无" value="none" />
                        <el-option label="1小时平均" value="1h" />
                    </el-select>
                </div>
            </div>
        </div>

        <!-- 图表容器 -->
        <div class="chart-container" v-loading="loading">
            <!-- 空状态 -->
            <el-empty v-if="!loading && isEmpty" description="暂无数据" />
            <!-- 图表 -->
            <template v-else>
                <div ref="euStoredChart" class="chart"></div>
                <div ref="wirelessEUChart" class="chart"></div>
            </template>
        </div>
    </div>
</template>

<script>
import * as echarts from 'echarts'
import { useDark } from '@vueuse/core'
import { QuestionFilled } from '@element-plus/icons-vue'

export default {
    components: {
        QuestionFilled,
    },
    name: 'TrendChart',
    props: {
        historyData: {
            type: Array,
            default: () => [],
        },
        timeRange: {
            type: [Number, String],
            default: 4,
        },
        granularity: {
            type: String,
            default: 'none',
        },
        customStartTime: {
            type: Number,
            default: null,
        },
        customEndTime: {
            type: Number,
            default: null,
        },
        loading: {
            type: Boolean,
            default: false,
        },
    },
    emits: ['update:timeRange', 'update:granularity', 'update:customStartTime', 'update:customEndTime'],
    data() {
        const now = new Date();
        const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 3600 * 1000);
        return {
            chartInstances: {
                euStored: null,
                wirelessEU: null,
            },
            chartStats: {
                euStored: { max: null, min: null, avg: null },
                wirelessEU: { max: null, min: null, avg: null },
            },
            customTimeRangeLocal: [threeDaysAgo, now],
            dateShortcuts: [
                {
                    text: '最近1天',
                    value: () => {
                        const end = new Date();
                        const start = new Date(end.getTime() - 24 * 3600 * 1000);
                        return [start, end];
                    },
                },
                {
                    text: '最近3天',
                    value: () => {
                        const end = new Date();
                        const start = new Date(end.getTime() - 3 * 24 * 3600 * 1000);
                        return [start, end];
                    },
                },
                {
                    text: '最近7天',
                    value: () => {
                        const end = new Date();
                        const start = new Date(end.getTime() - 7 * 24 * 3600 * 1000);
                        return [start, end];
                    },
                },
            ],
        };
    },
    computed: {
        timeRangeValue: {
            get() {
                return this.timeRange;
            },
            set(value) {
                this.$emit('update:timeRange', value);
            },
        },
        granularityValue: {
            get() {
                return this.granularity;
            },
            set(value) {
                this.$emit('update:granularity', value);
            },
        },
        isEmpty() {
            return !this.historyData || this.historyData.length === 0;
        },
    },
    setup() {
        const isDark = useDark();
        return { isDark };
    },
    watch: {
        historyData: {
            handler(newData) {
                if (newData && newData.length > 0) {
                    this.processChartData(newData);
                }
            },
            deep: true,
        },
        isDark() {
            // 暗色模式切换时更新图表颜色
            if (this.historyData && this.historyData.length > 0) {
                this.processChartData(this.historyData);
            }
        },
    },
    methods: {
        handleTimeRangeChange(val) {
            // 当切换到自定义时，自动应用默认的自定义时间范围
            if (val === 'custom') {
                this.handleCustomTimeChange(this.customTimeRangeLocal);
            }
        },
        handleGranularityChange() {
            // 父组件会响应 v-model 更新并重新获取数据
        },
        handleCustomTimeChange(val) {
            if (val && val.length === 2) {
                const startTime = Math.floor(val[0].getTime() / 1000);
                const endTime = Math.floor(val[1].getTime() / 1000);
                this.$emit('update:customStartTime', startTime);
                this.$emit('update:customEndTime', endTime);
            }
        },
        initCharts() {
            const textColor = this.isDark ? '#E5EAF3' : '#1a1a1a';

            // EU存储电量图表
            this.chartInstances.euStored = echarts.init(this.$refs.euStoredChart);
            this.chartInstances.euStored.setOption(this.getChartOption('兰波顿存储电量', textColor));

            // 无线电网电量图表
            this.chartInstances.wirelessEU = echarts.init(this.$refs.wirelessEUChart);
            this.chartInstances.wirelessEU.setOption(this.getChartOption('无线电网电量', textColor));
        },
        getChartOption(title, textColor) {
            return {
                title: {
                    text: title,
                    left: 'center',
                    textStyle: { color: textColor, fontSize: 14 },
                },
                tooltip: {
                    trigger: 'item',
                    backgroundColor: 'rgba(50, 50, 50, 0.9)',
                    borderColor: '#333',
                    borderWidth: 1,
                    padding: [8, 12],
                    textStyle: {
                        color: '#fff',
                        fontSize: 13,
                    },
                    formatter: (params) => {
                        const time = params.name || '';
                        const formatted = this.formatLargeNumber(params.value);
                        const raw = Math.round(params.value).toLocaleString();
                        return `<div style="font-weight: bold; margin-bottom: 4px;">${time}</div>
                                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${params.color};margin-right:6px;"></span>${formatted}<br/>
                                <div style="margin-left: 16px; color: #aaa; font-size: 12px;">${raw}</div>`;
                    },
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true,
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: [],
                    axisLabel: {
                        color: textColor,
                        rotate: 45,
                        fontSize: 10,
                        interval: 'auto',
                    },
                },
                yAxis: {
                    type: 'value',
                    axisLabel: {
                        color: textColor,
                        formatter: (value) => this.formatLargeNumber(value),
                    },
                },
                series: [{
                    name: title,
                    type: 'line',
                    smooth: true,
                    data: [],
                    showSymbol: true,
                    symbol: 'circle',
                    symbolSize: 6,
                    emphasis: {
                        scale: true,
                        focus: 'series',
                        itemStyle: {
                            borderWidth: 2,
                            borderColor: '#fff',
                        }
                    },
                    areaStyle: {
                        opacity: 0.3,
                    },
                    lineStyle: {
                        width: 2,
                    },
                    itemStyle: {
                        color: '#66ccff',
                    },
                }],
            };
        },
        processChartData(history) {
            let processedData = history;

            // 如果选择了时间粒度，进行聚合
            if (this.granularity === '1h') {
                processedData = this.aggregateByHour(history);
            }

            // 计算统计信息
            const euStoredValues = processedData.map(item => item.results.eu_stored);
            const wirelessEUValues = processedData.map(item => item.results.total_wireless_eu);

            this.chartStats.euStored = {
                max: Math.max(...euStoredValues),
                min: Math.min(...euStoredValues),
                avg: euStoredValues.reduce((a, b) => a + b, 0) / euStoredValues.length,
            };

            this.chartStats.wirelessEU = {
                max: Math.max(...wirelessEUValues),
                min: Math.min(...wirelessEUValues),
                avg: wirelessEUValues.reduce((a, b) => a + b, 0) / wirelessEUValues.length,
            };

            // 更新图表
            this.updateCharts(processedData);
        },
        aggregateByHour(history) {
            const hourlyData = {};

            history.forEach(item => {
                const date = new Date(item.completed_time);
                const hourKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;

                if (!hourlyData[hourKey]) {
                    hourlyData[hourKey] = {
                        count: 0,
                        eu_stored_sum: 0,
                        wireless_eu_sum: 0,
                        time: new Date(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours()).toISOString(),
                    };
                }

                hourlyData[hourKey].count++;
                hourlyData[hourKey].eu_stored_sum += item.results.eu_stored;
                hourlyData[hourKey].wireless_eu_sum += item.results.total_wireless_eu;
            });

            return Object.values(hourlyData).map(item => ({
                completed_time: item.time,
                results: {
                    eu_stored: item.eu_stored_sum / item.count,
                    total_wireless_eu: item.wireless_eu_sum / item.count,
                },
            })).sort((a, b) => new Date(a.completed_time) - new Date(b.completed_time));
        },
        updateCharts(data) {
            const times = data.map(item => {
                const date = new Date(item.completed_time);
                return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
            });

            const euStoredData = data.map(item => item.results.eu_stored);
            const wirelessEUData = data.map(item => item.results.total_wireless_eu);

            const textColor = this.isDark ? '#E5EAF3' : '#1a1a1a';

            // 更新EU存储电量图表
            this.chartInstances.euStored.setOption({
                xAxis: { data: times, axisLabel: { color: textColor } },
                yAxis: { axisLabel: { color: textColor } },
                title: { textStyle: { color: textColor } },
                graphic: [{
                    type: 'text',
                    left: 60,
                    top: 30,
                    style: {
                        text: `最大: ${this.formatLargeNumber(this.chartStats.euStored.max)}  最小: ${this.formatLargeNumber(this.chartStats.euStored.min)}  平均: ${this.formatLargeNumber(this.chartStats.euStored.avg)}`,
                        fill: textColor,
                        fontSize: 12,
                    },
                }],
                series: [{
                    data: euStoredData,
                    markLine: {
                        silent: true,
                        symbol: ['none', 'none'],
                        label: {
                            formatter: (params) => `${params.name}: ${this.formatLargeNumber(params.value)}`,
                        },
                        data: [
                            { type: 'max', name: '最大' },
                            { type: 'min', name: '最小' },
                            { type: 'average', name: '平均' },
                        ],
                    },
                }],
            });

            // 更新无线电网电量图表
            this.chartInstances.wirelessEU.setOption({
                xAxis: { data: times, axisLabel: { color: textColor } },
                yAxis: { axisLabel: { color: textColor } },
                title: { textStyle: { color: textColor } },
                graphic: [{
                    type: 'text',
                    left: 60,
                    top: 30,
                    style: {
                        text: `最大: ${this.formatLargeNumber(this.chartStats.wirelessEU.max)}  最小: ${this.formatLargeNumber(this.chartStats.wirelessEU.min)}  平均: ${this.formatLargeNumber(this.chartStats.wirelessEU.avg)}`,
                        fill: textColor,
                        fontSize: 12,
                    },
                }],
                series: [{
                    data: wirelessEUData,
                    markLine: {
                        silent: true,
                        symbol: ['none', 'none'],
                        label: {
                            formatter: (params) => `${params.name}: ${this.formatLargeNumber(params.value)}`,
                        },
                        data: [
                            { type: 'max', name: '最大' },
                            { type: 'min', name: '最小' },
                            { type: 'average', name: '平均' },
                        ],
                    },
                }],
            });
        },
        formatLargeNumber(num) {
            if (num === null || num === undefined) return '-';
            if (num >= 1e24) return (num / 1e24).toFixed(2) + 'Y';
            if (num >= 1e21) return (num / 1e21).toFixed(2) + 'Z';
            if (num >= 1e18) return (num / 1e18).toFixed(2) + 'E';
            if (num >= 1e15) return (num / 1e15).toFixed(2) + 'P';
            if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
            if (num >= 1e9) return (num / 1e9).toFixed(2) + 'G';
            if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
            if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
            return num.toFixed(0);
        },
        resizeCharts() {
            if (this.chartInstances.euStored) this.chartInstances.euStored.resize();
            if (this.chartInstances.wirelessEU) this.chartInstances.wirelessEU.resize();
        },
    },
    mounted() {
        this.$nextTick(() => {
            this.initCharts();
        });
        window.addEventListener('resize', this.resizeCharts);
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.resizeCharts);
        if (this.chartInstances.euStored) this.chartInstances.euStored.dispose();
        if (this.chartInstances.wirelessEU) this.chartInstances.wirelessEU.dispose();
    },
};
</script>

<style scoped>
.trend-card {
    margin-top: 20px;
    padding: 20px;
    border-radius: 4px;
    background-color: var(--el-bg-color-overlay);
}

.trend-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
}

.trend-title {
    margin: 0;
    font-size: 18px;
    font-weight: 500;
}

.trend-controls {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
}

.control-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.control-label {
    font-size: 13px;
    color: var(--el-text-color-regular);
    white-space: nowrap;
}

.trend-controls .el-select {
    width: 110px;
}

.chart-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.chart {
    width: 100%;
    height: 300px;
}

@media (max-width: 900px) {
    .trend-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .trend-controls {
        width: 100%;
    }

    .control-item {
        flex: 1;
        min-width: 140px;
    }

    .date-picker-item {
        width: 100%;
        max-width: 100%;
        overflow-x: auto;
    }

    .chart {
        height: 250px;
    }
}

@media (max-width: 600px) {
    .trend-card {
        padding: 12px;
    }

    .trend-controls {
        flex-direction: column;
    }

    .control-item {
        width: 100%;
    }

    .trend-controls .el-select {
        flex: 1;
    }
}
</style>

<style>
html.dark {
    .trend-card {
        background: none;
    }
}

/* 日期选择器弹窗自适应 */
.custom-date-picker-popper {
    max-width: calc(100vw - 16px) !important;
}

.custom-date-picker-popper .el-picker-panel__body-wrapper {
    max-width: 100%;
    overflow-x: auto;
}
</style>
