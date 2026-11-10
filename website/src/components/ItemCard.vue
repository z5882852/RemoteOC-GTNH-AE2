<template>
    <div class="item-card-container">
        <el-image :src="item.image || ''" class="component-image item-image" :alt="item.title" lazy>
            <template #placeholder>
                <el-skeleton :loading="true" animated class="component-image">
                    <template #template>
                        <el-skeleton-item variant="image" style="width: 24px; height: 24px" />
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

<script>
import itemUtil from "@/utils/items";

export default {
    props: {
        item: {
            type: Object,
            required: true,
        },
    },
    watch: {
        item: {
            handler(newVal) {
                this.updateItem(newVal);
            },
            deep: true,
        },
    },
    methods: {
        updateItem(item) {
            const updatedItem = itemUtil.getItem(item);
            if (itemUtil.isFluid(item)) {
                item.image = itemUtil.getFluidIcon(item);
            } else {
                item.image = itemUtil.getItemIcon(updatedItem);
            }
            item.title = itemUtil.getName(updatedItem, item, item) || item.label;
        }
    },
    created() {
        this.updateItem(this.item);
    },
};
</script>

<style scoped>
.item-card-container {
    display: flex;
    align-items: center;
    padding: 4px 0;
    cursor: pointer;
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
