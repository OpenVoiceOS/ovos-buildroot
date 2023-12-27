-- WirePlumber
--
-- Copyright © 2022-2023 The WirePlumber project contributors
--    @author Dmitry Sharshakov <d3dx12.xx@gmail.com>
--
-- SPDX-License-Identifier: MIT

local config = ... or {}
config.rules = config.rules or {}

for _, r in ipairs(config.rules) do
  r.interests = {}
  for _, i in ipairs(r.matches) do
    local interest_desc = { type = "properties" }

    for _, c in ipairs(i) do
      c.type = "pw"
      table.insert(interest_desc, Constraint(c))
    end

    local interest = Interest(interest_desc)
    table.insert(r.interests, interest)
  end
end

-- TODO: only check for hotplug of nodes with known DSP rules
nodes_om = ObjectManager {
  Interest { type = "node" },
}

clients_om = ObjectManager {
  Interest { type = "client" }
}

filter_chains = {}
hidden_nodes = {}

nodes_om:connect("object-added", function (om, node)
  for _, r in ipairs(config.rules or {}) do
    for _, interest in ipairs(r.interests) do
      if interest:matches(node["global-properties"]) then
        local id = node["global-properties"]["object.id"]

        if r.filter_chain then
          if filter_chains[id] then
            Log.warning("Sink " .. id .. " has been plugged now, but has a filter chain loaded. Skipping")
          else
            filter_chains[id] = LocalModule("libpipewire-module-filter-chain", r.filter_chain, {}, true)
          end
        end

        if r.hide_parent then
          Log.debug("Hiding node " .. node["bound-id"] .. " from clients")
          for client in clients_om:iterate { type = "client" } do
            if not client["properties"]["wireplumber.daemon"] then
              client:update_permissions { [node["bound-id"]] = "-" }
            end
          end
          hidden_nodes[node["bound-id"]] = id
        end

      end
    end
  end
end)

nodes_om:connect("object-removed", function (om, node)
  local id = node["global-properties"]["object.id"]
  if filter_chains[id] then
    Log.debug("Unloading filter chain associated with sink " .. id)
    filter_chains[id] = nil
  else
    Log.debug("Disconnected sink " .. id .. " does not have any filters to be removed")
  end
end)

clients_om:connect("object-added", function (om, client)
  for id, _ in pairs(hidden_nodes) do
    if not client["properties"]["wireplumber.daemon"] then
      client:update_permissions { [id] = "-" }
    end
  end
end)

nodes_om:activate()
clients_om:activate()
