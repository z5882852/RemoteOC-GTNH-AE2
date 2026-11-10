import axios from "axios";
import Setting from '@/utils/setting';


const itemUtil = {
    items: null,
    fluids: null,
    version: "2.9.0-beta-3",
    // The bundled lookup database is only used for translated names and icons.
    // Unknown 2.9 entries fall back to the live label returned by OpenComputers.
    assetVersion: "2.8.0",

    getAssetVersionKey() {
        return this.assetVersion.replace(/\./g, "");
    },

    loadWithProgress(url, progressCallback) {
        axios.get(url, {
            onDownloadProgress: (event) => {
                if (event.lengthComputable) {
                    const percentCompleted = Math.round(
                        (event.loaded / event.total) * 100
                    );
                    progressCallback(percentCompleted);
                }
            },
        }).then((res) => {

            progressCallback(100);
        });
    },

    loadItems(progressCallback) {
        if (!this.items) {
            let url = (Setting.get("resourceUrl")) + `/items_GTNH${this.getAssetVersionKey()}.json`;
            if (Setting.get("useGzip")) {
                url += ".gz";
            }
            axios.get(url, {
                onDownloadProgress: (event) => {
                    if (event.lengthComputable) {
                        const percentCompleted = Math.round((event.loaded / event.total) * 100);
                        if(progressCallback) progressCallback(percentCompleted);  // 更新进度
                    }
                },
            }).then((res) => {
                // 响应码判断
                if (res.status === 200) {
                    this.items = res.data;
                    if(progressCallback) progressCallback(100);
                } else {
                    console.error(`Error loading items: ${res.status}`);
                    if(progressCallback) progressCallback(-1);
                }
            }).catch((error) => {
                console.error("Error loading items:", error);
                if(progressCallback) progressCallback(-1);
            });
        } else {
            if(progressCallback) progressCallback(100);
        }
    },

    loadFluids(progressCallback) {
        if (!this.fluids) {
            let url = (Setting.get("resourceUrl")) + `/fluids_GTNH${this.getAssetVersionKey()}.json`;
            if (Setting.get("useGzip")) {
                url += ".gz";
            }
            axios.get(url, {
                onDownloadProgress: (event) => {
                    if (event.lengthComputable) {
                        const percentCompleted = Math.round((event.loaded / event.total) * 100);
                        if(progressCallback) progressCallback(percentCompleted);
                    }
                },
            }).then((res) => {
                // 响应码判断
                if (res.status === 200) {
                    this.fluids = res.data;
                    if(progressCallback) progressCallback(100);
                } else {
                    console.error(`Error loading fluids: ${res.status}`);
                    if(progressCallback) progressCallback(-1);
                }
            }).catch((error) => {
                console.error("Error loading fluids:", error);
                if(progressCallback) progressCallback(-1);
            });
        } else {
            if(progressCallback) progressCallback(100);
        }
    },

    isItem: (obj) => {
        return obj && obj["name"] && obj.stackType !== "fluid" && obj["damage"] !== null;
    },

    isFluid: (obj) => {
        return obj && (obj.stackType === "fluid" || obj.name === "ae2fc:fluid_drop");
    },

    getItem(obj) {
        if (this.isItem(obj)) {
            const items = this.items;
            let name = obj["name"];
            if (!items[name]) {
                name = name.replaceAll("|", "_");
                if (!items[name]) return null;
            }
            let damage = (obj["damage"] ? obj["damage"] : 0) + "";
            let item = items[name][damage];
            return item ? item : items[name]["0"];
        }
        return null;
    },

    getName(item, originItem, data) {
        if (originItem.stackType === "fluid") {
            const fluid = this.fluids && this.fluids[originItem.name];
            return fluid && fluid.zh ? fluid.zh : originItem.label;
        }
        if (item) {
            let name = item && item.zh ? item.zh : originItem.label;
            if (originItem.name === "ae2fc:fluid_drop") {
                if (data && data.tag) {
                    try {
                        let tag = JSON.parse(data.tag);
                        let fluidId = tag.value.Fluid.value;
                        let fluids = this.fluids;
                        name = fluids[fluidId].zh;
                    } catch (err) {
                        name = originItem.label.replace("drop of ", "");
                    }
                } else {
                    name = originItem.label.replace("drop of ", "");
                }
            }
            if (originItem.name === 'minecraft:paper' && originItem.label !== 'Paper' && name === '纸') {
                name = `${name} (${originItem.label})`;
            }
            return name;
        }
        return originItem.label;
    },

    getItemIcon: (item) => {
        if (item && item.img_path) {
            return "img/items/" + item.img_path;
        }
        return "img/default.png";
    },

    getFluidIcon: (data) => {
        if (data) {
            if (data.stackType === "fluid" && data.name) {
                return "img/fluids/" + data.name + ".png";
            }
            // Legacy AE2FC fluid drop.
            if (data.tag) {
                try {
                    let tag = JSON.parse(data.tag);
                    let fluidId = tag.value.Fluid.value;
                    return "img/fluids/" + fluidId + ".png";
                } catch (err) {
                    return "img/default.png";
                }
            }
        }
        return "img/default.png";
    },
};

export default itemUtil;
