<template>
    <el-select-v2 v-model="selectedItem" :options="itemShowList" :props="selectProps" :placeholder="placeholder"
        :loading="loading" :item-height="56" filterable  :remote-method="filterMethod"
        @visible-change="handleVisibleChange" popper-class="item-select-popper">
        <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <el-button size="small" @click="getAllSilempleItems" :loading="headerLoading">刷新</el-button>
                <el-text size="small">最近更新: {{ lastUpdate }}</el-text>
            </div>
        </template>

        <template #default="{ item }">
            <div class="item-card-container" @click="handleCpuSelected(item)">
                <el-image :src="item.icon || ''" class="component-image item-image" :alt="item.title" lazy>
                    <template #placeholder>
                        <el-skeleton :loading="true" animated class="component-image">
                            <template #template>
                                <el-skeleton-item variant="image" style="width: 36px; height: 36px" />
                            </template>
                        </el-skeleton>
                    </template>
                    <template #error>
                        <el-icon size="24" class="unknow-icon">
                            <QuestionFilled />
                        </el-icon>
                    </template>
                </el-image>
                <div style="width: calc(100% - 44px);">
                    <p class="words">{{ item.title }}</p>
                    <p class="words">{{ item.name }}{{ item.damage == null ? '' : `:${item.damage}` }}</p>
                </div>
            </div>
        </template>
        <template v-if="footer" #footer>
            <el-text size="small">{{ footer }}</el-text>
        </template>
    </el-select-v2>
</template>

<script>
import itemUtil from "@/utils/items";
import ItemCard from "@/components/ItemCard.vue";
import { fetchStatusOnce, fetchStatus, addTask } from '@/utils/task'

export default {
    components: {
        ItemCard,
    },
    props: {
        options: {
            type: Array,
            required: false,
        },
        type: {  // 传入的值为 'all'、'items' 或 'fluids'，默认为 'all'
            type: String,
            required: false,
            default: 'all',
        },
        craft: {
            type: Boolean,
            required: false,
            default: false,
        },
        footer: {
            type: String,
            required: false,
        },
    },
    data() {
        return {
            itemList: [],
            itemShowList: [],
            itemOptions: [],
            selectProps: {
                label: 'title',
                value: 'title',
            },
            placeholder: '在此输入搜索并选择物品',
            selectedItem: '',
            headerLoading: false,
            loading: true,
            firstLoad: true,
            lastUpdate: '未知',
        };
    },
    watch: {
        options: {
            immediate: true,
            handler(newOptions) {
                if (newOptions) {
                    this.itemList = newOptions;
                    this.handleVisibleChange(true);
                }
            },
        },
    },
    mounted() {
        this.fetchItems();
    },
    methods: {
        handleCpuSelected(item) {
            this.$emit('handleItemSelected', item);
        },
        getAllSilempleItems() {
            this.headerLoading = true;
            addTask("getAllSilempleItems", null, () => {
                fetchStatus("getAllSilempleItems", null, null, this.handleTaskComplete, 1000);
            })
        },
        fetchItems() {
            if (this.firstLoad && (!this.options || this.options.length === 0)) {
                fetchStatusOnce("getAllSilempleItems", this.handleTaskComplete);
            }
        },
        handleTaskComplete(data) {
            this.headerLoading = false;
            this.loading = false;
            if (data.result) {
                let itemList = data.result;
                this.lastUpdate = data.completed_time.replace('T', ' ').replace('Z', ' ').split('.')[0];

                // 遍历每个物品，添加 icon 和 title 属性
                itemList.forEach(item => {
                    let item_ = itemUtil.getItem(item)
                    item.icon = itemUtil.isFluid(item) ? itemUtil.getFluidIcon(item) : itemUtil.getItemIcon(item_);
                    item.title = itemUtil.getName(item_, item, item) || item.label;
                });
                if (!this.options) {
                    this.itemList = itemList;
                    this.handleVisibleChange(true);
                }
                if (!this.firstLoad) {
                    this.$message.success(`获取物品列表成功!`);
                }
                this.$emit('handleLoadItemList', itemList);
            } else {
                this.$message.warning(`返回数据为空!`);
            }
            this.firstLoad = false;
        },
        filterMethod(query) {
            if (query === '') {
                this.itemShowList = this.itemOptions;
            } else {
                this.itemShowList = this.itemOptions.filter(item => item.title.toLowerCase().includes(query.toLowerCase()));
            }
        },
        handleVisibleChange(visible) {
            if (visible) {
                if (this.options && this.options.length > 0) {
                    this.itemList = this.options;
                }
                if (this.craft) {
                    this.itemOptions = this.itemList.filter(item => item.isCraftable);
                } else {
                    this.itemOptions = this.itemList;
                }
                if (this.type === 'items') {
                    this.itemShowList = this.itemOptions.filter(item => !itemUtil.isFluid(item));
                } else if (this.type === 'fluids') {
                    this.itemShowList = this.itemOptions.filter(item => itemUtil.isFluid(item));
                } else {
                    this.itemShowList = this.itemOptions;
                }
            }
        },
    }
};
</script>

<style>
.item-select-popper .el-select-dropdown__item {
    padding: 0;
}
</style>

<style scoped>
.item-card-container {
    display: flex;
    align-items: center;
    padding: 4px 0;
    cursor: pointer;
    padding: 0 32px 0 20px;
}

.item-image {
    width: 36px;
    height: 36px;
    margin-right: 8px;
}

.words {
    line-height: 24px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
}

.component-image {
    margin: auto 0;
    width: 36px;
    height: 36px;
    margin-right: 6px;
}

.unknow-icon {
    /* 居中 */
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);

}
</style>
