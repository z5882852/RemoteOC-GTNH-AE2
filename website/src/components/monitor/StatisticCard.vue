<template>
    <div class="statistic-card">
        <el-statistic :value="displayValue" :suffix="suffix" :formatter="internalFormatter">
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
            default: null,
        },
    },
    computed: {
        internalFormatter() {
            if (this.formatter) {
                return this.formatter;
            }
            // 显示完整数字格式
            return (value) => {
                const num = value.value;
                if (num === null || num === undefined) return '-';
                // 使用 toLocaleString 显示完整数字，最大支持 20 位有效数字
                console.log(num, num.toLocaleString('zh-CN', { maximumFractionDigits: 0 }));
                return num.toLocaleString('zh-CN', { maximumFractionDigits: 0 });
            };
        },
    },
    methods: {
        formatLargeNumber(num) {
            if (num === null || num === undefined) return '-';
            const absNum = Math.abs(num);
            const sign = num < 0 ? '-' : '';
            if (absNum >= 1e24) return sign + (absNum / 1e24).toFixed(2) + 'Y';
            if (absNum >= 1e21) return sign + (absNum / 1e21).toFixed(2) + 'Z';
            if (absNum >= 1e18) return sign + (absNum / 1e18).toFixed(2) + 'E';
            if (absNum >= 1e15) return sign + (absNum / 1e15).toFixed(2) + 'P';
            if (absNum >= 1e12) return sign + (absNum / 1e12).toFixed(2) + 'T';
            if (absNum >= 1e9) return sign + (absNum / 1e9).toFixed(2) + 'G';
            if (absNum >= 1e6) return sign + (absNum / 1e6).toFixed(2) + 'M';
            if (absNum >= 1e3) return sign + (absNum / 1e3).toFixed(2) + 'K';
            return Math.round(num).toLocaleString();
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
