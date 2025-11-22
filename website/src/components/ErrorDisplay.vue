<template>
    <div class="error-container">
        <el-empty description=" ">
            <template #image>
                <el-icon :size="80" color="#f56c6c">
                    <CircleClose />
                </el-icon>
            </template>
            <template #description>
                <el-space direction="vertical" :size="16">
                    <el-text class="error-title" size="large">数据加载失败</el-text>
                    <el-text class="error-message" type="danger">{{ errorMessage }}</el-text>
                    <el-text class="error-hint" type="info">请检查数据源是否正确配置</el-text>
                </el-space>
            </template>
            <el-button type="primary" @click="handleRefresh">
                <el-icon style="margin-right: 4px;">
                    <Refresh />
                </el-icon>
                刷新页面
            </el-button>
        </el-empty>
    </div>
</template>

<script>
export default {
    name: 'ErrorDisplay',
    props: {
        errorMessage: {
            type: String,
            default: '未知错误'
        }
    },
    methods: {
        handleRefresh() {
            location.reload();
        }
    }
};
</script>

<style scoped>
.error-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    padding: 40px 20px;
}

.error-title {
    font-size: 20px;
    font-weight: 600;
}

.error-message {
    font-size: 16px;
    max-width: 600px;
    word-break: break-word;
}

.error-hint {
    font-size: 14px;
}
</style>

