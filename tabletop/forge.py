#!/usr/bin/env python3
"""The Tabletop Simulator object forge (done-line 0198).

One declared spec (game.spec.json) -> tabletop/build/: TTS-importable
Saved Object JSON, a full save with the table laid out and Global chat
commands, and the standalone .ttslua scripts. Stdlib, deterministic
(GUIDs are content hashes, output bytes are a pure function of the
inputs), in the loop/'s grain: it validates, renders, and refuses —
it never guesses.

The teeth (§10): `validate` refuses a spec that breaks the compendium's
laws — not exactly 8 elements, opposition that is not XOR 7 on the F2^3
cube, non-monotonic tier capacities/timecoin values — and `render`
refuses an unresolved template placeholder or an embedded script that
would break its own Lua long-bracket quoting. tests/test_tabletop.py
proves the refusals non-vacuous.

Usage (from the repo root):
    python tabletop/forge.py check
    python tabletop/forge.py build [--out DIR]
    python tabletop/forge.py list
"""

import argparse
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SPEC_PATH = HERE / "game.spec.json"
LUA_DIR = HERE / "lua"
BUILD_DIR = HERE / "build"

SCRIPT_BRACKET = "====="  # CC_SCRIPTS long-bracket level: [=====[ ... ]=====]
ELEMENT_COUNT = 8         # the F2^3 cube has exactly eight corners
OPPOSE_XOR = 7            # oppose(x) = x XOR 7 (wiki/glossary/element.md)


# ---------------------------------------------------------------- spec

def load_spec(path=SPEC_PATH):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def validate(spec):
    """The canon laws. Returns a list of problems; empty means lawful."""
    problems = []
    elements = spec.get("elements", [])
    if len(elements) != ELEMENT_COUNT:
        problems.append(
            f"elements: expected exactly {ELEMENT_COUNT} on the F2^3 cube, got {len(elements)}")
    by_addr = {}
    by_name = {}
    for e in elements:
        addr, name = e.get("addr"), e.get("name")
        if addr in by_addr:
            problems.append(f"elements: address {addr} claimed twice")
        if name in by_name:
            problems.append(f"elements: name {name!r} claimed twice")
        by_addr[addr], by_name[name] = e, e
        color = e.get("color", {})
        for ch in ("r", "g", "b"):
            v = color.get(ch)
            if not isinstance(v, (int, float)) or not 0 <= v <= 1:
                problems.append(f"elements: {name} color.{ch} is not in [0,1]")
    if len(elements) == ELEMENT_COUNT and not problems:
        for e in elements:
            partner = by_addr.get(e["addr"] ^ OPPOSE_XOR)
            if partner is None or partner["name"] != e.get("opposite"):
                problems.append(
                    f"elements: {e['name']} (addr {e['addr']}) names opposite "
                    f"{e.get('opposite')!r}, but oppose(x)=x XOR {OPPOSE_XOR} says "
                    f"{partner['name'] if partner else '<missing address>'!r}")
    tiers = spec.get("tiers", [])
    if not tiers:
        problems.append("tiers: at least one tier is required")
    prev = None
    for row in tiers:
        t, cap, coin = row.get("tier"), row.get("capacity"), row.get("timecoin")
        if prev is not None:
            if t != prev["tier"] + 1:
                problems.append(f"tiers: tier numbers must step by 1 ({prev['tier']} -> {t})")
            if not (isinstance(cap, (int, float)) and cap > prev["capacity"]):
                problems.append(
                    f"tiers: capacity must strictly increase with tier "
                    f"(T{prev['tier']}={prev['capacity']} -> T{t}={cap})")
            if not (isinstance(coin, (int, float)) and coin > prev["timecoin"]):
                problems.append(
                    f"tiers: timecoin must strictly increase with tier "
                    f"(T{prev['tier']}={prev['timecoin']} -> T{t}={coin})")
        prev = row
    names = {e.get("name") for e in elements}
    for kind in ("races", "classes"):
        for row in spec.get(kind, []):
            if row.get("is") not in names:
                problems.append(f"{kind}: {row.get('name')} IS {row.get('is')!r}, not an element")
    for b in spec.get("samples", {}).get("biomes", []):
        if b.get("element") not in names:
            problems.append(f"samples.biomes: {b.get('name')} element {b.get('element')!r} unknown")
    return problems


# ------------------------------------------------------------- lua render

def lua_str(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def lua_num(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return repr(float(v))


def render_data(spec):
    """The generated CC table every script shares."""
    lines = ["CC = {"]
    lines.append(f"  game = {lua_str(spec['_meta']['game'])},")
    lines.append("  elements = {")
    for e in spec["elements"]:
        c = e["color"]
        lines.append(
            f"    {{ addr = {e['addr']}, name = {lua_str(e['name'])}, "
            f"opposite = {lua_str(e['opposite'])}, role = {lua_str(e['role'])}, "
            f"color = {{ r = {lua_num(c['r'])}, g = {lua_num(c['g'])}, b = {lua_num(c['b'])} }} }},")
    lines.append("  },")
    lines.append("  tiers = {")
    for t in spec["tiers"]:
        lines.append(
            f"    {{ tier = {t['tier']}, capacity = {t['capacity']}, timecoin = {t['timecoin']} }},")
    lines.append("  },")
    lines.append("  races = {")
    for r in spec["races"]:
        lines.append(
            f"    {{ name = {lua_str(r['name'])}, is = {lua_str(r['is'])}, "
            f"wants = {lua_str(r['wants'])}, weak = {lua_str(r['weak'])} }},")
    lines.append("  },")
    lines.append("  classes = {")
    for c in spec["classes"]:
        lines.append(
            f"    {{ name = {lua_str(c['name'])}, is = {lua_str(c['is'])}, "
            f"wants = {lua_str(c['wants'])}, weak = {lua_str(c['weak'])}, "
            f"ability = {lua_str(c.get('ability', ''))} }},")
    lines.append("  },")
    clock = spec["clock"]
    lines.append(
        f"  clock = {{ hours = {clock['hours']}, max_turns = {clock['max_turns']}, "
        f"eon_message = {lua_str(clock['eon_message'])} }},")
    cur = spec["currency"]
    denoms = ", ".join(str(d) for d in cur["denominations"])
    lines.append(
        f"  currency = {{ name = {lua_str(cur['name'])}, start = {cur['start']}, "
        f"denominations = {{ {denoms} }} }},")
    ap = spec["attention"]
    lines.append(
        f"  attention = {{ name = {lua_str(ap['name'])}, per_turn = {ap['per_turn']} }},")
    lines.append("  shapes = {")
    for s in spec["shapes"]:
        lines.append(f"    {{ label = {lua_str(s['label'])}, tts = {lua_str(s['tts'])} }},")
    lines.append("  },")
    lines.append("}")
    return "\n".join(lines)


def render_scripts(spec):
    """Every template rendered; returns {name: lua_source}. Refuses an
    unresolved placeholder or an embed that breaks the long-bracket."""
    data = render_data(spec)
    common = (LUA_DIR / "common.lua").read_text(encoding="utf-8")
    common = common.replace("{{FORGE:DATA}}", data)

    def fill(name):
        src = (LUA_DIR / name).read_text(encoding="utf-8")
        return src.replace("{{FORGE:COMMON}}", common)

    out = {
        "hourglass": fill("hourglass.lua"),
        "clock": fill("clock.lua"),
        "biome": fill("biome.lua"),
        "persona": fill("persona.lua"),
        "global": fill("global.lua"),
    }
    closer = f"]{SCRIPT_BRACKET}]"
    embeds = ["CC_SCRIPTS = {"]
    for key in ("hourglass", "clock", "biome", "persona"):
        if closer in out[key]:
            raise ValueError(
                f"refused: {key} script contains {closer!r} and cannot be embedded "
                f"in the console's long-bracket string")
        embeds.append(f"{key} = [{SCRIPT_BRACKET}[\n{out[key]}\n]{SCRIPT_BRACKET}],")
    embeds.append("}")
    console = (LUA_DIR / "console.lua").read_text(encoding="utf-8")
    console = console.replace("{{FORGE:COMMON}}", common)
    console = console.replace("{{FORGE:SCRIPTS}}", "\n".join(embeds))
    out["console"] = console
    for name, src in out.items():
        if "{{FORGE:" in src:
            raise ValueError(f"refused: unresolved forge placeholder left in {name}")
    return out


# ------------------------------------------------------- saved objects

def guid(name):
    return hashlib.sha256(("cc:" + name).encode("utf-8")).hexdigest()[:6]


def transform(pos, rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
    return {
        "posX": float(pos[0]), "posY": float(pos[1]), "posZ": float(pos[2]),
        "rotX": float(rot[0]), "rotY": float(rot[1]), "rotZ": float(rot[2]),
        "scaleX": float(scale[0]), "scaleY": float(scale[1]), "scaleZ": float(scale[2]),
    }


def obj(tts_name, nickname, pos, scale=(1, 1, 1), rot=(0, 0, 0), tint=None,
        description="", gm_notes="", lua="", tags=(), locked=False, contained=None,
        extra=None):
    state = {
        "GUID": guid(nickname),
        "Name": tts_name,
        "Transform": transform(pos, rot, scale),
        "Nickname": nickname,
        "Description": description,
        "GMNotes": gm_notes,
        "ColorDiffuse": ({"r": float(tint[0]), "g": float(tint[1]), "b": float(tint[2])}
                         if tint else {"r": 1.0, "g": 1.0, "b": 1.0}),
        "Tags": list(tags),
        "Locked": bool(locked),
        "Grid": True,
        "Snap": True,
        "Autoraise": True,
        "Sticky": True,
        "Tooltip": True,
        "LuaScript": lua,
        "LuaScriptState": "",
        "XmlUI": "",
    }
    if contained is not None:
        state["ContainedObjects"] = contained
    if extra:
        state.update(extra)
    return state


def color_of(element):
    c = element["color"]
    return (c["r"], c["g"], c["b"])


def build_objects(spec, scripts):
    """Returns {file_stem: [object_states]} — the kit, each piece placed
    where the full save lays it out."""
    elements = spec["elements"]
    tiers = spec["tiers"]
    coin_name = spec["currency"]["name"]

    console = obj("BlockRectangle", "Spawner Console", (-14, 1.5, -2),
                  scale=(6, 0.4, 8), tint=(0.16, 0.15, 0.20), locked=True,
                  lua=scripts["console"], tags=["cc-console"],
                  description="The in-game script generator. Chat: !cc help")

    clock = obj("BlockSquare", "The Global Clock", (0, 1.5, 6),
                scale=(7, 0.3, 7), tint=(0.30, 0.22, 0.16),
                lua=scripts["clock"],
                gm_notes=json.dumps({"max_turns": spec["clock"]["max_turns"]}),
                tags=["cc-clock"],
                description="One hand, twelve hours. END TURN fires the world.")

    hourglasses = []
    for i, t in enumerate(tiers):
        hourglasses.append(obj(
            "BlockRectangle", f"Hourglass T{t['tier']}",
            (-8 + i * 4, 1.5, -10), scale=(2.5, 0.8, 2.5),
            tint=(0.55 + 0.08 * t["tier"], 0.50 + 0.06 * t["tier"], 0.35),
            lua=scripts["hourglass"],
            gm_notes=json.dumps({"tier": t["tier"]}),
            tags=["cc-holder", "cc-hourglass"],
            description=(f"Tier {t['tier']}: holds {t['capacity']} grains, "
                         f"worth {t['timecoin']} {coin_name}.")))

    bags = []
    for i, e in enumerate(elements):
        grain = obj("Checker_white", f"{e['name']} Grain", (0, 0, 0),
                    scale=(0.45, 0.45, 0.45), tint=color_of(e), tags=["cc-grain"])
        bags.append(obj(
            "Infinite_Bag", f"{e['name']} Grains",
            (-8.4 + i * 2.4, 1.5, 12), scale=(0.9, 0.9, 0.9), tint=color_of(e),
            tags=["cc-grainbag"], contained=[grain],
            description=f"{e['role']} | opposite: {e['opposite']}"))

    by_name = {e["name"]: e for e in elements}
    biomes = []
    biome_positions = [(-7, 1.5, -2), (7, 1.5, -2), (0, 1.5, -6)]
    for i, b in enumerate(spec["samples"]["biomes"]):
        e = by_name[b["element"]]
        biomes.append(obj(
            "BlockRectangle", f"{b['name']} — {b['element']} biome",
            biome_positions[i % len(biome_positions)], scale=(6, 0.2, 6),
            tint=color_of(e), lua=scripts["biome"],
            gm_notes=json.dumps({"name": b["name"], "element": b["element"],
                                 "own": b["own"], "rate": b["rate"]}),
            tags=["cc-holder", "cc-biome", "cc-turn-listener"],
            description=f"Generates {b['rate']} {b['element']} grain(s) per turn."))

    personas = []
    persona_positions = [(-7, 2.5, -2), (0, 1.5, -3)]
    for i, p in enumerate(spec["samples"]["personas"]):
        personas.append(obj(
            "PlayerPawn", f"Unknown T{p['tier']}",
            persona_positions[i % len(persona_positions)], scale=(1.1, 1.1, 1.1),
            tint=(0.45, 0.45, 0.45), lua=scripts["persona"],
            gm_notes=json.dumps({"name": p["name"], "race": p["race"],
                                 "class": p["class"], "tier": p["tier"],
                                 "pool": p["pool"], "identified": False}),
            tags=["cc-holder", "cc-persona"],
            description="Unidentified persona — click ID? on the pawn."))
    personas.append(obj(
        "PlayerPawn", "Unknown T1", persona_positions[1], scale=(1.1, 1.1, 1.1),
        tint=(0.45, 0.45, 0.45), lua=scripts["persona"],
        gm_notes=json.dumps({"name": "Nameless", "race": "Mortal", "class": "Magus",
                             "tier": 1, "pool": {}, "identified": False}),
        tags=["cc-holder", "cc-persona"],
        description="A blank persona — edit GM Notes to make anyone."))

    chip_types = {10: "Chip_10", 100: "Chip_100", 1000: "Chip_1000"}
    coins = []
    for i, denom in enumerate(spec["currency"]["denominations"]):
        chip = obj(chip_types.get(denom, "Chip_100"), f"{coin_name} {denom}",
                   (0, 0, 0), tint=(0.9, 0.75, 0.3))
        coins.append(obj(
            "Infinite_Bag", f"{coin_name} {denom} Mint",
            (13, 1.5, 4 + i * 3), scale=(0.9, 0.9, 0.9), tint=(0.85, 0.7, 0.25),
            tags=["cc-coinbag"], contained=[chip],
            description=f"An endless mint of {denom}-{coin_name} chips."))
    coins.append(obj(
        "Counter", f"{coin_name} Bank", (13, 1.5, 1), scale=(1.4, 1.4, 1.4),
        tint=(0.85, 0.7, 0.25),
        description=f"The player starts with {spec['currency']['start']} {coin_name}.",
        extra={"Counter": {"value": spec["currency"]["start"]}}))

    ap = spec["attention"]
    ap_token = obj("Checker_white", ap["name"], (0, 0, 0),
                   scale=(0.5, 0.5, 0.5), tint=(0.15, 0.65, 0.6))
    ap_bag = obj("Infinite_Bag", f"{ap['name']} Tokens", (13, 1.5, -2),
                 scale=(0.9, 0.9, 0.9), tint=(0.15, 0.65, 0.6),
                 contained=[ap_token],
                 description=(f"{ap['name']} — attention/action points "
                              f"({ap['per_turn']}/turn; unspent converts to {coin_name})."))

    shape_items = [obj(s["tts"], f"{s['label']} (shape)", (0, 0, 0))
                   for s in spec["shapes"]]
    crate = obj("Bag", "Shape Crate", (-14, 1.5, 6), scale=(1.1, 1.1, 1.1),
                tint=(0.5, 0.45, 0.4), contained=shape_items,
                description="One of each generic shape — recolor via the console or right-click.")

    return {
        "spawner-console": [console],
        "global-clock": [clock],
        "hourglasses-t1-t5": hourglasses,
        "element-grain-bags": bags,
        "biomes-sample": biomes,
        "personas-sample": personas,
        "timecoin-mint": coins,
        "ap-tokens": [ap_bag],
        "shape-crate": [crate],
    }


def saved_object(save_name, object_states, global_lua="", table="", note=""):
    return {
        "SaveName": save_name,
        "Date": "",
        "VersionNumber": "",
        "GameMode": "",
        "GameType": "",
        "GameComplexity": "",
        "Tags": [],
        "Gravity": 0.5,
        "PlayArea": 0.5,
        "Table": table,
        "Sky": "",
        "Note": note,
        "TabStates": {},
        "LuaScript": global_lua,
        "LuaScriptState": "",
        "XmlUI": "",
        "ObjectStates": object_states,
    }


# ------------------------------------------------------------------ build

def build(spec, out_dir=BUILD_DIR):
    problems = validate(spec)
    if problems:
        raise ValueError("refused: the spec breaks the canon laws:\n  - "
                         + "\n  - ".join(problems))
    scripts = render_scripts(spec)
    groups = build_objects(spec, scripts)

    out = pathlib.Path(out_dir)
    lua_out = out / "lua"
    obj_out = out / "objects"
    save_out = out / "save"
    for d in (lua_out, obj_out, save_out):
        d.mkdir(parents=True, exist_ok=True)

    written = []

    def write(path, text):
        path.write_text(text, encoding="utf-8", newline="\n")
        written.append(path)

    for name, src in sorted(scripts.items()):
        write(lua_out / f"{name}.ttslua", src)

    all_states = []
    for stem, states in groups.items():
        all_states.extend(states)
        write(obj_out / f"{stem}.json",
              json.dumps(saved_object(f"CC {stem}", states), indent=2,
                         ensure_ascii=False) + "\n")

    guids = [s["GUID"] for s in all_states]
    dupes = {g for g in guids if guids.count(g) > 1}
    if dupes:
        raise ValueError(f"refused: duplicate GUIDs across the kit: {sorted(dupes)}")

    full = saved_object(
        "Catalyst Core — The 13th Hour (paper play)", all_states,
        global_lua=scripts["global"], table="Table_Hexagon",
        note=("Paper-play kit forged from tabletop/game.spec.json. "
              "Chat: !cc help. Every scripted piece is reconfigurable via GM Notes."))
    write(save_out / "CatalystCore-PaperPlay.json",
          json.dumps(full, indent=2, ensure_ascii=False) + "\n")

    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("check", help="validate the spec against the canon laws")
    b = sub.add_parser("build", help="regenerate tabletop/build/")
    b.add_argument("--out", default=str(BUILD_DIR))
    b.add_argument("--spec", default=str(SPEC_PATH))
    sub.add_parser("list", help="what the forge would emit")
    args = parser.parse_args(argv)

    if args.cmd == "check":
        problems = validate(load_spec())
        if problems:
            print("result: needs-you — the spec breaks the canon laws:")
            for p in problems:
                print(f"  - {p}")
            return 1
        print("result: done — the spec is lawful (8 elements, XOR-7 opposition, "
              "monotonic tiers)")
        return 0

    if args.cmd == "build":
        try:
            written = build(load_spec(args.spec), args.out)
        except ValueError as exc:
            print(f"result: needs-you — {exc}")
            return 1
        print(f"result: done — forged {len(written)} file(s) into {args.out}")
        return 0

    if args.cmd == "list":
        spec = load_spec()
        scripts = render_scripts(spec)
        groups = build_objects(spec, scripts)
        for name in sorted(scripts):
            print(f"lua/{name}.ttslua")
        for stem, states in groups.items():
            print(f"objects/{stem}.json  ({len(states)} object(s))")
        print("save/CatalystCore-PaperPlay.json  (full table + Global chat commands)")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
