# Sabores Argentinos

Mod para **Minecraft Java Edition 26.3** con **Fabric**. Agrega comida argentina, una pestaña en el inventario creativo y recetas que se desbloquean al conseguir los ingredientes.

## Instalación

1. Instalá Fabric Loader para Minecraft 26.3. La versión probada es 0.20.1.
2. Poné el JAR del mod y Fabric API para 26.3 en la carpeta `mods`.
3. Iniciá el perfil de Fabric. En multijugador, instalá ambos JAR en el servidor y en cada cliente. Si configurás Java a mano, usá Java 25.

- [Instalador de Fabric](https://fabricmc.net/use/installer/)
- [Fabric API para 26.3](https://modrinth.com/mod/fabric-api/versions?g=26.3)

## Recetas y efectos

Un muslito de la barra equivale a dos puntos de hambre. Las recetas de mesa son sin forma, así que los ingredientes pueden ir en cualquier posición.

| Comida | Muslitos | Pila | Receta | Efecto |
| --- | ---: | ---: | --- | --- |
| Mate amargo | 3,5 | 1 | Cuenco + algas secas + balde con agua | Velocidad I durante 35 s |
| Choripán | 5 | 4 | Pan + chuleta de cerdo cocida | Curación instantánea II y Lentitud II durante 15 s |
| Empanada de carne picante | 4 | 12 | Trigo + carne de vaca cruda o cocida + bayas dulces. Después, horno | Velocidad I durante 25 s y 20 % de probabilidad de Daño instantáneo I |
| Empanada de humita | 4 | 12 | Trigo + semillas de calabaza + balde de leche. Después, horno | Regeneración I durante 8 s |
| Empanadas de otros rellenos | 4 | 12 | Trigo + alimento de relleno. Después, horno | Depende del relleno. Se muestra en la descripción del ítem |
| Alfajor de dulce de leche | 2 | 16 | Dos galletas + dulce de leche. Rinde cuatro alfajores | Velocidad I durante 20 s |
| Dulce de leche | 8 | 1 | Balde de leche en el horno durante 20 s | Saturación I y Lentitud III durante 120 s |

El mate usa algas secas en lugar de yerba. La humita usa semillas de calabaza en lugar de maíz. El choripán usa la chuleta cocida como ingrediente de cerdo. Al tomar el mate recuperás el cuenco. El dulce de leche devuelve el balde cuando lo comés o cuando lo usás para preparar alfajores.

Hay 35 rellenos. Podés usar alimentos como bacalao, salmón, pollo, zanahoria, miel o estofado de conejo. La carne y el pescado con versión cocida aceptan cualquiera de las dos formas para el mismo relleno. También podés usar el pez directamente desde su balde. Cada relleno ocupa su propia pila. Las empanadas crudas también se apilan hasta 12 y se cocinan en 10 segundos en el horno común.

## Desarrollo

Con JDK 25, ejecutá `gradlew.bat build` en Windows o `./gradlew build` en Linux o macOS. El JAR queda en `build/libs`.

El catálogo de rellenos, ingredientes y efectos está en `src/main/resources/empanadas.tsv`. Para regenerar las recetas, traducciones, modelos y texturas después de modificar el catálogo, ejecutá `python3 tools/generar_recursos.py`.
