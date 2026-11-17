"use strict";

// The system names, shared by the collection and the Systems page.
// Full display names; the stored names stay as they are, because PriceCharting's URLs rely on them.
const CONSOLE_NAMES = {
    "3DS": "Nintendo 3DS",
    "Colecovision": "ColecoVision",
    "DS": "Nintendo DS",
    "GBA": "Nintendo Game Boy Advance",
    "GameBoy": "Nintendo Game Boy",
    "Gameboy": "Nintendo Game Boy",
    "Game Boy": "Nintendo Game Boy",
    "GameBoy Color": "Nintendo Game Boy Color",
    "Gameboy Color": "Nintendo Game Boy Color",
    "Game Boy Color": "Nintendo Game Boy Color",
    "GameCube": "Nintendo GameCube",
    "GameBoy Advance": "Nintendo Game Boy Advance",
    "Gameboy Advance": "Nintendo Game Boy Advance",
    "Game Boy Advance": "Nintendo Game Boy Advance",
    "Intellivision": "Mattel Intellivision",
    "Mini Arcade": "Arcade",
    "N64": "Nintendo 64",
    "NES": "Nintendo Entertainment System",
    "PSP": "Sony PlayStation Portable",
    "PlayStation": "Sony PlayStation",
    "Playstation": "Sony PlayStation",
    "PlayStation 2": "Sony PlayStation 2",
    "PlayStation 3": "Sony PlayStation 3",
    "PlayStation 4": "Sony PlayStation 4",
    "PlayStation 5": "Sony PlayStation 5",
    "PlayStation Vita": "Sony PlayStation Vita",
    "SNES": "Nintendo Super Nintendo | Super Famicom",
    "Super Famicom": "Nintendo Super Nintendo | Super Famicom",
    "Super Nintendo": "Nintendo Super Nintendo | Super Famicom",
    "Sega Genesis": "Sega Genesis | Mega Drive",
    "Sega Mega Drive": "Sega Genesis | Mega Drive",
    "Switch": "Nintendo Switch",
    "TI-99": "Texas Instruments TI-99",
    "Wii": "Nintendo Wii",
    "Wii U": "Nintendo Wii U",
    "Xbox 360": "Microsoft Xbox 360"
};

// The full name shown for a stored system name; one the map does not know shows as it is stored
function consoleDisplayName(stored) {
    return CONSOLE_NAMES[stored] ?? stored;
}
