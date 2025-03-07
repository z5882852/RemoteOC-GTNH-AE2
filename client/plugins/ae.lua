local component = require("component")
local base64 = require("lib.base64")
local env = require("env")

local aeAddress = env.aeAddress

local me

if component.proxy(aeAddress) then
    me = component.proxy(aeAddress)
elseif component.isAvailable("me_controller") then
    me = component.me_controller
elseif component.isAvailable("me_interface") then
    me = component.me_interface
else
    error("未找到 AE 网络")
end

ae = {}


local function parseItem(items)
    if items == nil then return nil end
    local data = {}
    for i, item in pairs(items) do
        if item.hasTag then
            item.tag = base64.encode(item.tag)
        end
        table.insert(data, item)
        
        -- 每处理一定数量的项目后挂起一次，避免 "too long without yielding" 错误
        if i % 50 == 0 then
            os.sleep(0)
        end
    end
    return data
end

local function getSimpleInfo(cpu)
    return {
        cpu = {},
        busy = cpu.busy,
        coprocessors = cpu.coprocessors,
        storage = cpu.storage,
        name = cpu.name
    }
end

local function simpleItemInfo(item)
    if item == nil then return nil end
    return {
        name = item.name,
        label = item.label,
        damage = item.damage,
        size = item.size,
        isCraftable = item.isCraftable
    }
end

local function simpleItemsInfo(items)
    if items == nil then return end
    for i, item in pairs(items) do
        items[i] = simpleItemInfo(item)
        if i % 50 == 0 then
            os.sleep(0)
        end
    end
end

local function removeEmptyItem(items)
    if items == nil then return nil end

    local newOne = {}
    for i, item in pairs(items) do
        if item.size ~= nil and item.size ~= 0 or item.amount ~= nil and item.amount ~= 0 then
            table.insert(newOne, simpleItemInfo(item))
        end
        if i % 50 == 0 then
            os.sleep(0)
        end
    end
    return newOne
end

local function getDetailInfo(cpu)
    local sub = cpu.cpu
    local result = {
        activeItems = removeEmptyItem(sub.activeItems()),
        -- fix: 当itme存在tag时，编码错误
        finalOutput = simpleItemInfo(sub.finalOutput()),
        active = sub.isActive(),
        busy = sub.isBusy(),
        pendingItems = removeEmptyItem(sub.pendingItems()),
        storedItems = removeEmptyItem(sub.storedItems())
    }
    return result
end

function ae.getCpuInfoByName(cpuName)
    if not cpuName or cpuName == "" then
        return { message = "CPU 名称为空" }
    end

    local cpus = me.getCpus()
    if not cpus then
        return { message = "未找到 CPU" }
    end

    for _, cpu in pairs(cpus) do
        if cpu.name == cpuName then
            return { message = "success", data = getSimpleInfo(cpu) }
        end
    end

    return { message = "没有找到名称为 " .. cpuName .. " 的 CPU" }
end

function ae.getCpuList(detail)
    -- 获取所有CPU信息
    local cpus = me.getCpus()
    if cpus == nil then return { message = "no cpus" } end
    local result = {}
    for _, cpu in pairs(cpus) do
        local simple = getSimpleInfo(cpu)
        if detail then simple.cpu = getDetailInfo(cpu) end
        table.insert(result, simple)
    end
    return { message = "success", data = result}
end

function ae.getCpuDetail(cpuName)
    -- 获取指定CPU信息
    local cpus = me.getCpus()
    if cpus == nil then return nil end
    for _, cpu in pairs(cpus) do
        if cpu.name == cpuName then
            local result = getSimpleInfo(cpu)
            result.cpu = getDetailInfo(cpu)
            return result
        end
    end
    return { message = "no cpus" }
end

function ae.requestItem(name, damage, amount, cpuName, label)
    -- 请求合成指定的物品
    -- 参数:
    -- name (string): 要合成物品的名称
    -- damage (int): 物品的损坏值
    -- amount (int, 可选): 要合成的物品数量，默认值为1
    -- cpuName (string, 可选): 用于执行任务的CPU名称，若为空则系统自动选择
    -- label (string, 可选): 物品的标签，用于区分不同的流体液滴
    if not name or not damage then
        return { message = "物品信息为空" }
    end

    local craftable
    if label then
        craftable = me.getCraftables({
            name = name,
            damage = damage,
            label = label
        })[1]
    else
        craftable = me.getCraftables({
            name = name,
            damage = damage
        })[1]
    end

    if not craftable then
        return { message = "没有找到指定的物品" }
    end

    amount = amount or 1


    local result
    if not cpuName or cpuName == "" then
        result = craftable.request(amount, true)
    else
        -- 检查CPU是否存在并且为空闲状态
        local cpuInfo = ae.getCpuInfoByName(cpuName)
        if cpuInfo.message == "success" then
            if cpuInfo.data.busy then
                return { message = "CPU 正忙" }
            else
                result = craftable.request(amount, nil, cpuName)
            end
        else
            return { message = "CPU不存在", data = cpuInfo }
        end
    end

    if not result then
        return { message = "合成物品失败" }
    end

    local res = {
        item = craftable.getItemStack(),
        failed = result.hasFailed() or false,
        computing = result.isComputing() or false,
        done = { result = false, why = nil },
        canceled = { result = false, why = nil }
    }

    res.done.result, res.done.why = result.isDone()
    res.canceled.result, res.canceled.why = result.isCanceled()

    return { message = "success", data = res }
end

function ae.getAllSilempleItems(filter)
    -- 获取所有物品简单信息
    local items = me.getItemsInNetwork(filter)
    local newOne = {}
    for i, item in pairs(items) do
        if item.size ~= nil or item.amount ~= nil then
            table.insert(newOne, simpleItemInfo(item))
        end
        if i % 50 == 0 then
            os.sleep(0)
        end
    end
    return { message = "success", data = newOne}
end

function ae.getAllItems(filter)
    -- 获取所有物品信息
    local items = me.getItemsInNetwork(filter)
    return { message = "success", data = parseItem(items) }
end

function ae.getAllCraftables()
    -- 获取所有可合成的物品

    local items = me.getItemsInNetwork()
    if not items then return { message = "not items" } end

    local result = {}
    for _, item in pairs(items) do
    if item.isCraftable then
        local entry = {
            name = item.name,
            label = item.label,
            size = item.size,
            damage = item.damage
        }
        
        if item.hasTag then
            entry.hasTag = true
            entry.tag = base64.encode(item.tag)
        end
        
        table.insert(result, entry)
        end
    end

    return { message = "success", data = result }
end

function ae.cancelCraftingByCpuName(cpuName)
    -- 根据 CPU 名称取消合成任务
    -- 参数:
    -- cpuName (string): 要取消合成任务的 CPU 名称, 如果为空则不执行任何操作

    if not cpuName or cpuName == "" then
        return { message = "CPU 名称为空，无法取消合成任务" }
    end

    local cpus = me.getCpus()
    if not cpus then
        return { message = "未找到任何 CPU" }
    end

    for _, cpu in pairs(cpus) do
        if cpu.name == cpuName then
            local currentCpu = cpu.cpu
            if currentCpu then
                currentCpu.cancel()
                return { message = "已取消 CPU: " .. cpuName .. " 的合成任务" }
            else
                return { message = "取消合成任务失败，CPU: " .. cpuName }
            end
        end
    end

    return { message = "没有找到名称为 " .. cpuName .. " 的 CPU" }
end
