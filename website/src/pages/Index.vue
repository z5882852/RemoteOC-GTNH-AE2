<template>
    <div>
        <!-- 错误显示组件 -->
        <ErrorDisplay v-if="hasLoadError" :error-message="getErrorMessage" />

        <!-- 正常内容 -->
        <template v-else>
            <el-row :gutter="20" justify="center" align="middle" style="margin: 0; margin-top: 5%;">
                <el-col :span="8" style="text-align: center;">
                    <el-image src="/img/gtnh.png" alt="GTNH" style="width: 40%; height: auto;" />
                </el-col>
                <el-col :span="8" style="text-align: center;">
                    <el-image src="/img/oc.png" alt="OpenComputers" style="width: 40%; height: auto;" />
                </el-col>
            </el-row>

            <div style="text-align: center; margin-top: 5%;">
                <el-space direction="vertical" style="gap: 24px 0px">
                    <el-text class="title" size="large">GTNH赛博监工</el-text>
                    <el-text size="large">基于 OpenComputers 的 GTNH AE2 远程控制框架</el-text>
                    <el-text size="large">当前版本 <el-tag size="large">GTNH {{ $gameVersion }}</el-tag></el-text>

                    <div class="link-grid">
                        <el-link :href="`${$defaultLinkPrefix}/${$userName}/${$repoName}`" target="_blank" :underline="false">
                            <div class="link-item">
                                <el-icon :size="36">
                                    <svg t="1734116698512" class="icon" viewBox="0 0 1024 1024" version="1.1"
                                        xmlns="http://www.w3.org/2000/svg" p-id="4255" width="256" height="256">
                                        <path
                                            d="M511.6 76.3C264.3 76.2 64 276.4 64 523.5 64 718.9 189.3 885 363.8 946c23.5 5.9 19.9-10.8 19.9-22.2v-77.5c-135.7 15.9-141.2-73.9-150.3-88.9C215 726 171.5 718 184.5 703c30.9-15.9 62.4 4 98.9 57.9 26.4 39.1 77.9 32.5 104 26 5.7-23.5 17.9-44.5 34.7-60.8-140.6-25.2-199.2-111-199.2-213 0-49.5 16.3-95 48.3-131.7-20.4-60.5 1.9-112.3 4.9-120 58.1-5.2 118.5 41.6 123.2 45.3 33-8.9 70.7-13.6 112.9-13.6 42.4 0 80.2 4.9 113.5 13.9 11.3-8.6 67.3-48.8 121.3-43.9 2.9 7.7 24.7 58.3 5.5 118 32.4 36.8 48.9 82.7 48.9 132.3 0 102.2-59 188.1-200 212.9 23.5 23.2 38.1 55.4 38.1 91v112.5c0.8 9 0 17.9 15 17.9 177.1-59.7 304.6-227 304.6-424.1 0-247.2-200.4-447.3-447.5-447.3z"
                                            p-id="4256" data-spm-anchor-id="a313x.search_index.0.i0.21af3a818Eu8eB">
                                        </path>
                                    </svg>
                                </el-icon>
                                <el-text>仓库</el-text>
                            </div>
                        </el-link>

                        <el-link :href="`${$defaultLinkPrefix}/${$userName}`" target="_blank" :underline="false">
                            <div class="link-item">
                                <el-icon :size="36">
                                    <svg t="1734116698512" class="icon" viewBox="0 0 1024 1024" version="1.1"
                                        xmlns="http://www.w3.org/2000/svg" p-id="4255" width="256" height="256">
                                        <path
                                            d="M511.6 76.3C264.3 76.2 64 276.4 64 523.5 64 718.9 189.3 885 363.8 946c23.5 5.9 19.9-10.8 19.9-22.2v-77.5c-135.7 15.9-141.2-73.9-150.3-88.9C215 726 171.5 718 184.5 703c30.9-15.9 62.4 4 98.9 57.9 26.4 39.1 77.9 32.5 104 26 5.7-23.5 17.9-44.5 34.7-60.8-140.6-25.2-199.2-111-199.2-213 0-49.5 16.3-95 48.3-131.7-20.4-60.5 1.9-112.3 4.9-120 58.1-5.2 118.5 41.6 123.2 45.3 33-8.9 70.7-13.6 112.9-13.6 42.4 0 80.2 4.9 113.5 13.9 11.3-8.6 67.3-48.8 121.3-43.9 2.9 7.7 24.7 58.3 5.5 118 32.4 36.8 48.9 82.7 48.9 132.3 0 102.2-59 188.1-200 212.9 23.5 23.2 38.1 55.4 38.1 91v112.5c0.8 9 0 17.9 15 17.9 177.1-59.7 304.6-227 304.6-424.1 0-247.2-200.4-447.3-447.5-447.3z"
                                            p-id="4256" data-spm-anchor-id="a313x.search_index.0.i0.21af3a818Eu8eB">
                                        </path>
                                    </svg>
                                </el-icon>
                                <el-text>主页</el-text>
                            </div>
                        </el-link>
                    </div>
                </el-space>
            </div>
            <div v-if="isMobile" style="text-align: center; margin-top: 5%;">
                <el-space direction="vertical" style="gap: 24px 0px">
                    <el-text>使用PC端以获得更好的体验</el-text>
                </el-space>
            </div>
        </template>
    </div>
</template>

<script>
import { inject } from 'vue';
import ErrorDisplay from '@/components/ErrorDisplay.vue';

export default {
    name: 'Index',
    components: {
        ErrorDisplay,
    },
    data() {
        return {
        };
    },
    setup() {
        const isMobile = inject('isMobile');
        const loadError = inject('loadError');
        const errorMessage = inject('errorMessage');
        return {
            isMobile,
            loadError,
            errorMessage,
        };
    },
    computed: {
        hasLoadError() {
            return this.loadError();
        },
        getErrorMessage() {
            return this.errorMessage();
        },
    },
    methods: {
    },
    created() {
    },
    beforeUnmount() {
    },
};
</script>

<style scoped>
.title {
    font-size: 28px;
}

.link-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
}

.link-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    justify-content: space-evenly;
    width: 48px;
    height: 72px;
}
</style>