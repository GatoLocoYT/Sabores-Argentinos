package ar.sabores;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.Consumables;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.item.consume_effects.ApplyStatusEffectsConsumeEffect;

public final class SaboresArgentinos implements ModInitializer {
    public static final String ID = "sabores_argentinos";
    private static final String TEXT = "tooltip." + ID + ".";
    private static final String FILLINGS = "/empanadas.tsv";
    private final List<Item> creativeItems = new ArrayList<>();

    @Override
    public void onInitialize() {
        Item mate = food("mate_amargo", 7, 1, 0.3F, true, Items.BOWL,
            new Effect(MobEffects.SPEED, 35, 1));
        food("choripan", 10, 4, 0.65F, false, null,
            new Effect(MobEffects.SLOWNESS, 15, 2),
            new Effect(MobEffects.INSTANT_HEALTH, 0, 2));
        food("alfajor_dulce_de_leche", 4, 16, 0.3F, false, null,
            new Effect(MobEffects.SPEED, 20, 1));
        food("dulce_de_leche", 16, 1, 0.65F, false, Items.BUCKET,
            new Effect(MobEffects.SATURATION, 0, 1),
            new Effect(MobEffects.SLOWNESS, 120, 3));

        registerEmpanadas();

        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, id("comidas"),
            FabricCreativeModeTab.builder()
                .title(Component.translatable("itemGroup." + ID + ".comidas"))
                .icon(() -> new ItemStack(mate))
                .displayItems((parameters, output) -> creativeItems.forEach(output::accept))
                .build());
    }

    private void registerEmpanadas() {
        List<String> rawItems = new ArrayList<>();
        InputStream input = Objects.requireNonNull(getClass().getResourceAsStream(FILLINGS), FILLINGS);
        try (var reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
            for (String line : reader.lines().skip(1).toList()) {
                String[] fields = line.split("\t", -1);
                String filling = fields[0];
                Effect[] effects = Arrays.stream(fields[5].split(","))
                    .map(Effect::parse)
                    .toArray(Effect[]::new);
                food("empanada_" + filling, 8, 12, 0.5F, false, null, effects);
                rawItems.add("empanada_cruda_" + filling);
            }
        } catch (IOException error) {
            throw new IllegalStateException("No se pudo leer " + FILLINGS, error);
        }

        for (String name : rawItems) {
            register(name, new Item.Properties().stacksTo(12)
                .component(DataComponents.LORE, new ItemLore(List.of(Component.translatable(TEXT + "horno")))));
        }
    }

    private Item food(String name, int hunger, int stackSize, float saturation, boolean drink,
                      Item remainder, Effect... effects) {
        var consumable = drink ? Consumables.defaultDrink() : Consumables.defaultFood();
        var lore = new ArrayList<Component>();
        for (Effect effect : effects) {
            var instance = new MobEffectInstance(effect.type(), Math.max(1, effect.seconds() * 20), effect.level() - 1);
            consumable.onConsume(new ApplyStatusEffectsConsumeEffect(instance, effect.chance()));
            lore.add(effect.tooltip());
        }

        var properties = new Item.Properties()
            .stacksTo(stackSize)
            .food(new FoodProperties.Builder().nutrition(hunger).saturationModifier(saturation).build(),
                consumable.build())
            .component(DataComponents.LORE, new ItemLore(lore));
        if (remainder != null) {
            properties.usingConvertsTo(remainder);
            if (remainder == Items.BUCKET) {
                properties.craftRemainder(remainder);
            }
        }
        return register(name, properties);
    }

    private Item register(String name, Item.Properties properties) {
        var key = ResourceKey.create(Registries.ITEM, id(name));
        Item item = Registry.register(BuiltInRegistries.ITEM, key, new Item(properties.setId(key)));
        creativeItems.add(item);
        return item;
    }

    private static Identifier id(String name) {
        return Identifier.fromNamespaceAndPath(ID, name);
    }

    private record Effect(Holder<MobEffect> type, int seconds, int level, float chance) {
        Effect(Holder<MobEffect> type, int seconds, int level) {
            this(type, seconds, level, 1.0F);
        }

        static Effect parse(String text) {
            String[] fields = text.split(":");
            var effect = BuiltInRegistries.MOB_EFFECT.get(Identifier.withDefaultNamespace(fields[0])).orElseThrow();
            float chance = fields.length == 4 ? Integer.parseInt(fields[3]) / 100.0F : 1.0F;
            return new Effect(effect, Integer.parseInt(fields[1]), Integer.parseInt(fields[2]), chance);
        }

        Component tooltip() {
            Component name = type.value().getDisplayName();
            if (chance < 1.0F) {
                return Component.translatable(TEXT + "probabilidad", name, level, Math.round(chance * 100));
            }
            if (seconds == 0) {
                return Component.translatable(TEXT + "instantaneo", name, level);
            }
            return Component.translatable(TEXT + "duracion", name, level, seconds);
        }
    }
}
