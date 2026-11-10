<template>
    <el-container style="height: 100%;" v-loading="loading">
        <el-header v-loading="headerLoading" :element-loading-text="headerLoadingText" class="control-header-item">
            <el-card class="control-card" shadow="hover">
                <div v-if="isMobile" class="control-bar">
                    <div class="segmented-container">
                        <el-segmented v-model="showCraft" :options="['全部', '可下单']" size="default" />
                        <el-segmented class="liquid-segmented" v-model="showLiquid" :options="['全部', '物品', '液体']"
                            size="default" />
                    </div>
                    <div class="search-container">
                        <el-input v-model="searchText" class="item-search" placeholder="请输入信息以查询">
                            <template #suffix>
                                <el-icon class="el-input__icon">
                                    <search />
                                </el-icon>
                            </template>
                            <template #prepend>
                                <el-select v-model="searchType" placeholder="查询类型" style="width: 75px">
                                    <el-option label="物品名" value="title" />
                                    <el-option label="标签名" value="label" />
                                    <el-option label="name" value="name" />
                                </el-select>
                            </template>
                        </el-input>
                        <el-button type="primary" @click="getItems">获取物品信息</el-button>
                    </div>
                </div>
                <div v-else class="control-bar">
                    <div style="display: flex;">
                        <el-segmented v-model="showCraft" :options="['全部', '可下单']" size="default" />
                        <el-segmented style="margin: 0 16px;" v-model="showLiquid" :options="['全部', '物品', '液体']"
                            size="default" />
                        <el-input v-model="searchText" class="item-search" placeholder="请输入信息以查询">
                            <template #suffix>
                                <el-icon class="el-input__icon">
                                    <search />
                                </el-icon>
                            </template>
                            <template #prepend>
                                <el-select v-model="searchType" placeholder="查询类型" style="width: 100px">
                                    <el-option label="物品名" value="title" />
                                    <el-option label="标签名" value="label" />
                                    <el-option label="name" value="name" />
                                </el-select>
                            </template>
                        </el-input>
                    </div>

                    <el-button type="primary" @click="getItems">获取物品信息</el-button>
                </div>
            </el-card>
        </el-header>
        <el-main style="width: 100%; overflow: hidden;">
            <el-card class="box-card">
                <div class="card-container">
                    <el-card v-for="(item, index) in showItems" :key="index" class="item-card" style="height: 116px;"
                        shadow="hover">
                        <div class="image-wrapper">
                            <el-image :src="item.image || ''" class="component-image" :alt="item.title" lazy>
                                <template #placeholder>
                                    <el-skeleton :loading="true" animated class="component-image">
                                        <template #template>
                                            <el-skeleton-item variant="image" style="width: 48px; height: 48px" />
                                        </template>
                                    </el-skeleton>
                                </template>
                                <template #error>
                                    <el-icon size="40" class="unknow-icon">
                                        <QuestionFilled />
                                    </el-icon>
                                </template>
                            </el-image>

                            <div class="item-info">
                                <div class="ellipsis" :title="item.title" v-html="parseLineColorCode(item.title)"></div>
                                <div class="words" :title="item.label" v-html="parseLineColorCode(item.label)"></div>
                                <div class="words">{{ item.data.stackType === 'fluid' ? '数量 (mB):' : '数量:' }}
                                    <NumberFormat :number="item.size" />
                                </div>
                                <div v-if="item.isCraftable"><el-tag size="small" type="success">可合成</el-tag></div>
                                <el-tooltip placement="top" effect="dark">
                                    <template #content>
                                        <div style="font-size: 12px; color: #aaa;">Tooltip</div>
                                        <div>{{ item.title }}</div>
                                        <div v-if="item.size > 0">存储物品: <span @click="copyToClipboard(item.size)">{{
                                            item.size }}</span></div>
                                        <div class="words copy-container" v-for="(info, index) in item.tooltip"
                                            :key="index" @click="copyToClipboard(info)">
                                            {{ info }}
                                        </div>
                                        <div class="words copy-container"
                                            @click="copyToClipboard(item.data.damage == null ? item.data.name : `${item.data.name}:${item.data.damage}`)">{{
                                                item.data.name }}{{ item.data.damage == null ? '' : `:${item.data.damage}` }}</div>
                                        <div style="font-size: 12px; color: #aaa;">其他属性</div>
                                        <div v-for="(value, key, index) in item.data" :key="index"
                                            :title="typeof value === 'object' ? JSON.stringify(value) : value"
                                            @click="copyToClipboard(value)" class="words copy-container">
                                            {{ key }}: {{ value }}
                                        </div>
                                        <div style="font-size: 10px; color: #aaa;">点击复制属性值</div>
                                    </template>
                                    <el-icon size="large" class="info-icon">
                                        <InfoFilled />
                                    </el-icon>
                                </el-tooltip>
                                <el-tooltip placement="top" effect="dark" v-if="item.isCraftable">
                                    <template #content>
                                        下单制作
                                    </template>
                                    <el-icon size="large" class="craft-icon"
                                        @click="openCraftDialog(item)">
                                        <GoodsFilled />
                                    </el-icon>
                                </el-tooltip>
                            </div>
                        </div>
                    </el-card>
                </div>
                <div class="pagination-container">
                    <div class="pagination-info">
                        <span style="display: flex;">最近更新时间: {{ lastUpdate }}</span>
                        <span v-if="isMobile" style="display: flex;">共 {{ page.total }} 条</span>
                    </div>
                    <el-pagination style="display: flex;" v-model:current-page="page.current"
                        v-model:page-size="page.size" :pager-count="isMobile ? 5 : 7" :page-sizes="[50, 100, 200, 400]"
                        size="small"
                        :layout="isMobile ? 'sizes, prev, pager, next' : 'total, sizes, prev, pager, next, jumper'"
                        :total="page.total" @size-change="handlePaginationChange"
                        @current-change="handlePaginationChange" />
                </div>
            </el-card>
        </el-main>
        <el-dialog v-model="showCraftDialog" :title="craftDialogTitle" class="craft-dialog" align-center>
            <el-form :model="craft">
                <el-form-item label="下单数量">
                    <el-input v-model="craft.amount" type="number" placeholder="请输入下单数量" />
                </el-form-item>
                <el-form-item label="选择CPU">
                    <div style="width: 100%; display: flex; justify-content: space-between;">
                        <el-tooltip>
                            <template #content>
                                {{ craft.cpuOptions.length === 0 ? '请先获取CPU列表' : '请选择CPU' }}
                            </template>
                            <el-select-v2 ref="select" :disabled="craft.cpuOptions.length === 0"
                                v-model="craft.selectCpu" :options="craft.cpuOptions" placeholder="自动分配"
                                style="width: 280px">
                                <template #footer>
                                    <span>仅能选择已命名且空闲的CPU</span>
                                </template>
                            </el-select-v2>
                        </el-tooltip>
                        <el-button type="primary" @click="getCpuList" :loading="craft.cpuBthLoading">获取CPU</el-button>
                    </div>
                </el-form-item>
            </el-form>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="showCraftDialog = false">取消</el-button>
                    <el-button type="primary" @click="craftItem" :loading="craft.btnLoading">
                        确认
                    </el-button>
                </div>
            </template>
        </el-dialog>
    </el-container>
</template>

<script>
import { inject } from 'vue';
import bus from 'vue3-eventbus';
import { fetchStatus, addTask, createCraftTask, createPollingController } from '@/utils/task';
import itemUtil from "@/utils/items";
import nbt from "@/utils/nbt";
import Setting from '@/utils/setting';
import { parseLineColorCode } from '@/utils/utils';
import NumberFormat from '@/components/NumberFormat.vue';

export default {
    name: 'Items',
    components: {
        NumberFormat,
    },
    data() {
        return {
            loading: true,
            headerLoading: false,
            headerLoadingText: "",
            lastUpdate: "",
            showCraft: "全部",
            showLiquid: "全部",
            searchType: "title",
            searchText: "",
            items: [],
            showItems: [],
            page: {
                total: 0,
                size: parseInt(localStorage.getItem('pageSize')) || 50,
                current: 1,
            },
            pollingController: null,
            showCraftDialog: false,
            craftDialogTitle: "下单",
            craft: {
                name: null,
                damage: null,
                stackType: "item",
                amount: 1,
                label: null,
                btnLoading: false,
                cpuBthLoading: false,
                selectCpu: null,
                cpuOptions: [],
            }
        };
    },
    setup() {
        const isMobile = inject('isMobile');
        return {
            isMobile,
            parseLineColorCode,
        };
    },
    mounted() {
        this.startPolling("getAllItems");
    },
    methods: {
        handlePaginationChange() {
            localStorage.setItem('pageSize', this.page.size);
            this.updateShowItems();
            // const start = (this.page.current - 1) * this.page.size;
            // const end = start + this.page.size;
            // this.showItems = this.items.slice(start, end);
        },
        startPolling(taskId) {
            this.pollingController = createPollingController();
            fetchStatus(taskId, this.handleTaskResult, this.handleTaskUploading, this.handleTaskComplete, 1000, this.pollingController);
        },
        stopPolling() {
            if (this.pollingController) {
                this.pollingController.stop();
                console.log('Polling stopped.');
            }
        },
        handleTaskResult(data) {
            // console.log('Task result:', data);
            this.loading = false;

            if (data.result) {
                try {
                    let result = data.result;
                    this.lastUpdate = data.completed_time ? data.completed_time.split(".")[0].replace("T", " ") : '未知';
                    let isShowLiquidImage = Setting.get("showFluid");
                    let items = result;
                    let new_items = []
                    for (let item of items) {
                        let { image, title, size, isCraftable, label, ...data } = item;
                        if (data.hasTag && nbt) {
                            nbt.parse(nbt.base64ToUint8Array(data.tag), (e, unzipNbt) => {
                                if (e) {
                                    console.error(e)
                                } else {
                                    data.tag = JSON.stringify(unzipNbt)
                                }
                            })
                        }
                        let item_ = itemUtil.getItem(item)
                        if (isShowLiquidImage && itemUtil.isFluid(data)) {
                            image = itemUtil.getFluidIcon(data)
                        } else {
                            image = itemUtil.getItemIcon(item_)
                        }
                        let new_item = {
                            image: image,
                            title: itemUtil.getName(item_, item, data) || item.label,
                            label: item.label,
                            size: item.size,
                            tooltip: item_ && item_.tooltip || [],
                            isCraftable: item.isCraftable,
                            data: data,
                        }
                        // 伪合成处理
                        if (new_item.data && new_item.data.name === 'minecraft:paper' && new_item.label !== 'Paper' && new_item.title === '纸') {
                            new_item.title = `${new_item.title}(${new_item.label})`
                        }
                        new_items.push(new_item);
                    }
                    this.items = new_items;
                    this.handlePaginationChange();
                } catch (e) {
                    console.error(e, data);
                    this.$message.warning(e);
                }
            } else {
                this.$message.warning(`返回数据为空!`);
            }
        },
        handleTaskUploading(data) {
            if (this.headerLoadingText === "客户端正在上传数据，请稍后... Task id: getAllItems") {
                return
            }
            this.headerLoading = false;
            this.$nextTick(() => {
                this.headerLoadingText = "客户端正在上传数据，请稍后... Task id: getAllItems";
                this.headerLoading = true;
            });
        },
        handleTaskComplete() {
            this.loading = false;
            this.headerLoading = false;
        },
        getItems() {
            this.headerLoading = true;
            this.headerLoadingText = "请求已发送，等待客户端响应... Task id: getAllItems";
            addTask("getAllItems", null, () => {
                this.startPolling("getAllItems")
            })
        },
        copyToClipboard(text) {
            if (typeof text === 'object') {
                text = JSON.stringify(text);
            }
            try {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed'; // 避免滚动页面
                textarea.style.opacity = '0'; // 隐藏
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                const success = document.execCommand('copy');
                document.body.removeChild(textarea);

                if (success) {
                    this.$message({
                        message: '复制成功!',
                        type: 'success'
                    });
                } else {
                    console.error('execCommand复制失败');
                    throw new Error('execCommand复制失败');
                }
            } catch (err) {
                console.error('复制失败:', err);
                this.$message({
                    message: '复制失败',
                    type: 'error'
                });
            }
        },
        openCraftDialog(item) {
            this.craft.name = item.data.name;
            this.craft.damage = item.data.damage;
            this.craft.stackType = item.data.stackType || "item";
            this.craft.amount = 1;
            this.craft.label = item.label;
            this.craftDialogTitle = "下单-" + item.title;
            this.showCraftDialog = true;
        },
        craftItem() {
            let name = this.craft.name;
            let damage = this.craft.damage;
            let amount = this.craft.amount;
            let cpuName = this.craft.selectCpu;
            let label = name === "ae2fc:fluid_drop" ? this.craft.label : null;
            let stackType = this.craft.stackType;
            this.craft.btnLoading = true;
            console.log("craft：", stackType, name, damage, amount, cpuName, label)
            createCraftTask(stackType, name, damage, amount, cpuName, label, (data) => {
                this.craft.btnLoading = false;
                this.showCraftDialog = false;
            }, (cpuResult) => {
                console.log(cpuResult)
                bus.emit('refreshCpuList', cpuResult);
            });
        },
        updateShowItems() {
            let filteredItems = this.items;
            if (this.showCraft === "可下单") {
                filteredItems = filteredItems.filter(item => item.isCraftable);
            }
            if (this.showLiquid === "物品") {
                filteredItems = filteredItems.filter(item => !itemUtil.isFluid(item.data));
            } else if (this.showLiquid === "液体") {
                filteredItems = filteredItems.filter(item => itemUtil.isFluid(item.data));
            }

            if (this.searchText) {
                filteredItems = filteredItems.filter(item => {
                    if (this.searchType === "label") {
                        return item.label && item.label.toLowerCase().includes(this.searchText.toLowerCase());
                    } else if (this.searchType === "name") {
                        return item.data.name && item.data.name.toLowerCase().includes(this.searchText.toLowerCase());
                    } else {
                        return item.title && item.title.toLowerCase().includes(this.searchText.toLowerCase());
                    }
                });
            }
            this.page.total = filteredItems.length;

            const start = (this.page.current - 1) * this.page.size;
            const end = start + this.page.size;
            this.showItems = filteredItems.slice(start, end);
        },
        getCpuList() {
            this.craft.cpuBthLoading = true;
            addTask("getCpuList", null, () => {
                fetchStatus("getCpuList", null, null, (data) => {
                    this.craft.cpuBthLoading = false;
                    if (data && data.result && data.result[0]) {
                        let cpuInfo = JSON.parse(data.result[0]);
                        if (cpuInfo.message && cpuInfo.message === "success") {
                            let cpuList = cpuInfo.data;
                            console.log(cpuList)
                            cpuList = cpuList.filter(cpu => !cpu.busy && cpu.name !== "");
                            this.craft.cpuOptions = cpuList.map(item => ({
                                value: item.name,
                                label: item.name,
                            }))
                            this.craft.cpuOptions.push({
                                label: "自动分配",
                                value: null,
                            })
                            this.$message.success(`获取CPU列表成功`)
                        } else {
                            this.$message.error(`获取CPU列表失败: ${cpuInfo.message}`)
                        }
                    } else {
                        this.$message.error("获取CPU列表失败")
                    }
                });
            })
        }
    },
    watch: {
        items() {
            this.updateShowItems();
        },
        showCraft() {
            this.updateShowItems();
        },
        showLiquid() {
            this.updateShowItems();
        },
        searchType() {
            this.updateShowItems();
        },
        searchText() {
            this.updateShowItems();
        }
    }
};
</script>

<style>
.box-card .el-card__body {
    padding: 16px;
}



.item-card .el-card__body {
    height: 100%;
    padding: 8px;
}

@media screen and (min-width: 768px) {
    .control-header-item {
        width: 100%;
        margin-top: 10px;
    }

    .item-card {
        flex: 0 0 300px;
    }

    .craft-dialog {
        min-width: 250px;
        max-width: 400px;
    }
}

/* 移动端适配 control-card 高100px */
@media screen and (max-width: 768px) {
    .control-header-item {
        width: 100%;
        margin-top: 10px;
        height: 120px !important;
    }

    .item-card {
        flex: 0 0 calc(100% - 16px);
    }

    .craft-dialog {
        width: 80% !important;
        max-width: 400px;
    }
}

.control-header-item .el-card__body {
    height: 100%;
    padding: 8px;
}

.control-header-item .el-loading-spinner .circular {
    height: 24px;
    width: 24px;
}

.search-container .el-select__wrapper {
    padding-right: 5px;
    padding-left: 5px;
}

.el-popper {
    max-width: 400px;
}

.box-card {
    height: 100%;
}

.box-card .el-card__body {
    height: 100%;
}

.el-pagination {
    justify-content: flex-end;
}
</style>

<style scoped>
.el-container {
    height: 100%;
}

@media screen and (min-width: 768px) {
    .control-card {
        padding: 10px;
        margin-bottom: 10px;
    }

    .control-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .liquid-segmented {
        margin: 0 16px;
    }

    .item-search {
        width: 30vw;
        max-width: 400px;
        margin-left: 10px;
    }

    .card-container {
        overflow-y: auto;
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        justify-content: flex-start;
        height: calc(100% - 14px - 36px);
    }

    .pagination-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: auto 0;
        height: 36px;
        padding-right: 10px;
    }
}

/* 移动端适配 control-card 高100px */
@media screen and (max-width: 768px) {
    .control-card {
        height: 100px;
        padding: 10px;
        margin-bottom: 10px;
    }

    .control-bar {
        height: calc(100% - 20px);
        display: flex;
        justify-content: space-between;
        flex-direction: column;
        align-items: center;
    }

    .item-search {
        width: 50vw;
        max-width: 400px;
    }

    .card-container {
        overflow-y: auto;
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        justify-content: flex-start;
        height: calc(100% - 14px - 50px);
    }

    .pagination-info {
        display: flex;
        justify-content: space-between;
        width: 100%;
    }

    .pagination-container {
        display: flex;
        align-items: flex-start;
        margin: auto 0;
        height: 50px;
        justify-content: space-evenly;
        flex-direction: column;
    }

}

.segmented-container {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.search-container {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.ellipsis {
    font-size: 20px;
    line-height: 25px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: calc(100% - 20px);
}

.words {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
}

.copy-container {
    cursor: pointer;
}

.image-wrapper {
    display: flex;
    height: calc(100% - 32px);
}

.item-card {
    position: relative;
    margin-bottom: 8px;
}

.component-image {
    margin: auto 0;
    width: 48px;
    height: 48px;
    margin-right: 12px;
}

.item-info {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    /* 让信息块顶部对齐 */
    width: calc(100% - 60px);
    line-height: 1.5;
}

.info-icon {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 20px;
    cursor: pointer;
}

.unknow-icon {
    /* 居中 */
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);

}

.craft-icon {
    position: absolute;
    top: 28px;
    right: 8px;
    font-size: 20px;
    cursor: pointer;
}
</style>
