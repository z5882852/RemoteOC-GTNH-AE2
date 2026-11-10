local requested = {}
local fluidQueries = 0
local dropName = "ae2fc:fluid_drop"
local recipes
local cpus = {}

local function matches(stack, filter)
    for key, value in pairs(filter or {}) do
        if stack[key] ~= value then return false end
    end
    return true
end

local function status()
    return {
        hasFailed = function() return false end,
        isComputing = function() return false end,
        isDone = function() return true end,
        isCanceled = function() return false end,
    }
end

local function craftable(stack)
    return {
        getStack = function() return stack end,
        request = function(amount, prioritizePower, cpuName)
            requested.stack = stack
            requested.amount = amount
            requested.prioritizePower = prioritizePower
            requested.cpuName = cpuName
            return status()
        end,
    }
end

recipes = {
    craftable({name = "minecraft:stone", label = "Stone", damage = 0, size = 0}),
    craftable({name = "water", label = "Water", amount = 0, size = 0}),
    craftable({name = dropName, label = "Water Drop", damage = 0, size = 0}),
    craftable({name = dropName, label = "Lava Drop", damage = 0, size = 0}),
}

local me = {
    getItemsInNetwork = function(filter)
        local stack = {name = "minecraft:stone", label = "Stone", damage = 0, size = 64, isCraftable = true}
        return matches(stack, filter) and {stack} or {}
    end,
    getFluidsInNetwork = function()
        fluidQueries = fluidQueries + 1
        return {{name = "water", label = "Water", amount = 1000, size = 1000, isCraftable = true}}
    end,
    getCraftable = function(details, stackType)
        requested.details = details
        requested.stackType = stackType
        if stackType == "fluid" then
            return craftable({name = details.name, label = "Water", amount = 0, size = 0})
        end
        -- Like the typed parser, ignore label and select the first matching variant.
        if details.name == dropName then return recipes[3] end
        return craftable({name = details.name, label = "Stone", damage = details.damage, size = 0})
    end,
    getCraftables = function(filter)
        local result = {}
        for _, recipe in ipairs(recipes) do
            if matches(recipe.getStack(), filter) then table.insert(result, recipe) end
        end
        return result
    end,
    getCpus = function() return cpus end,
}

package.preload.component = function()
    return {
        proxy = function() return me end,
        isAvailable = function() return false end,
    }
end
package.preload.env = function() return {aeAddress = "test"} end
package.preload["lib.base64"] = function() return {encode = function(value) return "base64:" .. value end} end

dofile("client/plugins/ae.lua")

local all = ae.getAllItems().data
assert(#all == 2, "items and native fluids should be returned together")
assert(all[1].stackType == "item")
assert(all[2].stackType == "fluid")

local simple = ae.getAllSilempleItems().data
assert(#simple == 2)
assert(simple[2].name == "water" and simple[2].stackType == "fluid")

for _, query in ipairs({ae.getAllItems, ae.getAllSilempleItems}) do
    local before = fluidQueries
    local filtered = query({name = "minecraft:stone"}).data
    assert(#filtered == 1 and filtered[1].stackType == "item")
    assert(#query({name = "missing:item"}).data == 0)
    assert(#query({}).data == 1, "an explicit item filter should return only items")
    assert(fluidQueries == before, "filtered item queries must not fetch native fluids")
end

local itemResult = ae.requestItem("minecraft:stone", 0, 12)
assert(itemResult.message == "success")
assert(requested.stackType == "item" and requested.details.damage == 0)
assert(itemResult.data.stack.stackType == "item")

local dropResult = ae.requestItem(dropName, 0, 500, nil, "Lava Drop")
assert(dropResult.message == "success")
assert(requested.stack.label == "Lava Drop" and requested.amount == 500)
assert(dropResult.data.stack.stackType == "item")
local lastRequested = requested.stack
assert(ae.requestItem(dropName, 0, 500, nil, "Missing Drop").message == "没有找到指定的合成配方")
assert(ae.requestItem(dropName, 1, 500, nil, "Lava Drop").message == "没有找到指定的合成配方")
assert(ae.requestItem("missing:item", 0, 500, nil, "Lava Drop").message == "没有找到指定的合成配方")
assert(requested.stack == lastRequested, "unmatched labels must not request another variant")

cpus = {{name = "Main CPU", busy = true}}
assert(ae.requestItem(dropName, 0, 500, "Main CPU", "Lava Drop").message == "CPU 正忙")
assert(requested.stack == lastRequested)
cpus[1].busy = false
assert(ae.requestItem(dropName, 0, 500, "Main CPU", "Lava Drop").message == "success")
assert(requested.cpuName == "Main CPU" and requested.stack.label == "Lava Drop")
cpus = {}

local fluidResult = ae.requestFluid("water", 4000, "Main CPU")
assert(fluidResult.message == "CPU不存在", "named CPU validation should still be enforced")

local fluidAutoResult = ae.requestFluid("water", 4000)
assert(fluidAutoResult.message == "success")
assert(requested.stackType == "fluid" and requested.amount == 4000)
assert(fluidAutoResult.data.stack.stackType == "fluid")

local craftables = ae.getAllCraftables().data
assert(#craftables == 4)
assert(craftables[1].stackType == "item")
assert(craftables[2].stackType == "fluid")

print("test_ae.lua: ok")
