<template>
    <div class="statistic-card">
        <el-statistic :value="displayValue" :suffix="suffix" :formatter="formatter">
            <template #title>
                <div class="statistic-title" style="display: inline-flex; align-items: center">
                    {{ title }}
                    <el-tooltip v-if="tooltip" effect="dark" :content="tooltip" placement="top">
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
                <span v-if="change >= 0" class="green">
                    {{ (Math.abs(change) * 100).toFixed(2) }}%
                    <el-icon>
                        <CaretTop />
                    </el-icon>
                </span>
                <span v-else class="red">
                    {{ (Math.abs(change) * 100).toFixed(2) }}%
                    <el-icon>
                        <CaretBottom />
                    </el-icon>
                </span>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'StatisticCard',
    props: {
        title: {
            type: String,
            required: true,
        },
        displayValue: {
            type: [Number, Object],
            required: true,
        },
        suffix: {
            type: String,
            default: 'EU',
        },
        change: {
            type: Number,
            default: 0,
        },
        tooltip: {
            type: String,
            default: '',
        },
        formatter: {
            type: Function,
            default: (value) => parseInt(value.value).toLocaleString(),
        },
    },
};
</script>

<style scoped>
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

@media (max-width: 600px) {
    .statistic-card {
        padding: 20px;
    }
}
</style>

<style>
html.dark {
    .statistic-card {
        background: none;
    }
}
</style>
