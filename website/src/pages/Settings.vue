<template>
    <div>
        <el-form label-position="left" label-width="auto" style="max-width: 600px; margin: 20px;">
            <el-space fill style="width: 100%; margin-bottom: 5px;">
                <el-alert type="info" show-icon :closable="false">
                    <p>该页面内容请勿泄露给他人</p>
                </el-alert>
            </el-space>
            <el-form-item label="页面标题">
                <el-input v-model="title" placeholder="Title"></el-input>
            </el-form-item>
            <el-form-item label="启用监控页面">
                <el-checkbox v-model="showMoniter" type="checkbox"></el-checkbox>
            </el-form-item>
            <el-form-item label="服务端地址">
                <el-input v-model="backendUrl" placeholder="Backend URL"></el-input>
            </el-form-item>
            <el-form-item label="服务端令牌">
                <el-input v-model="token" placeholder="Token" type="password" show-password></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="saveSettings">保存</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
export default {
    name: 'Settings',
    data() {
        return {
            title: localStorage.getItem("pageTitle") || "GTNH赛博监工",
            backendUrl: localStorage.getItem('backendUrl') || '',
            token: localStorage.getItem('token') || '',
            showMoniter: localStorage.getItem('showMoniter') === "true" || false,
        };
    },
    methods: {
        saveSettings() {
            localStorage.setItem('pageTitle', this.title);
            localStorage.setItem('backendUrl', this.backendUrl);
            localStorage.setItem('token', this.token);
            localStorage.setItem('showMoniter', this.showMoniter);
            this.$message.success('设置已保存，刷新网页生效');
        },
    },
};
</script>