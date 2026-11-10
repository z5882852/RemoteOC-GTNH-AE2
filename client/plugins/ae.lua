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

local ITEM_STACK = "item"
local FLUID_STACK = "fluid"

local function inferStackType(stack)
    if stack and stack.stackType then return stack.stackType end
    if stack and stack.damage ~= nil then return ITEM_STACK end
    return FLUID_STACK
end

local function tagStack(stack, stackType)
    if stack ~= nil then
        stack.stackType = stackType or inferStackType(stack)
    end
    return stack
end

local function parseStacks(items, stackType)
    if items == nil then return nil end
    local data = {}
    for i, item in pairs(items) do
        tagStack(item, stackType)
        if item.hasTag and item.tag ~= nil then
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

local function simpleStackInfo(item, stackType)
    if item == nil then return nil end
    return {
        name = item.name,
        label = item.label,
        damage = item.damage,
        size = item.size,
        amount = item.amount,
        isCraftable = item.isCraftable,
        stackType = stackType or inferStackType(item)
    }
end

local function simpleItemsInfo(items)
    if items == nil then return end
    for i, item in pairs(items) do
        items[i] = simpleStackInfo(item)
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
            table.insert(newOne, simpleStackInfo(item))
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
        finalOutput = simpleStackInfo(sub.finalOutput()),
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

local function requestStack(stackType, details, amount, cpuName)
    local craftable
    if stackType ~= ITEM_STACK or not details.label then
        craftable = me.getCraftable(details, stackType)
    end
    if stackType == ITEM_STACK and not craftable then
        -- Filtered lookup preserves labels and finds NBT outputs without a tag in details.
        local craftables = me.getCraftables(details)
        craftable = craftables and craftables[1]
    end

    if not craftable then
        return { message = "没有找到指定的合成配方" }
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
        stack = tagStack(craftable.getStack(), stackType),
        failed = result.hasFailed() or false,
        computing = result.isComputing() or false,
        done = { result = false, why = nil },
        canceled = { result = false, why = nil }
    }

    res.done.result, res.done.why = result.isDone()
    res.canceled.result, res.canceled.why = result.isCanceled()

    return { message = "success", data = res }
end

function ae.requestItem(name, damage, amount, cpuName, label)
    -- GTNH 2.9 / OpenComputers 1.12 使用带类型的 AE2 合成 API。
    if not name or damage == nil then
        return { message = "物品信息为空" }
    end

    local details = { name = name, damage = damage }
    if label then details.label = label end
    return requestStack(ITEM_STACK, details, amount, cpuName)
end

function ae.requestFluid(name, amount, cpuName)
    if not name then
        return { message = "流体信息为空" }
    end
    return requestStack(FLUID_STACK, { name = name }, amount, cpuName)
end

function ae.getAllSilempleItems(filter)
    -- 保留旧函数名，并在 2.9 中同时返回物品和原生 AE2 流体。
    local items = me.getItemsInNetwork(filter)
    local newOne = {}
    for i, item in pairs(items) do
        if item.size ~= nil or item.amount ~= nil then
            table.insert(newOne, simpleStackInfo(item, ITEM_STACK))
        end
        if i % 50 == 0 then
            os.sleep(0)
        end
    end
    -- An item filter must not include unrelated native fluids.
    if filter ~= nil then
        return { message = "success", data = newOne }
    end
    local fluids = me.getFluidsInNetwork()
    for i, fluid in pairs(fluids or {}) do
        if fluid.size ~= nil or fluid.amount ~= nil then
            table.insert(newOne, simpleStackInfo(fluid, FLUID_STACK))
        end
        if i % 50 == 0 then
            os.sleep(0)
        end
    end
    return { message = "success", data = newOne}
end

function ae.getAllItems(filter)
    -- 2.9 将流体提升为 AE2 原生存储类型，因此一起返回供网页统一展示。
    local items = me.getItemsInNetwork(filter)
    local data = parseStacks(items, ITEM_STACK) or {}
    if filter ~= nil then
        return { message = "success", data = data }
    end
    local fluids = parseStacks(me.getFluidsInNetwork(), FLUID_STACK) or {}
    for _, fluid in pairs(fluids) do
        table.insert(data, fluid)
    end
    return { message = "success", data = data }
end

function ae.getAllFluids()
    -- 获取所有流体信息
    local fluids = me.getFluidsInNetwork()
    return { message = "success", data = parseStacks(fluids, FLUID_STACK) }
end

function ae.getAllEssentia()
    -- 获取所有源质信息
    local essentia = me.getEssentiaInNetwork()
    return { message = "success", data = parseStacks(essentia) }
end

function ae.getAllCraftables()
    -- 获取所有可合成的物品

    local craftables = me.getCraftables()
    if not craftables then return { message = "not craftables" } end

    local result = {}
    for i, craftable in pairs(craftables) do
        local stack = craftable.getStack()
        if stack then
            local stackType = inferStackType(stack)
            local entry = simpleStackInfo(stack, stackType)
            if stack.hasTag and stack.tag ~= nil then
                entry.hasTag = true
                entry.tag = base64.encode(stack.tag)
            end
            table.insert(result, entry)
        end
        if i % 50 == 0 then
            os.sleep(0)
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
