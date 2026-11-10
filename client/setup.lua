local shell = require('shell')
local repo

local args = {...}
if #args >= 1 then
    repo = args[1]
else
    repo = "https://raw.githubusercontent.com/z5882852/RemoteOC-GTNH-AE2/main/client/"
end

local scripts = {
    'run.lua',
    'env.lua',
    'lib/logger.lua',
    'lib/json.lua',
    'lib/json2.lua',
    'lib/base64.lua',
    'src/executor.lua',
    'plugins/ae.lua',
}

print("installing...")
for i = 1, #scripts do
    local script_path = string.format('%s', scripts[i])
    shell.execute(string.format('rm -f %s', script_path))

    local script_dir = script_path:match("(.*/)")

    if script_dir then
        shell.execute(string.format('mkdir -p %s', script_dir))
    end

    shell.execute(string.format('wget -f %s%s %s', repo, scripts[i], script_path))
end
print("done.")
