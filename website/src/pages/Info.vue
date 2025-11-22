<template>
    <el-descriptions border :column="1" :size="isMobile ? '' : 'large'" :label-width="120" style="margin: 20px;"
        v-loading="loading">
        <el-descriptions-item label="GTNH版本">{{ $gameVersion }}</el-descriptions-item>
        <el-descriptions-item label="Web版本">{{ version }}</el-descriptions-item>
        <el-descriptions-item label="后端版本">{{ meta.version }}</el-descriptions-item>
        <el-descriptions-item label="OC客户端">
            <el-text style="cursor: pointer;" @click="handleClientDialog">
                {{ meta.device_num }}台 (点击查看详情)
            </el-text>
        </el-descriptions-item>
        <el-descriptions-item label="开源地址">
            <el-link :href="`${$defaultLinkPrefix}/${$userName}/${$repoName}`" target="_blank" :underline="false">
                {{ $defaultLinkPrefix }}/{{ $userName }}/{{ $repoName }}
            </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="问题反馈">
            <el-link :href="`${$defaultLinkPrefix}/${$userName}/${$repoName}/issues`" target="_blank"
                :underline="false">
                {{ $defaultLinkPrefix }}/{{ $userName }}/{{ $repoName }}/issues
            </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="接口文档">
            <el-link :href="backendUrl ? `${backendUrl}/docs` : '#'" target="_blank"
                :underline="false">
                {{ backendUrl ? `${backendUrl}/docs` : '-' }}
            </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="许可信息">MIT license</el-descriptions-item>
    </el-descriptions>
    <el-dialog v-model="client.show" class="client-dialog" style="height: 400px;" title="客户端信息" align-center>
        <el-table :data="client.data" v-loading="client.loading" :height="340" width="100%" stripe border>
            <el-table-column type="index" label="序号" width="80" align="center"></el-table-column>
            <el-table-column property="id" label="客户端id" align="center" />
            <el-table-column property="last_active_time" label="最后活跃时间" align="center" />
        </el-table>
    </el-dialog>
</template>

<script>
import { inject } from 'vue';
import Setting from '@/utils/setting';
import Requests from '@/utils/requests';

export default {
    name: 'Info',
    data() {
        return {
            loading: false,
            backendUrl: Setting.get('backendUrl'),
            version: __VERSION__,
            meta: {
                version: "-",
                device_num: 0,
            },
            client: {
                show: false,
                loading: false,
                data: [],
            },
            license: "",
        };
    },
    setup() {
        const isMobile = inject('isMobile');
        return {
            isMobile,
        };
    },
    methods: {
        async getMeta() {
            try {
                if (!this.backendUrl) {
                    this.$message.warning('后端地址未配置');
                    return;
                }
                this.loading = true;
                const response = await Requests.get('/api/info/meta');
                const data = response.data;
                if (data.code === 200) {
                    this.meta = data.data;
                    this.loading = false;
                } else {
                    this.$message.error(`获取后端信息失败: ${data.code}, ${data.message ? data.message : data}`);
                    console.error(data);
                    this.loading = false;
                }
            } catch (error) {
                this.$message.error(`获取后端信息失败: ${error}`);
                console.error('Error fetching meta:', error);
                this.loading = false;
            }
        },
        async getClients() {
            try {
                if (!this.backendUrl) {
                    this.$message.warning('后端地址未配置');
                    return;
                }
                this.client.loading = true;
                const response = await Requests.get('/api/info/devices');
                const data = response.data;
                if (data.code === 200) {
                    this.client.data = data.data.map((item) => {
                        return {
                            id: item.id,
                            last_active_time: item.active[item.active.length - 1].time,
                        };
                    });
                    this.client.loading = false;
                } else {
                    this.$message.error(`获取客户端信息失败: ${data.code}, ${data.message ? data.message : data}`);
                    console.error(data);
                    this.client.loading = false;
                }
            } catch (error) {
                this.$message.error(`获取客户端信息失败: ${error}`);
                console.error('Error fetching clients:', error);
                this.client.loading = false;
            }
        },
        handleClientDialog() {
            this.client.show = true;
            this.getClients();
        },
    },
    created() {
        this.getMeta();
    },
    beforeUnmount() {
    },
};
</script>

<style>
@media screen and (max-width: 768px) {
    .client-dialog {
        width: 100% !important;
        max-width: 400px;
    }
}
</style>