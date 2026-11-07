"use strict";

const TRANSLATIONS = {
    fr: {
        "pageTitle": "PyCharting",
        "heading": "PyCharting",
        "language": "Langue",
        "loading": "Chargement…",
        "count.one": "{visible} entrée",
        "count.other": "{visible} entrées",
        "empty": "Aucune entrée ne correspond à ces filtres.",
        "column.console": "Console",
        "column.title": "Jeu",
        "column.owner": "Propriétaire",
        "column.region": "Région",
        "column.quantity": "Quantité",
        "column.game": "Item",
        "column.manual": "Manuel",
        "column.box": "Boîte",
        "column.details": "Tags",
        "column.source": "Source",
        "column.actions": "Actions",
        "filter.search": "Rechercher un titre",
        "filter.all": "Tous",
        "filter.owned": "Oui",
        "filter.missing": "Non",
        "tags": "Tags",
        "filter.reset": "Réinitialiser",
        "flag.console": "Console",
        "flag.gamepad": "Manette",
        "flag.virtual": "Virtuel",
        "flag.reproduction": "Reproduction",
        "flag.previously_owned": "Anciennement possédé",
        "flag.wishlist": "Liste de souhaits",
        "flag.amiibo": "amiibo",
        "priceChartingLink": "PriceCharting",
        "action.edit": "Modifier",
        "action.delete": "Supprimer",
        "action.add": "Ajouter",
        "action.priceCharting": "PriceCharting",
        "editor.heading": "Modifier l'entrée",
        "editor.addHeading": "Ajouter une entrée",
        "editor.chooseConsole": "Choisir une console…",
        "editor.newConsole": "Nouvelle console…",
        "editor.autoSource": "Automatique",
        "editor.newSource": "Nouvelle source…",
        "editor.cancel": "Annuler",
        "editor.save": "Enregistrer",
        "confirm.delete": "Supprimer « {title} » ({console}, {owner}) ?",
        "error.server": "Le serveur ne répond pas.",
        "error.missing": "Cette entrée n'existe plus. Rechargez la page.",
        "error.invalid": "Certaines valeurs sont invalides.",
        "error.status": "Erreur du serveur ({status})."
    },
    en: {
        "pageTitle": "PyCharting",
        "heading": "PyCharting",
        "language": "Language",
        "loading": "Loading…",
        "count.one": "{visible} entry",
        "count.other": "{visible} entries",
        "empty": "No entries match these filters.",
        "column.console": "Console",
        "column.title": "Title",
        "column.owner": "Owner",
        "column.region": "Region",
        "column.quantity": "Quantity",
        "column.game": "Item",
        "column.manual": "Manual",
        "column.box": "Box",
        "column.details": "Tags",
        "column.source": "Source",
        "column.actions": "Actions",
        "filter.search": "Search for a title",
        "filter.all": "All",
        "filter.owned": "Yes",
        "filter.missing": "No",
        "tags": "Tags",
        "filter.reset": "Reset",
        "flag.console": "Console",
        "flag.gamepad": "Gamepad",
        "flag.virtual": "Virtual",
        "flag.reproduction": "Reproduction",
        "flag.previously_owned": "Previously owned",
        "flag.wishlist": "Wishlist",
        "flag.amiibo": "amiibo",
        "priceChartingLink": "PriceCharting",
        "action.edit": "Edit",
        "action.delete": "Delete",
        "action.add": "Add",
        "action.priceCharting": "PriceCharting",
        "editor.heading": "Edit entry",
        "editor.addHeading": "Add an entry",
        "editor.chooseConsole": "Choose a console…",
        "editor.newConsole": "New console…",
        "editor.autoSource": "Automatic",
        "editor.newSource": "New source…",
        "editor.cancel": "Cancel",
        "editor.save": "Save",
        "confirm.delete": "Delete “{title}” ({console}, {owner})?",
        "error.server": "The server is not responding.",
        "error.missing": "This entry no longer exists. Reload the page.",
        "error.invalid": "Some values are invalid.",
        "error.status": "Server error ({status})."
    }
};
const LOCALES = { fr: "fr-CA", en: "en-CA" };
const LANGUAGE_STORAGE_KEY = "pycharting.language";

const COLUMNS = [
    { key: "console" },
    { key: "title" },
    { key: "region" },
    { key: "quantity", numeric: true },
    { key: "game", numeric: true },
    { key: "manual", numeric: true },
    { key: "box", numeric: true },
    { key: "details", sortable: false },
    { key: "owner" },
    { key: "source" },
    { key: "actions", sortable: false }
];
const TAGS = ["console", "gamepad", "amiibo", "virtual", "reproduction", "previously_owned", "wishlist"];
const OWNERSHIP = ["game", "manual", "box"];
const ROUTES = { item: "items", row: "rows" };
const DATA_PREFIX = "pycharting/data/";
const ICONS = {
    edit: ["M12 20h9", "M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"],
    delete: ["M3 6h18", "M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2", "M19 6l-1 14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1L5 6", "M10 11v6", "M14 11v6"],
    add: ["M12 5v14", "M5 12h14"],
    reset: ["M18 6 6 18", "M6 6l12 12"]
};
const FILTER_IDS = ["filter-console", "filter-title", "filter-owner", "filter-region", "filter-game", "filter-manual", "filter-box", "filter-attribute", "filter-source"];
// Full display names; the stored names stay as they are, because PriceCharting's URLs rely on them
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
const PRICECHARTING_SEARCH = "https://www.pricecharting.com/search-products?type=prices&q=";
const NEW_VALUE = "new-value";
const REGIONS = ["NTSC", "PAL"];

const element = id => document.getElementById(id);

let language = "fr";
let collator;
let numberFormat;
let entries = null;
let owners = [];
let loadFailed = false;
let sort = { key: "console", direction: 1 };
let editing = null;

function t(key, parameters = {}) {
    return TRANSLATIONS[language][key].replace(/\{(\w+)\}/g, (_, name) => parameters[name]);
}

function initialLanguage() {
    try {
        const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);

        if (stored in TRANSLATIONS) {
            return stored;
        }
    }
    catch {
        // Storage can be unavailable; fall back to the browser's language
    }

    return navigator.language.toLowerCase().startsWith("fr") ? "fr" : "en";
}

function setLanguage(value, remember = false) {
    language = value;
    collator = new Intl.Collator(LOCALES[language], { numeric: true, sensitivity: "base" });
    numberFormat = new Intl.NumberFormat(LOCALES[language], { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    document.documentElement.lang = language;
    document.title = t("pageTitle");
    element("language").value = language;
    document.querySelectorAll("[data-i18n]").forEach(node => node.textContent = t(node.dataset.i18n));
    document.querySelectorAll("[data-i18n-placeholder]").forEach(node => node.placeholder = t(node.dataset.i18nPlaceholder));
    document.querySelectorAll("[data-i18n-label]").forEach(node => node.setAttribute("aria-label", t(node.dataset.i18nLabel)));
    document.querySelectorAll("[data-i18n-title]").forEach(node => {
        node.title = t(node.dataset.i18nTitle);
        node.setAttribute("aria-label", node.title);
    });

    if (remember) {
        try {
            localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
        }
        catch {
            // The choice then only lasts until the page is reloaded
        }
    }

    fillFilters();
    render();
}

// In alphabetical order for the language shown
function sortedTags(keys) {
    return [...keys].sort((left, right) => collator.compare(t(`flag.${left}`), t(`flag.${right}`)));
}

function normalize(text) {
    return String(text).normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();
}

function sourceLabel(entry) {
    return entry.source.replace(DATA_PREFIX, "");
}

function consoleName(entry) {
    return CONSOLE_NAMES[entry.console] ?? entry.console;
}

function regionOf(entry) {
    return entry.values.region ?? null;
}

// The stored link when one was verified, otherwise a search for that title on that console
function priceChartingLink(entry) {
    const url = entry.values.pricecharting;

    if (/^https?:\/\//i.test(url ?? "")) {
        return url;
    }

    return PRICECHARTING_SEARCH + encodeURIComponent(`${entry.title} ${entry.values.region === "PAL" ? "PAL " : ""}${entry.console}`);
}

// A value in Game, Manual or Box means that part is owned, even at 0 or with only an X
function isOwned(entry, key) {
    const value = entry.values[key];

    return value !== null && value !== "";
}

function ownershipSortValue(entry, key) {
    if (!isOwned(entry, key)) {
        return null;
    }

    const number = Number(entry.values[key]);

    return Number.isNaN(number) ? 0 : number;
}

function sortValue(entry, key) {
    if (key === "quantity") {
        return entry.values.quantity;
    }

    if (OWNERSHIP.includes(key)) {
        return ownershipSortValue(entry, key);
    }

    if (key === "region") {
        return regionOf(entry);
    }

    if (key === "console") {
        return consoleName(entry);
    }

    return key === "source" ? sourceLabel(entry) : entry[key];
}

function compare(left, right) {
    const a = sortValue(left, sort.key);
    const b = sortValue(right, sort.key);

    // Empty values stay last whichever way the column is sorted
    if (a === null || b === null) {
        if (a !== b) {
            return a === null ? 1 : -1;
        }
    }
    else {
        const order = typeof a === "number" ? a - b : collator.compare(a, b);

        if (order !== 0) {
            return order * sort.direction;
        }
    }

    return collator.compare(left.console, right.console) || collator.compare(left.title, right.title) || left.id - right.id;
}

function visibleEntries() {
    const title = normalize(element("filter-title").value.trim());
    const owner = element("filter-owner").value;
    const console_ = element("filter-console").value;
    const region = element("filter-region").value;
    const attribute = element("filter-attribute").value;
    const source = element("filter-source").value;

    const ownership = OWNERSHIP.map(key => [key, element(`filter-${key}`).value]).filter(([, wanted]) => wanted);

    return entries
        .filter(entry => ownership.every(([key, wanted]) => isOwned(entry, key) === (wanted === "owned")))
        .filter(entry => !title || normalize(entry.title).includes(title))
        .filter(entry => !owner || entry.owner === owner)
        .filter(entry => !console_ || consoleName(entry) === console_)
        .filter(entry => !region || regionOf(entry) === region)
        .filter(entry => !attribute || entry.values[attribute] === true)
        .filter(entry => !source || sourceLabel(entry) === source)
        .sort(compare);
}

function chip(text) {
    const span = document.createElement("span");
    span.className = "chip";
    span.textContent = text;

    return span;
}

function detailsCell(entry) {
    const cell = document.createElement("td");
    const chips = document.createElement("div");
    chips.className = "chips";

    for (const key of sortedTags(TAGS)) {
        if (entry.values[key]) {
            chips.append(chip(t(`flag.${key}`)));
        }
    }

    cell.append(chips);

    return cell;
}

function textCell(text, className = "") {
    const cell = document.createElement("td");
    cell.className = className;
    cell.textContent = text;

    return cell;
}

function ownershipCell(entry, key) {
    const value = entry.values[key];
    const number = Number(value);

    if (!isOwned(entry, key)) {
        return textCell("", "number");
    }

    return textCell(Number.isNaN(number) ? value : numberFormat.format(number), "number");
}

function icon(paths) {
    const namespace = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(namespace, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");

    for (const data of paths) {
        const path = document.createElementNS(namespace, "path");
        path.setAttribute("d", data);
        svg.append(path);
    }

    return svg;
}

function actionButton(action, entry, className, onClick) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.title = t(`action.${action}`);
    button.setAttribute("aria-label", `${t(`action.${action}`)} ${entry.title}`);
    button.append(icon(ICONS[action]));
    button.addEventListener("click", onClick);

    return button;
}

function priceChartingButton(entry) {
    const label = t("action.priceCharting");
    const link = document.createElement("a");
    link.className = "icon-button";
    link.href = priceChartingLink(entry);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.title = label;
    link.setAttribute("aria-label", `${label} ${entry.title}`);
    const image = document.createElement("img");
    image.src = "/static/pricecharting.ico";
    image.alt = "";
    image.width = 16;
    image.height = 16;
    link.append(image);

    return link;
}

function renderHeaders() {
    const headers = element("headers");
    headers.replaceChildren();

    for (const column of COLUMNS) {
        const header = document.createElement("th");
        const label = t(`column.${column.key}`);
        header.scope = "col";

        if (column.sortable === false) {
            const span = document.createElement("span");
            span.textContent = label;
            header.append(span);
        }
        else {
            const active = sort.key === column.key;
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = label + (active ? (sort.direction === 1 ? " ▲" : " ▼") : "");
            button.addEventListener("click", () => {
                sort = { key: column.key, direction: active ? -sort.direction : (column.numeric ? -1 : 1) };
                render();
            });
            header.setAttribute("aria-sort", active ? (sort.direction === 1 ? "ascending" : "descending") : "none");
            header.append(button);
        }

        headers.append(header);
    }
}

function renderRows(visible) {
    const rows = element("rows");
    rows.replaceChildren();

    if (!visible.length) {
        const row = document.createElement("tr");
        const cell = textCell(t("empty"), "empty");
        cell.colSpan = COLUMNS.length;
        row.append(cell);
        rows.append(row);

        return;
    }

    for (const entry of visible) {
        const row = document.createElement("tr");
        const actions = document.createElement("td");
        actions.className = "actions";
        actions.append(
            priceChartingButton(entry),
            actionButton("edit", entry, "icon-button", () => openEditor(entry)),
            actionButton("delete", entry, "icon-button danger", () => removeEntry(entry))
        );
        row.append(
            textCell(consoleName(entry)),
            textCell(entry.title, "title"),
            textCell(regionOf(entry) ?? ""),
            textCell(entry.values.quantity, "number"),
            ...OWNERSHIP.map(key => ownershipCell(entry, key)),
            detailsCell(entry),
            textCell(entry.owner),
            textCell(sourceLabel(entry), "source"),
            actions
        );
        rows.append(row);
    }
}

function render() {
    renderHeaders();

    if (entries === null) {
        element("count").textContent = loadFailed ? "" : t("loading");

        return;
    }

    const visible = visibleEntries();
    element("count").textContent = t(visible.length === 1 ? "count.one" : "count.other", { visible: visible.length });
    renderRows(visible);
    renderTotals(visible);
}

// Totals of the visible entries; an X means owned, but has no price to add
function renderTotals(visible) {
    element("total-quantity").textContent = visible.reduce((sum, entry) => sum + entry.values.quantity, 0);

    for (const key of OWNERSHIP) {
        const priced = visible.filter(entry => isOwned(entry, key) && !Number.isNaN(Number(entry.values[key])));
        const total = priced.reduce((sum, entry) => sum + Number(entry.values[key]) * entry.values.quantity, 0);
        element(`total-${key}`).textContent = numberFormat.format(total);
    }
}

function fillSelect(id, values) {
    const select = element(id);
    const selected = select.value;
    const first = select.options[0];
    select.replaceChildren(first);

    for (const [value, label] of values) {
        select.add(new Option(label, value));
    }

    // A deleted or renamed value falls back to the first option
    select.value = values.some(([value]) => value === selected) ? selected : "";
}

function fillFilters() {
    const all = entries ?? [];
    const unique = values => [...new Set(values)].sort(collator.compare).map(value => [value, value]);
    fillSelect("filter-owner", unique(all.map(entry => entry.owner)));
    fillSelect("filter-console", unique(all.map(consoleName)));
    fillSelect("filter-region", REGIONS.map(region => [region, region]));
    OWNERSHIP.forEach(key => fillSelect(`filter-${key}`, [["owned", t("filter.owned")], ["missing", t("filter.missing")]]));
    fillSelect("filter-source", unique(all.map(sourceLabel)));
    fillSelect("filter-attribute", sortedTags(TAGS).map(key => [key, t(`flag.${key}`)]));
}

// The stored name, not the display name, is what the crawler uses: pick the one most used for that console
function storedConsoleName(displayName) {
    const region = element("filter-region").value;
    const counts = new Map();

    for (const entry of entries) {
        if (consoleName(entry) === displayName && (!region || regionOf(entry) === region)) {
            counts.set(entry.console, (counts.get(entry.console) ?? 0) + 1);
        }
    }

    return [...counts].sort((left, right) => right[1] - left[1])[0]?.[0] ?? "";
}

function showMessage(text) {
    element("message").textContent = text;
    element("message").hidden = !text;
}

async function request(url, options = {}) {
    let response;

    try {
        response = await fetch(url, options);
    }
    catch {
        throw new Error(t("error.server"));
    }

    if (response.status === 404) {
        throw new Error(t("error.missing"));
    }

    if (!response.ok) {
        throw new Error(response.status === 422 ? t("error.invalid") : t("error.status", { status: response.status }));
    }

    return response.json();
}

async function loadEntries() {
    entries = await request("/collection/entries");
    owners = await request("/collection/owners");
    fillFilters();
    render();
}

function field(name, label, value, options = {}) {
    const wrapper = document.createElement("label");
    const input = document.createElement("input");
    input.name = name;
    input.value = value ?? "";
    input.required = options.required === true;
    input.type = options.type ?? "text";

    if (options.min !== undefined) {
        input.min = options.min;
    }

    wrapper.append(label, input);

    return wrapper;
}

function consoleLabel(stored) {
    return consoleName({ console: stored });
}

// One choice per console shown in the table. Each saves its most used stored name,
// except the entry's own console, which keeps the stored name it already has.
function consoleChoices(current) {
    const counts = new Map();

    for (const entry of entries) {
        counts.set(entry.console, (counts.get(entry.console) ?? 0) + 1);
    }

    const choices = new Map();

    for (const [stored] of [...counts].sort((left, right) => left[1] - right[1])) {
        choices.set(consoleLabel(stored), stored);
    }

    if (current) {
        choices.set(consoleLabel(current), current);
    }

    return [...choices].sort(([left], [right]) => collator.compare(left, right));
}

// A list of known values, plus a last choice that reveals a text box for a new one
function choiceField(name, label, choices, current, newLabel, required) {
    const wrapper = document.createElement("label");
    const select = document.createElement("select");
    select.name = name;
    select.required = required;

    for (const [text, value] of choices) {
        select.add(new Option(text, value));
    }

    select.add(new Option(newLabel, NEW_VALUE));
    select.value = current ?? "";
    const input = document.createElement("input");
    input.name = `${name}-${NEW_VALUE}`;
    input.hidden = true;
    input.placeholder = newLabel;
    input.setAttribute("aria-label", newLabel);
    select.addEventListener("change", () => {
        input.hidden = select.value !== NEW_VALUE;
        input.required = !input.hidden;

        if (!input.hidden) {
            input.focus();
        }
    });
    wrapper.append(label, select, input);

    return wrapper;
}

function choiceFieldValue(form, name) {
    return form[name].value === NEW_VALUE ? form[`${name}-${NEW_VALUE}`].value : form[name].value;
}

function consoleField(name, current) {
    const choices = [[t("editor.chooseConsole"), ""], ...consoleChoices(current)];

    return choiceField(name, t("column.console"), choices, current, t("editor.newConsole"), true);
}

function regionField(current) {
    const choices = [{ id: "", name: "" }, ...REGIONS.map(region => ({ id: region, name: region }))];

    return selectField("region", t("column.region"), choices, current ?? "");
}

// Only a new entry can start without a source: an existing one always shows the source it has
function sourceField(current, isNew) {
    const known = new Map(entries.map(entry => [entry.source, sourceLabel(entry)]));
    const choices = [...known].map(([value, label]) => [label, value]).sort(([left], [right]) => collator.compare(left, right));

    return choiceField("source", t("column.source"), isNew ? [[t("editor.autoSource"), ""], ...choices] : choices, current, t("editor.newSource"), false);
}

// An untouched source stays null, so the entry keeps following its source file
function sourceFieldValue(form) {
    const value = choiceFieldValue(form, "source").trim();

    return value === "" || value === editing?.source ? null : value;
}

function selectField(name, label, options, value) {
    const wrapper = document.createElement("label");
    const select = document.createElement("select");
    select.name = name;
    select.append(...options.map(option => new Option(option.name, option.id)));
    select.value = value;
    wrapper.append(label, select);

    return wrapper;
}

function checkbox(name, label, checked) {
    const wrapper = document.createElement("label");
    wrapper.className = "check";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.name = name;
    input.checked = checked === true;
    wrapper.append(input, label);

    return wrapper;
}

function tagsField(keys, values) {
    const wrapper = document.createElement("div");
    wrapper.className = "tags";
    wrapper.setAttribute("role", "group");
    const label = document.createElement("span");
    label.textContent = t("tags");
    const list = document.createElement("div");
    list.append(...sortedTags(keys).map(key => checkbox(key, t(`flag.${key}`), values[key])));
    wrapper.setAttribute("aria-label", t("tags"));
    wrapper.append(label, list);

    return wrapper;
}

function openEditor(entry) {
    editing = entry;
    const fields = element("editor-fields");
    element("editor-heading").textContent = t("editor.heading");
    element("editor-error").hidden = true;
    fields.replaceChildren();

    if (entry.kind === "item") {
        fields.append(
            consoleField("group_name", entry.console),
            field("name", t("column.title"), entry.title, { required: true }),
            regionField(regionOf(entry)),
            field("quantity", t("column.quantity"), entry.values.quantity, { type: "number", min: 0 }),
            ...OWNERSHIP.map(key => field(key, t(`column.${key}`), priceText(entry.values[key]))),
            tagsField(TAGS, entry.values),
            selectField("owner_id", t("column.owner"), owners, entry.values.owner_id),
            sourceField(entry.source, false),
            field("pricecharting", t("priceChartingLink"), entry.values.pricecharting, { type: "url" })
        );
    }
    else {
        fields.append(
            consoleField("system", entry.console),
            field("title", t("column.title"), entry.title, { required: true }),
            regionField(regionOf(entry)),
            field("quantity", t("column.quantity"), entry.values.quantity, { type: "number", min: 0 }),
            ...OWNERSHIP.map(key => field(key, t(`column.${key}`), priceText(entry.values[key]))),
            tagsField(TAGS, entry.values),
            selectField("owner_id", t("column.owner"), owners, entry.values.owner_id),
            sourceField(entry.source, false),
            field("pricecharting", t("priceChartingLink"), entry.values.pricecharting, { type: "url" })
        );
    }

    element("editor").showModal();
}

// New entries start from the current filters, so adding to a filtered view stays visible
function openAddForm() {
    editing = null;
    const filteredOwner = owners.find(owner => owner.name === element("filter-owner").value);
    const filteredSource = entries.find(entry => sourceLabel(entry) === element("filter-source").value)?.source;
    element("editor-heading").textContent = t("editor.addHeading");
    element("editor-error").hidden = true;
    element("editor-fields").replaceChildren(
        consoleField("group_name", storedConsoleName(element("filter-console").value) || null),
        field("name", t("column.title"), "", { required: true }),
        regionField(element("filter-region").value),
        field("quantity", t("column.quantity"), 1, { type: "number", min: 0 }),
        ...OWNERSHIP.map(key => field(key, t(`column.${key}`), null)),
        tagsField(TAGS, {}),
        selectField("owner_id", t("column.owner"), owners, (filteredOwner ?? owners[0])?.id),
        sourceField(filteredSource, true),
        field("pricecharting", t("priceChartingLink"), null, { type: "url" })
    );
    element("editor").showModal();
}

// A price as shown in the form: always two decimals, and without thousands separators so it stays editable
function priceText(value) {
    if (value === null || value === undefined || value === "") {
        return "";
    }

    const number = Number(value);

    return Number.isNaN(number) ? String(value) : new Intl.NumberFormat(LOCALES[language], { minimumFractionDigits: 2, maximumFractionDigits: 2, useGrouping: false }).format(number);
}

// Keeps the stored value when a field is untouched, otherwise reads numbers as numbers
function cellValue(input, original) {
    const text = input.value.trim();

    if (text === priceText(original)) {
        return original ?? null;
    }

    if (text === "") {
        return null;
    }

    const number = Number(text.replace(",", "."));

    return Number.isNaN(number) ? text : number;
}

function editorPayload() {
    const form = element("editor-form").elements;
    const values = editing?.values ?? {};

    if (editing === null || editing.kind === "item") {
        const payload = {
            group_name: choiceFieldValue(form, "group_name"),
            name: form.name.value,
            region: form.region.value || null,
            owner_id: Number(form.owner_id.value),
            source: sourceFieldValue(form),
            quantity: form.quantity.value === "" ? 1 : Number(form.quantity.value),
            pricecharting: form.pricecharting.value.trim() || null
        };

        for (const key of TAGS) {
            payload[key] = form[key].checked ? true : null;
        }

        for (const key of OWNERSHIP) {
            payload[key] = cellValue(form[key], values[key]);
        }

        return payload;
    }

    const payload = {
        system: choiceFieldValue(form, "system"),
        title: form.title.value,
        region: form.region.value || null,
        owner_id: Number(form.owner_id.value),
        source: sourceFieldValue(form),
        quantity: form.quantity.value === "" ? 1 : Number(form.quantity.value),
        pricecharting: form.pricecharting.value.trim() || null
    };

    for (const key of TAGS) {
        payload[key] = form[key].checked ? true : null;
    }

    for (const key of OWNERSHIP) {
        payload[key] = cellValue(form[key], values[key]);
    }

    return payload;
}

async function saveEditor(event) {
    event.preventDefault();

    try {
        await request(editing === null ? "/collection/items" : `/collection/${ROUTES[editing.kind]}/${editing.id}`, {
            method: editing === null ? "POST" : "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(editorPayload())
        });
        element("editor").close();
        showMessage("");
        await loadEntries();
    }
    catch (error) {
        if (element("editor").open) {
            element("editor-error").textContent = error.message;
            element("editor-error").hidden = false;
        }
        else {
            showMessage(error.message);
        }
    }
}

async function removeEntry(entry) {
    if (!confirm(t("confirm.delete", { title: entry.title, console: entry.console, owner: entry.owner }))) {
        return;
    }

    try {
        await request(`/collection/${ROUTES[entry.kind]}/${entry.id}`, { method: "DELETE" });
        showMessage("");
        await loadEntries();
    }
    catch (error) {
        showMessage(error.message);
    }
}

element("language").addEventListener("change", event => setLanguage(event.target.value, true));
element("filters").addEventListener("input", render);
element("filter-reset").append(icon(ICONS.reset));
element("filter-reset").addEventListener("click", () => {
    FILTER_IDS.forEach(id => element(id).value = "");
    render();
});
element("add").append(icon(ICONS.add));
element("add").addEventListener("click", openAddForm);
element("editor-form").addEventListener("submit", saveEditor);
element("editor-cancel").addEventListener("click", () => element("editor").close());

setLanguage(initialLanguage());
loadEntries().catch(error => {
    loadFailed = true;
    render();
    showMessage(error.message);
});
