// mcp.js — recognize, discover, and surface MCP servers + their tools (pure
// data + fs layer, no `vscode`).
//
// Row 13 of the parity checklist: "MCP tools available + invocable." The bridge
// spike (SPIKE-FINDINGS.md) resolved this row to `inherit`: MCP is provided by
// the SAME `claude` binary reading the SAME cwd config, so a configured MCP
// server is LOADED by the engine and its tools ride along in the init event's
// `tools` list — named `mcp__<server>__<tool>` — exactly as the built-in tools
// do. "Available" is proven by that live tools list; "invocable" is the engine
// calling the tool mid-turn (pass-through, like any tool — the surface does not
// re-implement an MCP client), with the row-9 allow/deny policy able to
// pre-authorize an `mcp__server__tool` by name and the live-verified
// `--mcp-config`/`--strict-mcp-config` flags letting the surface point the
// engine at a config. So this module owns only the SURFACE of MCP:
//   1. RECOGNISE an MCP tool name + split it into { server, tool } (parseMcpTool),
//   2. group the engine's LIVE tools list by server (mcpServersFromTools) — the
//      proof of what actually loaded,
//   3. DISCOVER the CONFIGURED servers from the same on-disk config the CLI
//      reads (`<cwd>/.mcp.json` + the user `~/.claude.json` mcpServers), and
//   4. MERGE the two into the surface's view (listMcpServers): each configured
//      server annotated with the tools the live env exposes for it (available).
//
// Discovery is a FOLD of the same on-disk config the CLI itself reads (the
// blueprint §The law: paint what is there, invent nothing), so it is proven
// host-free against a fake config — exactly as slash.js folds the command store.
// The engine remains the authority on what an MCP tool DOES and on whether a
// server actually connects; the surface recognises + discovers + offers, and a
// real billed turn that invokes an MCP tool is a human's to run.

'use strict';

const fs = require('fs');
const path = require('path');

// The naming convention the engine uses for an MCP server's tools in the init
// event's `tools` list: `mcp__<server>__<tool>`. Server names from
// `claude mcp add` are simple identifiers; the tool name is the remainder after
// the server's trailing `__` (so a tool name may itself contain `__`).
const MCP_PREFIX = 'mcp__';

// parseMcpTool(name) -> { name, server, tool } for an MCP tool, else null.
// Conservative: the name must start with `mcp__`, carry a non-empty server, a
// `__` separator, and a non-empty tool. A plain tool ('Bash', 'Read') is null.
function parseMcpTool(name) {
  if (typeof name !== 'string') return null;
  if (name.indexOf(MCP_PREFIX) !== 0) return null;
  const rest = name.slice(MCP_PREFIX.length);
  const sep = rest.indexOf('__');
  if (sep <= 0) return null; // empty server, or no separator
  const server = rest.slice(0, sep);
  const tool = rest.slice(sep + 2);
  if (!server || !tool) return null;
  return { name, server, tool };
}

// isMcpTool(name) -> true when `name` is an MCP tool name (`mcp__server__tool`).
function isMcpTool(name) {
  return parseMcpTool(name) !== null;
}

// mcpToolName(server, tool) -> the canonical `mcp__server__tool` identifier the
// engine uses (and the row-9 allow-list authorizes). Pure string join.
function mcpToolName(server, tool) {
  return MCP_PREFIX + String(server == null ? '' : server) + '__' +
    String(tool == null ? '' : tool);
}

// sortByKey(key) -> a stable string comparator on `obj[key]`.
function sortByKey(key) {
  return (a, b) => {
    const x = a && a[key] != null ? String(a[key]) : '';
    const y = b && b[key] != null ? String(b[key]) : '';
    return x < y ? -1 : x > y ? 1 : 0;
  };
}

// mcpServersFromTools(tools) -> the MCP tools present in an engine tools list
// (the init event's `tools`, i.e. foldReply's reply.tools), grouped by server:
//   [{ server, tools:[toolName,...] }]  (servers + tools sorted, deduped)
// This is the LIVE view — the proof of which MCP tools the inherited
// environment actually loaded (so the engine can invoke them). A non-MCP tool
// is ignored; a non-array yields [].
function mcpServersFromTools(tools) {
  const list = Array.isArray(tools) ? tools : [];
  const byServer = new Map();
  for (const t of list) {
    const p = parseMcpTool(t);
    if (!p) continue;
    if (!byServer.has(p.server)) byServer.set(p.server, new Set());
    byServer.get(p.server).add(p.tool);
  }
  const out = [];
  for (const [server, toolSet] of byServer) {
    const tns = Array.from(toolSet).sort();
    out.push({ server, tools: tns });
  }
  out.sort(sortByKey('server'));
  return out;
}

// mcpConfigPathFor(base) -> the `<base>/.mcp.json` project MCP config the CLI
// reads. Pure path join (no fs touch).
function mcpConfigPathFor(base) {
  return path.join(String(base || ''), '.mcp.json');
}

// userConfigPathFor(home) -> the `~/.claude.json` user config the CLI keeps
// user-scope MCP servers in (under a top-level `mcpServers`). Pure path join.
function userConfigPathFor(home) {
  return path.join(String(home || ''), '.claude.json');
}

// transportOf(def) -> a short, human transport label for an MCP server def, from
// the same fields the CLI's config uses: an explicit `type`, else `http`/`sse`
// when a `url` is present, else `stdio` when a `command` is present, else
// 'unknown'. Never throws on an odd shape.
function transportOf(def) {
  const d = def && typeof def === 'object' ? def : {};
  if (typeof d.type === 'string' && d.type) return d.type;
  if (typeof d.url === 'string' && d.url) return 'http';
  if (typeof d.command === 'string' && d.command) return 'stdio';
  return 'unknown';
}

// readMcpServerNames(file, scope) -> [{ name, scope, transport }] for every
// server under a config file's `mcpServers` object. Missing/unreadable/torn
// (bad JSON) tolerant -> [] (the config simply contributes none — never throws).
// Sorted by name.
function readMcpServerNames(file, scope) {
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (_) {
    return [];
  }
  let obj;
  try {
    obj = JSON.parse(raw);
  } catch (_) {
    return []; // a torn/partial config never breaks discovery
  }
  const servers =
    obj && obj.mcpServers && typeof obj.mcpServers === 'object'
      ? obj.mcpServers
      : null;
  if (!servers) return [];
  const out = [];
  for (const name of Object.keys(servers)) {
    out.push({
      name,
      scope: scope || 'project',
      transport: transportOf(servers[name]),
    });
  }
  out.sort(sortByKey('name'));
  return out;
}

// discoverMcpServers({ projectDir, userConfig }) -> the merged, deduped, sorted
// list of CONFIGURED MCP servers the CLI would load for this workspace:
//   [{ name, scope, transport }]
// the project `<cwd>/.mcp.json` (scope 'project') merged with the user config's
// `mcpServers` (scope 'user'). PROJECT shadows USER when a name appears in both
// (the same precedence the CLI honours). Missing/torn tolerant -> []. This is
// the CONFIGURED view (what is on disk); the LIVE view (what actually loaded) is
// mcpServersFromTools(reply.tools).
function discoverMcpServers(opts) {
  const o = opts || {};
  const user = o.userConfig ? readMcpServerNames(o.userConfig, 'user') : [];
  const project = o.projectDir
    ? readMcpServerNames(mcpConfigPathFor(o.projectDir), 'project')
    : [];
  const byName = new Map();
  for (const s of user) byName.set(s.name, s);
  for (const s of project) byName.set(s.name, s); // project shadows user
  const merged = Array.from(byName.values());
  merged.sort(sortByKey('name'));
  return merged;
}

// listMcpServers({ projectDir, userConfig, tools }) -> the surface's MCP view:
// the CONFIGURED servers (discoverMcpServers) each annotated with the tools the
// LIVE engine env exposes for it (mcpServersFromTools(tools)):
//   [{ name, scope, transport, tools:[toolName,...], available:boolean }]
// - `tools` is the live tool list for that server (empty when not yet loaded);
// - `available` is true when the live env actually exposes the server's tools
//   (so the engine can invoke them) — honest: a server configured on disk but
//   absent from the live tools is available:false (configured, not loaded).
// A server present in the LIVE tools but in NO config (e.g. a user-global one
// not in the files we read) is still surfaced, with scope 'live' — the engine
// named it, so it is real. Sorted by name.
function listMcpServers(opts) {
  const o = opts || {};
  const configured = discoverMcpServers(o);
  const live = mcpServersFromTools(o.tools);
  const liveByServer = new Map();
  for (const s of live) liveByServer.set(s.server, s.tools);

  const byName = new Map();
  for (const c of configured) {
    const liveTools = liveByServer.get(c.name) || [];
    byName.set(c.name, {
      name: c.name,
      scope: c.scope,
      transport: c.transport,
      tools: liveTools,
      available: liveTools.length > 0,
    });
  }
  // Live servers with no config entry — the env knows them, surface them too.
  for (const s of live) {
    if (byName.has(s.server)) continue;
    byName.set(s.server, {
      name: s.server,
      scope: 'live',
      transport: 'unknown',
      tools: s.tools,
      available: s.tools.length > 0,
    });
  }
  const merged = Array.from(byName.values());
  merged.sort(sortByKey('name'));
  return merged;
}

module.exports = {
  MCP_PREFIX,
  parseMcpTool,
  isMcpTool,
  mcpToolName,
  mcpServersFromTools,
  mcpConfigPathFor,
  userConfigPathFor,
  transportOf,
  readMcpServerNames,
  discoverMcpServers,
  listMcpServers,
};
