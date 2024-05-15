# Minecraft Block Renderer
Parses minecraft format json files to render and export blocks and items as they would appear in an inventory, works with mods!

## Summary
Minecraft uses a format called "Block Rendering" to display items and blocks in game. Instead of traditional 3D model files like .obj or .fbx, items in the world and the inventory reffer to a .json file which defines their shape using "Box Brushes", two corners of a rectangular prisim are defined per brush, by combining and rotating these brushes, the game can render shapes. This makes it diffacult to export images of 3D items as they appear in the inventory as no image file exists.

This project uses PyOpenGL and PyGame to parse through the json files and render them ortographically as they appear in game, it then exports the rendered view as an image to be used for whatever application you require. Use cases are maintaining wikis or working on other projects such CC-Overlord.

## Setup
The application is incomplete at this moment and requires a lengthy setup of extracting each modded .jar file you want to render items from. Usability will come after functionality. 