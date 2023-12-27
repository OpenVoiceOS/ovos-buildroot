components = {}

function load_module(m, a)
  assert(type(m) == "string", "module name is mandatory, bail out");
  if not components[m] then
    components[m] = { "libwireplumber-module-" .. m, type = "module", args = a }
  end
end

function load_optional_module(m, a)
  assert(type(m) == "string", "module name is mandatory, bail out");
  if not components[m] then
    components[m] = { "libwireplumber-module-" .. m, type = "module", args = a, optional = true }
  end
end

function load_pw_module(m, a)
  assert(type(m) == "string", "module name is mandatory, bail out");
  if not components[m] then
    components[m] = { "libpipewire-module-" .. m, type = "pw_module", args = a }
  end
end

function load_script(s, a)
  if not components[s] then
    components[s] = { s, type = "script/lua", args = a }
  end
end

function load_monitor(s, a)
  load_script("monitors/" .. s .. ".lua", a)
end

function load_access(s, a)
  load_script("access/access-" .. s .. ".lua", a)
end
