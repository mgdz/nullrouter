#!/usr/bin/lua
-- converts address with mask to subnets
--
function str2rt(addr)
	local ipaddr, mask = 0
	if type(addr) == "string" then
		local octets = { addr:match("^([0-9]+)%.([0-9]+)%.([0-9]+)%.([0-9]+)(/?([0-9]*))$") }
		for i = 1, 4 do
			local octet = tonumber(octets[i])
			ipaddr = bit32.lshift(ipaddr, 8) + octet
		end
		if octets[5] ~= "" then
			mask = tonumber(octets[6])
		end
		mask = mask or 32
		if mask > MAX_PFX then mask = MAX_PFX end
	end
	return setmetatable({}, {__index= {ipaddr=clearbits(ipaddr, mask), mask=mask}})
end

function rt2str(addr)
	local ipaddr, mask = addr.ipaddr, addr.mask
	return string.format("%d.%d.%d.%d%s",
			math.modf(ipaddr/0x1000000)%0x100,
			math.modf(ipaddr/0x10000)%0x100,
			math.modf(ipaddr/0x100)%0x100,
			          ipaddr%0x100, mask < 32 and ('/' .. mask) or '')
end

function clearbits(ipaddr, mask)
	local s = 32 - mask
	return bit32.lshift(bit32.rshift(ipaddr, s), s)
end

MAX_PFX=tonumber(arg[1])
while true do
	addr = io.read()
	if addr == nil then break end
	if addr ~= "" then
	    route = {}
	    route = str2rt(addr)
	    print (rt2str(route))
	end
end
