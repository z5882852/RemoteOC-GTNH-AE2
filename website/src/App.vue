<template>
    <el-container style="height: 100%;">
        <el-header style="height: 60px;">
            <div class="toolbar">
                <div v-if="isMobile" class="content-left">
                    <!-- <el-button size="large" v-if="isMobile" @click="toggleDrawer" icon="Expand"></el-button> -->
                    <el-icon size="24" @click="toggleDrawer">
                        <Expand />
                    </el-icon>
                </div>
                <div class="title-container">
                    <el-link href="/" :underline="false">
                        <h1 class="title">{{ pageTitle }}</h1>
                    </el-link>
                </div>
                <div class="content">
                    <el-switch v-if="!isMobile" v-model="isDark" @change="toggleDark" size="large" style="margin-right: 10px;">
                        <template #active-action>
                            <el-icon>
                                <Moon />
                            </el-icon>
                        </template>
                        <template #inactive-action>
                            <el-icon>
                                <Sunny />
                            </el-icon>
                        </template>
                    </el-switch>
                    <el-link :href="`${$defaultLinkPrefix}/${$userName}/${$repoName}`" target="_blank" :underline="false">
                        <el-icon :size="30">
                            <svg t="1734116698512" class="icon" viewBox="0 0 1024 1024" version="1.1"
                                xmlns="http://www.w3.org/2000/svg" p-id="4255" width="256" height="256">
                                <path
                                    d="M511.6 76.3C264.3 76.2 64 276.4 64 523.5 64 718.9 189.3 885 363.8 946c23.5 5.9 19.9-10.8 19.9-22.2v-77.5c-135.7 15.9-141.2-73.9-150.3-88.9C215 726 171.5 718 184.5 703c30.9-15.9 62.4 4 98.9 57.9 26.4 39.1 77.9 32.5 104 26 5.7-23.5 17.9-44.5 34.7-60.8-140.6-25.2-199.2-111-199.2-213 0-49.5 16.3-95 48.3-131.7-20.4-60.5 1.9-112.3 4.9-120 58.1-5.2 118.5 41.6 123.2 45.3 33-8.9 70.7-13.6 112.9-13.6 42.4 0 80.2 4.9 113.5 13.9 11.3-8.6 67.3-48.8 121.3-43.9 2.9 7.7 24.7 58.3 5.5 118 32.4 36.8 48.9 82.7 48.9 132.3 0 102.2-59 188.1-200 212.9 23.5 23.2 38.1 55.4 38.1 91v112.5c0.8 9 0 17.9 15 17.9 177.1-59.7 304.6-227 304.6-424.1 0-247.2-200.4-447.3-447.5-447.3z"
                                    p-id="4256" data-spm-anchor-id="a313x.search_index.0.i0.21af3a818Eu8eB">
                                </path>
                            </svg>
                        </el-icon>
                    </el-link>
                </div>
            </div>
        </el-header>
        <el-container style="height: 100%;">
            <!-- PC 侧边栏 -->
            <el-aside v-if="!isMobile" width="200px" style="height: calc(100vh - 60px);">
                <PageMenu />
            </el-aside>

            <!-- 移动端抽屉 -->
            <el-drawer v-if="isMobile" v-model="drawerVisible" :title="pageTitle" direction="ltr" size="60%">
                <PageMenu :close-drawer="closeDrawer" />
            </el-drawer>
            <!-- 使用 v-if 控制子组件渲染 -->
            <el-main style="height: calc(100vh - 60px); padding: 0;">
                <router-view v-if="isDataLoaded" v-slot="{ Component }">
                    <keep-alive>
                        <component :is="Component" />
                    </keep-alive>
                </router-view>
            </el-main>
        </el-container>
    </el-container>
    <el-progress v-if="showProgress" :percentage="itemProgress + fluidsProgress" :status="progressStatus" striped
        striped-flow :stroke-width="15" :text-inside="true"
        style="position: fixed; top: calc(50% + 100px); left: 50%; transform: translateX(-50%); width: 20%; z-index: 9999;" />
</template>

<script>
import { ElLoading, ElMessage, ElProgress } from "element-plus";
import { inject } from "vue";
import { useDark, useToggle } from '@vueuse/core'

import itemUtil from "@/utils/items";
import PageMenu from "@/components/PageMenu.vue";
import Setting from '@/utils/setting';

export default {
    components: {
        ElProgress,
        PageMenu,
    },
    setup() {
        const isDark = useDark();
        const toggleDark = useToggle(isDark);
        const isMobile = inject('isMobile');
        return {
            isMobile,
            isDark,
            toggleDark,
        };
    },
    data() {
        return {
            pageTitle: "",
            loadingInstance: null,
            itemProgress: 0,
            fluidsProgress: 0,
            progressStatus: "",
            isDataLoaded: false,
            drawerVisible: false,
            showProgress: false,
            loadError: false,
            errorMessage: "",
        };
    },
    provide() {
        return {
            loadError: () => this.loadError,
            errorMessage: () => this.errorMessage,
        };
    },
    created() {
        this.pageTitle = Setting.get("pageTitle");
        document.title = this.pageTitle;
        this.loadItemData();
    },

    methods: {
        toggleDrawer() {
            this.drawerVisible = !this.drawerVisible;
        },
        closeDrawer() {
            this.drawerVisible = false;
        },
        handleSelect(key, keyPath) {
            this.$router.push({ name: key });
            if (this.isMobile) {
                this.drawerVisible = false;
            }
        },
        loadItemData() {
            this.loadingInstance = ElLoading.service({
                fullscreen: true,
                customClass: 'custom-loading',
                text: '加载中...',
            });

            let itemsLoaded = false;
            let fluidsLoaded = false;
            this.showProgress = true;

            const resourceUrl = Setting.get("resourceUrl");
            const useGzip = Setting.get("useGzip");
            const version = itemUtil.version.replace(/\./g, "");

            // 加载 items 数据
            itemUtil.loadItems((percent) => {
                console.log(`Items JSON loading: ${percent}%`);
                this.itemProgress = percent / 2;
                if (percent === 100) {
                    itemsLoaded = true;
                    if (itemsLoaded && fluidsLoaded) {
                        this.loadingInstance.close();
                        this.isDataLoaded = true;
                        this.showProgress = false;
                    }
                } else if (percent === -1) {
                    const itemsUrl = `${resourceUrl}/items_GTNH${version}.json${useGzip ? '.gz' : ''}`;
                    this.errorMessage = `加载 items 数据失败，数据源：${itemsUrl}`;
                    this.loadError = true;
                    this.isDataLoaded = true;
                    this.loadingInstance.close();
                    this.showProgress = false;
                    ElMessage.error("加载 items 数据失败！");
                }
            });

            // 加载 fluids 数据
            itemUtil.loadFluids((percent) => {
                console.log(`Fluids JSON loading: ${percent}%`);
                this.fluidsProgress = percent / 2;
                if (percent === 100) {
                    fluidsLoaded = true;
                    if (itemsLoaded && fluidsLoaded) {
                        this.loadingInstance.close();
                        this.isDataLoaded = true;
                        this.showProgress = false;
                    }
                } else if (percent === -1) {
                    const fluidsUrl = `${resourceUrl}/fluids_GTNH${version}.json${useGzip ? '.gz' : ''}`;
                    this.errorMessage = `加载 fluids 数据失败，数据源：${fluidsUrl}`;
                    this.loadError = true;
                    this.isDataLoaded = true;
                    this.loadingInstance.close();
                    this.showProgress = false;
                    ElMessage.error("加载 fluids 数据失败！");
                }
            });
        },
    },
};
</script>

<style scoped>
.el-container {
    height: 100%;
}

.el-header {
    position: relative;
    background-color: var(--el-color-primary-light-9);
    color: var(--el-text-color-primary);
    padding: 0 32px;
}

.toolbar {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    right: 20px;
}

.toolbar .content-left {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    flex-grow: 1;
    height: 100%;
}

.toolbar .title-container {
    display: flex;
    align-items: center;
    height: 100%;
}

.toolbar .content {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    flex-grow: 1;
    height: 100%;
}

.title {
    font-size: 18px;
}

.el-menu-vertical-page {
    border: none;
}
</style>

<style>
/* 隐藏默认的加载图标 */
.custom-loading .el-loading-spinner .circular>circle {
    display: none;
}

.custom-loading .el-loading-spinner .circular {
    width: 80px !important;
    height: 80px !important;
    background: url('./assets/loading.gif') no-repeat center center;
    background-size: contain;
    animation: none;
}

html {
  --pending-bg-color: #f4f2e4;
  --active-bg-color: #d4e5ce;
}

html.dark {
    --pending-bg-color: rgb(41, 34.2, 24);
    --active-bg-color: rgb(28.3, 37.4, 23.8);
}
</style>