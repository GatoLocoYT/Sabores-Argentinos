#!/usr/bin/env python3
"""Regenera recetas, traducciones, modelos y texturas con la biblioteca estándar."""
import csv
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src/main/resources"
MOD = "sabores_argentinos"
DATA = ROOT / "data" / MOD
ASSETS = ROOT / "assets" / MOD

LANG = {
    "es_ar": {
        "itemGroup.sabores_argentinos.comidas": "Sabores Argentinos",
        "tooltip.sabores_argentinos.horno": "Horneala para cocinarla",
        "tooltip.sabores_argentinos.duracion": "%s (nivel %s) · %s s",
        "tooltip.sabores_argentinos.instantaneo": "%s (nivel %s)",
        "tooltip.sabores_argentinos.probabilidad": "%s (nivel %s) · %s %% de probabilidad",
    },
    "en_us": {
        "itemGroup.sabores_argentinos.comidas": "Argentine Flavors",
        "tooltip.sabores_argentinos.horno": "Bake in a furnace",
        "tooltip.sabores_argentinos.duracion": "%s (level %s) · %s s",
        "tooltip.sabores_argentinos.instantaneo": "%s (level %s)",
        "tooltip.sabores_argentinos.probabilidad": "%s (level %s) · %s %% chance",
    },
}

MATE = (
    "...........bb...",
    "..........bs....",
    "..........bs....",
    ".........bs.....",
    ".........bs.....",
    "....ooooobs.....",
    "...oggGggso.....",
    "..ogGgGgGggo....",
    "..ollggglllo....",
    "..oLlllllllo....",
    "..oLllcclllo....",
    "...oLlccllo.....",
    "...oLlllllo.....",
    "....ollllo......",
    ".....oooo.......",
    "................",
)

CHORI = (
    "................",
    "................",
    "............oo..",
    ".........ooolho.",
    ".......oolhLhlo.",
    ".....ooLhhhlrro.",
    "...oolLhhlrRro..",
    "..olLhllrRRroo..",
    ".olLllrRRgollo..",
    ".ollrRRgrlllo...",
    ".orrRgrllllo....",
    ".orlrllLllo.....",
    "..olLllllo......",
    "...oooooo.......",
    "................",
    "................",
)

ALFAJOR = (
    "................",
    "................",
    "................",
    ".....oooooo.....",
    "...oohhhhhhoo...",
    "..ohhllLllhhho..",
    ".ohllLlllLllhho.",
    ".ohlllllllllhho.",
    ".oocccccccccooo.",
    ".orrRRRRRRRRrro.",
    ".ooccccccccccoo.",
    "..olhhllllhllo..",
    "...oollllloo....",
    ".....ooooo......",
    "................",
    "................",
)

DULCE = (
    "................",
    ".....oooooo.....",
    "....osssssso....",
    "....obsbbbso....",
    ".....oooooo.....",
    "....oLlllllo....",
    "...oLhhhllllo...",
    "...oLhccclllo...",
    "...oLsbsbsllo...",
    "...oLbbbbcllo...",
    "...oLbsbscllo...",
    "...oLlccllllo...",
    "...oLLLLlllo....",
    "....ooooooo.....",
    "................",
    "................",
)

EMPANADA = (
    "................",
    "................",
    "................",
    ".....oooo.......",
    "...oolLlloo.....",
    "..olLLllllloo...",
    ".olLlhhhllhllo..",
    ".ollhhllllllllo.",
    ".ollllllllllllo.",
    ".ollcccccclcloo.",
    "..oclcxcxclcolo.",
    "...olclclclcoo..",
    "....ooococooo...",
    ".......ooo......",
    "................",
    "................",
)

PALETTES = {
    "mate": {"o": "392c25", "b": "748a85", "s": "cfebe5", "g": "56773b", "G": "7a9c47",
             "l": "9a5a38", "L": "cc9660", "c": "74472e"},
    "chori": {"o": "583225", "l": "c47a3e", "h": "e3a455", "L": "f4c478",
              "r": "813932", "R": "ad5141", "g": "72933e"},
    "alfajor": {"o": "39241f", "h": "c39367", "l": "a5704d", "L": "f3d094",
                "c": "684333", "r": "9c5029", "R": "e29c50"},
    "dulce": {"o": "593829", "s": "e4d5bb", "b": "9db6a9", "L": "f5d19b",
              "h": "d18a49", "l": "ab5c2c", "c": "88421f"},
    "empanada": {"o": "663827", "l": "d58a44", "L": "f9d18a", "h": "edac58", "c": "aa6037"},
    "cruda": {"o": "82654d", "l": "d5b68c", "L": "fcdfb2", "h": "eacba0", "c": "b49273"},
}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def chunk(kind, payload):
    data = kind + payload
    return struct.pack(">I", len(payload)) + data + struct.pack(">I", zlib.crc32(data))


def draw(name, pixels, palette):
    assert len(pixels) == 16 and all(len(row) == 16 for row in pixels), name
    rgba = {key: bytes.fromhex(color + "ff") for key, color in palette.items()}
    rgba["."] = bytes(4)
    scanlines = b"".join(b"\x00" + b"".join(rgba[pixel] for pixel in row) for row in pixels)
    header = struct.pack(">IIBBBBB", 16, 16, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(scanlines))
    path = ASSETS / "textures/item" / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png + chunk(b"IEND", b""))


def item(name, spanish, english, pixels, palette):
    for lang, label in (("es_ar", spanish), ("en_us", english)):
        LANG[lang][f"item.{MOD}.{name}"] = label
    write_json(ASSETS / "items" / f"{name}.json", {
        "model": {"type": "minecraft:model", "model": f"{MOD}:item/{name}"}
    })
    write_json(ASSETS / "models/item" / f"{name}.json", {
        "parent": "minecraft:item/generated", "textures": {"layer0": f"{MOD}:item/{name}"}
    })
    draw(name, pixels, palette)


def recipe(name, data, unlock_with):
    write_json(DATA / "recipe" / f"{name}.json", data)
    recipe_id = f"{MOD}:{name}"
    write_json(DATA / "advancement/recipes/food" / f"{name}.json", {
        "parent": "minecraft:recipes/root",
        "criteria": {
            "has_recipe": {
                "trigger": "minecraft:recipe_unlocked",
                "conditions": {"recipes": recipe_id},
            },
            "has_ingredients": {
                "trigger": "minecraft:inventory_changed",
                "conditions": {"items": [{"items": ingredient} for ingredient in unlock_with]},
            },
        },
        "requirements": [["has_recipe", "has_ingredients"]],
        "rewards": {"recipes": [recipe_id]},
    })


def shapeless(name, ingredients, count=1, group=None):
    result = {"id": f"{MOD}:{name}", "count": count}
    data = {"type": "minecraft:crafting_shapeless", "category": "misc",
            "ingredients": ingredients, "result": result}
    if group:
        data["group"] = group
    recipe(name, data, ingredients)


def smelt(name, ingredient, seconds, experience, group=None):
    data = {
        "type": "minecraft:smelting", "category": "food", "ingredient": ingredient,
        "result": {"id": f"{MOD}:{name}"}, "cookingtime": seconds * 20,
        "experience": experience,
    }
    if group:
        data["group"] = group
    recipe(name, data, [ingredient])


def vanilla(names):
    ids = [f"minecraft:{name}" for name in names.split("|")]
    return ids[0] if len(ids) == 1 else ids


def main():
    item("mate_amargo", "Mate amargo", "Bitter Mate", MATE, PALETTES["mate"])
    shapeless("mate_amargo", list(map(vanilla, ["bowl", "dried_kelp", "water_bucket"])))
    item("choripan", "Choripán", "Choripán", CHORI, PALETTES["chori"])
    shapeless("choripan", list(map(vanilla, ["bread", "cooked_porkchop"])))
    item("alfajor_dulce_de_leche", "Alfajor de dulce de leche", "Dulce de Leche Alfajor",
         ALFAJOR, PALETTES["alfajor"])
    shapeless("alfajor_dulce_de_leche", ["minecraft:cookie", f"{MOD}:dulce_de_leche", "minecraft:cookie"],
              count=4)
    item("dulce_de_leche", "Dulce de leche", "Dulce de Leche", DULCE, PALETTES["dulce"])
    smelt("dulce_de_leche", "minecraft:milk_bucket", 20, 0.35)

    with (ROOT / "empanadas.tsv").open(encoding="utf-8") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            name = "empanada_" + row["id"]
            raw = "empanada_cruda_" + row["id"]
            item(name, "Empanada de " + row["es"].lower(), row["en"] + " Empanada", EMPANADA,
                 PALETTES["empanada"] | {"x": row["accent"]})
            item(raw, "Empanada cruda de " + row["es"].lower(), "Raw " + row["en"] + " Empanada",
                 EMPANADA, PALETTES["cruda"] | {"x": row["accent"]})
            ingredients = list(map(vanilla, row["ingredients"].split("+")))
            shapeless(raw, ["minecraft:wheat", *ingredients], group="sabores_argentinos_empanadas_crudas")
            smelt(name, f"{MOD}:{raw}", 10, 0.2, group="sabores_argentinos_empanadas")

    write_json(ASSETS / "lang/es_ar.json", LANG["es_ar"])
    write_json(ASSETS / "lang/es_es.json", LANG["es_ar"])
    write_json(ASSETS / "lang/en_us.json", LANG["en_us"])


if __name__ == "__main__":
    main()
