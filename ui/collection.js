"use strict";

const TRANSLATIONS = {
    fr: {
        "pageTitle": "PyCharting",
        "heading": "PyCharting",
        "footer.poweredBy": "Propulsé par Ubuntu, Python, NGINX, Let's Encrypt et Namecheap.",
        "footer.privacy": "Ce site ne conserve aucune donnée sur ses visiteurs.",
        "footer.copyright": "© SLCTI. Tous droits réservés.",
        "language": "Langue",
        "loading": "Chargement…",
        "count.one": "{visible} entrée",
        "count.other": "{visible} entrées",
        "empty": "Aucune entrée ne correspond à ces filtres.",
        "column.console": "Système",
        "column.title": "Titre",
        "column.owner": "Propriétaire",
        "column.region": "Standard",
        "column.quantity": "Quantité",
        "column.game": "Article",
        "column.manual": "Manuel",
        "column.box": "Boîte",
        "column.date": "Date",
        "column.paid": "Payé",
        "column.subtotal": "Valeur",
        "column.total": "Différence",
        "column.details": "Étiquettes",
        "column.actions": "Actions",
        "filter.search": "Rechercher un titre",
        "filter.all": "Tous",
        "filter.owned": "Oui",
        "filter.missing": "Non",
        "filter.one": "1",
        "filter.more": ">1",
        "filter.beforeToday": "Avant aujourd'hui",
        "filter.olderMonth": "Plus de 1 mois",
        "filter.olderHalfYear": "Plus de 6 mois",
        "filter.olderYear": "Plus de 1 an",
        "tags": "Étiquettes",
        "filter.reset": "Réinitialiser",
        "flag.console": "Console",
        "flag.gamepad": "Manette",
        "flag.virtual": "Virtuel",
        "flag.reproduction": "Reproduction",
        "flag.previously_owned": "Anciennement possédé",
        "flag.wishlist": "Liste de souhaits",
        "flag.amiibo": "amiibo",
        "flag.accessory": "Accessoire",
        "flag.damaged": "Endommagé",
        "flag.selling": "À vendre",
        "flag.buying": "À acheter",
        "priceChartingLink": "PriceCharting",
        "action.edit": "Modifier",
        "action.delete": "Supprimer",
        "action.add": "Ajouter",
        "action.priceCharting": "PriceCharting",
        "action.updatePrices": "Mettre à jour les prix et la date depuis PriceCharting",
        "editor.heading": "Modifier l'entrée",
        "editor.addHeading": "Ajouter une entrée",
        "editor.chooseConsole": "Choisir un système…",
        "editor.newConsole": "Nouveau système…",
        "editor.cancel": "Annuler",
        "editor.save": "Enregistrer",
        "action.logout": "Se déconnecter",
        "nav.home": "Accueil",
        "nav.users": "Utilisateurs",
        "help": "Aide",
        "legend.heading": "Légende",
        "legend.previouslyOwned": "« {tag} » : un article possédé pendant l'enfance, puis racheté.",
        "legend.totals": "Les entrées « {reproduction} », « {virtual} », « {damaged} » et « {wishlist} » ne comptent pas dans les totaux.",
        "role.administrator": "Administrateur",
        "role.collaborator": "Collaborateur (lecture seule)",
        "account": "{username} · {role}",
        "confirm.delete": "Supprimer « {title} » ({console}, {owner}) ?",
        "confirm.updateVisible": "Mettre à jour les prix et la date de {count} entrées visibles depuis PriceCharting, une après l'autre ?",
        "bulk.none": "Aucune entrée visible n'a d'Article, de Manuel ou de Boîte à mettre à jour.",
        "bulk.progress": "Mise à jour depuis PriceCharting : {done} sur {count}… Cliquez de nouveau sur le bouton PriceCharting pour arrêter.",
        "bulk.done": "Mise à jour terminée : {updated} sur {count} entrées.",
        "bulk.stopped": "Mise à jour arrêtée : {updated} sur {count} entrées.",
        "bulk.failed": "Non mises à jour : {titles}.",
        "action.stopUpdate": "Arrêter la mise à jour",
        "error.server": "Le serveur ne répond pas.",
        "error.missing": "Cette entrée n'existe plus. Rechargez la page.",
        "error.invalid": "Certaines valeurs sont invalides.",
        "error.status": "Erreur du serveur ({status}).",
        "error.read_only": "Votre compte est en lecture seule.",
        "error.nothing_owned": "« {title} » : aucune partie (Article, Manuel, Boîte) n'est remplie, il n'y a rien à mettre à jour.",
        "error.product_not_found": "« {title} » est introuvable sur PriceCharting. Ajoutez le lien PriceCharting de l'entrée, puis réessayez.",
        "error.pricecharting": "PriceCharting ne répond pas. Réessayez plus tard.",
        "error.exchange_rate": "Le taux de change USD → CAD de la Banque du Canada est introuvable. Réessayez plus tard."
    },
    en: {
        "pageTitle": "PyCharting",
        "heading": "PyCharting",
        "footer.poweredBy": "Powered by Ubuntu, Python, NGINX, Let's Encrypt and Namecheap.",
        "footer.privacy": "This site keeps no data about its visitors.",
        "footer.copyright": "© SLCTI. All rights reserved.",
        "language": "Language",
        "loading": "Loading…",
        "count.one": "{visible} entry",
        "count.other": "{visible} entries",
        "empty": "No entries match these filters.",
        "column.console": "System",
        "column.title": "Title",
        "column.owner": "Owner",
        "column.region": "Standard",
        "column.quantity": "Quantity",
        "column.game": "Item",
        "column.manual": "Manual",
        "column.box": "Box",
        "column.date": "Date",
        "column.paid": "Paid",
        "column.subtotal": "Value",
        "column.total": "Difference",
        "column.details": "Tags",
        "column.actions": "Actions",
        "filter.search": "Search for a title",
        "filter.all": "All",
        "filter.owned": "Yes",
        "filter.missing": "No",
        "filter.one": "1",
        "filter.more": ">1",
        "filter.beforeToday": "Before today",
        "filter.olderMonth": "Over 1 month",
        "filter.olderHalfYear": "Over 6 months",
        "filter.olderYear": "Over 1 year",
        "tags": "Tags",
        "filter.reset": "Reset",
        "flag.console": "Console",
        "flag.gamepad": "Controller",
        "flag.virtual": "Virtual",
        "flag.reproduction": "Reproduction",
        "flag.previously_owned": "Previously owned",
        "flag.wishlist": "Wishlist",
        "flag.amiibo": "amiibo",
        "flag.accessory": "Accessory",
        "flag.damaged": "Damaged",
        "flag.selling": "Selling",
        "flag.buying": "Buying",
        "priceChartingLink": "PriceCharting",
        "action.edit": "Edit",
        "action.delete": "Delete",
        "action.add": "Add",
        "action.priceCharting": "PriceCharting",
        "action.updatePrices": "Update prices and date from PriceCharting",
        "editor.heading": "Edit entry",
        "editor.addHeading": "Add an entry",
        "editor.chooseConsole": "Choose a system…",
        "editor.newConsole": "New system…",
        "editor.cancel": "Cancel",
        "editor.save": "Save",
        "action.logout": "Sign out",
        "nav.home": "Home",
        "nav.users": "Users",
        "help": "Help",
        "legend.heading": "Legend",
        "legend.previouslyOwned": "“{tag}”: an item owned as a child, then bought back.",
        "legend.totals": "“{reproduction}”, “{virtual}”, “{damaged}” and “{wishlist}” entries do not count in the totals.",
        "role.administrator": "Administrator",
        "role.collaborator": "Collaborator (read-only)",
        "account": "{username} · {role}",
        "confirm.delete": "Delete “{title}” ({console}, {owner})?",
        "confirm.updateVisible": "Update the prices and date of {count} visible entries from PriceCharting, one after the other?",
        "bulk.none": "No visible entry has an Item, Manual or Box to update.",
        "bulk.progress": "Updating from PriceCharting: {done} of {count}… Click the PriceCharting button again to stop.",
        "bulk.done": "Update finished: {updated} of {count} entries.",
        "bulk.stopped": "Update stopped: {updated} of {count} entries.",
        "bulk.failed": "Not updated: {titles}.",
        "action.stopUpdate": "Stop the update",
        "error.server": "The server is not responding.",
        "error.missing": "This entry no longer exists. Reload the page.",
        "error.invalid": "Some values are invalid.",
        "error.status": "Server error ({status}).",
        "error.read_only": "Your account is read-only.",
        "error.nothing_owned": "“{title}”: no part (Item, Manual, Box) is filled in, so there is nothing to update.",
        "error.product_not_found": "“{title}” was not found on PriceCharting. Add the entry's PriceCharting link, then try again.",
        "error.pricecharting": "PriceCharting is not responding. Try again later.",
        "error.exchange_rate": "The Bank of Canada's USD → CAD rate could not be found. Try again later."
    }
};
const LOCALES = { fr: "fr-CA", en: "en-CA" };
const LANGUAGE_STORAGE_KEY = "pycharting.language";
const VIEW_STORAGE_KEY = "pycharting.view";  // The filters and the sort, kept when the page is reloaded

const COLUMNS = [
    { key: "console" },
    { key: "title" },
    { key: "region" },
    { key: "quantity", numeric: true },
    { key: "game", numeric: true },
    { key: "manual", numeric: true },
    { key: "box", numeric: true },
    { key: "date" },
    { key: "subtotal", numeric: true },
    { key: "paid", numeric: true },
    { key: "total", numeric: true },
    { key: "details", sortable: false },
    { key: "owner" },
    { key: "actions", sortable: false }
];
const TAGS = ["console", "gamepad", "accessory", "amiibo", "virtual", "reproduction", "previously_owned", "damaged", "selling", "buying", "wishlist"];
const OWNERSHIP = ["game", "manual", "box"];
// Every price column: the ownership ones, then what was paid, which says nothing about what is owned
const PRICES = [...OWNERSHIP, "paid"];
const ROUTES = { item: "items", row: "rows" };
const ICONS = {
    edit: ["M12 20h9", "M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"],
    delete: ["M3 6h18", "M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2", "M19 6l-1 14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1L5 6", "M10 11v6", "M14 11v6"],
    add: ["M12 5v14", "M5 12h14"],
    reset: ["M18 6 6 18", "M6 6l12 12"],
    logout: ["M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4", "M16 17l5-5-5-5", "M21 12H9"],
    help: ["M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", "M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3", "M12 17h.01"]
};
const FILTER_IDS = ["filter-console", "filter-title", "filter-owner", "filter-region", "filter-quantity", "filter-game", "filter-manual", "filter-box", "filter-date", "filter-paid", "filter-attribute"];
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
let viewRestored = false;
let account = null;  // The signed-in account: { username, role }
let bulkUpdate = null;  // The update of every visible entry, while it runs

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
    document.querySelectorAll("[data-language]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.language === language)));
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
    renderAccount();
    renderLegend();
}

// Built from the tags' own names, so that the legend follows them when they are renamed
function renderLegend() {
    element("legend-previously-owned").textContent = t("legend.previouslyOwned", { tag: t("flag.previously_owned") });
    element("legend-totals").textContent = t("legend.totals", { reproduction: t("flag.reproduction"), virtual: t("flag.virtual"), damaged: t("flag.damaged"), wishlist: t("flag.wishlist") });
}

// Under the ? button, lined up on its right edge
function placeLegend(event) {
    if (event.newState !== "open") {
        return;
    }

    const button = element("help").getBoundingClientRect();
    const legend = element("legend");
    legend.style.top = `${button.bottom + 8}px`;
    legend.style.right = `${document.documentElement.clientWidth - button.right}px`;
}

// In alphabetical order for the language shown
function sortedTags(keys) {
    return [...keys].sort((left, right) => collator.compare(t(`flag.${left}`), t(`flag.${right}`)));
}

function normalize(text) {
    return String(text).normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();
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

// Sorted by what is shown: the price of every copy, with an X first among the owned
function ownershipSortValue(entry, key) {
    if (!isOwned(entry, key)) {
        return null;
    }

    return amountOf(entry, key) ?? 0;
}

// A price that can be added up: an X, or an empty value, has none
function priceNumber(entry, key) {
    if (!isOwned(entry, key)) {
        return null;
    }

    const number = Number(entry.values[key]);

    return Number.isNaN(number) ? null : number;
}

// A price for every copy, as shown: prices are stored and edited for one copy
function amountOf(entry, key) {
    const price = priceNumber(entry, key);

    return price === null ? null : price * entry.values.quantity;
}

// Item + Manual + Box, as shown
function subtotalOf(entry) {
    const parts = OWNERSHIP.map(key => amountOf(entry, key)).filter(amount => amount !== null);

    return parts.length ? parts.reduce((sum, amount) => sum + amount, 0) : null;
}

// Always Valeur less Payé, as both are shown; an empty value counts as 0
function totalOf(entry) {
    return (subtotalOf(entry) ?? 0) - (amountOf(entry, "paid") ?? 0);
}

const COMPUTED = { subtotal: subtotalOf, total: totalOf };

function sortValue(entry, key) {
    if (key === "quantity") {
        return entry.values.quantity;
    }

    if (key in COMPUTED) {
        return COMPUTED[key](entry);
    }

    // Sorted by what is shown: what was paid for every copy
    if (PRICES.includes(key)) {
        return ownershipSortValue(entry, key);
    }

    if (key === "date") {
        return entry.values.date || null;
    }

    if (key === "region") {
        return regionOf(entry);
    }

    if (key === "console") {
        return consoleName(entry);
    }

    return entry[key];
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

// How many months back each "older than" choice of the Date filter goes
const DATE_AGES = { beforeToday: 0, olderMonth: 1, olderHalfYear: 6, olderYear: 12 };

// Yes and No are about having a date; the other choices keep the dates older than that, and leave out entries without one
function dateMatches(entry, wanted) {
    const value = entry.values.date;

    if (wanted === "owned" || wanted === "missing") {
        return Boolean(value) === (wanted === "owned");
    }

    if (!value) {
        return false;
    }

    const cutoff = new Date();
    cutoff.setMonth(cutoff.getMonth() - DATE_AGES[wanted]);

    return value < isoDate(cutoff);
}

function visibleEntries() {
    const title = normalize(element("filter-title").value.trim());
    const owner = element("filter-owner").value;
    const console_ = element("filter-console").value;
    const region = element("filter-region").value;
    const quantity = element("filter-quantity").value;
    const date = element("filter-date").value;
    const attribute = element("filter-attribute").value;

    const ownership = PRICES.map(key => [key, element(`filter-${key}`).value]).filter(([, wanted]) => wanted);

    return entries
        .filter(entry => ownership.every(([key, wanted]) => isOwned(entry, key) === (wanted === "owned")))
        .filter(entry => !title || normalize(entry.title).includes(title))
        .filter(entry => !owner || entry.owner === owner)
        .filter(entry => !console_ || consoleName(entry) === console_)
        .filter(entry => !region || regionOf(entry) === region)
        .filter(entry => !date || dateMatches(entry, date))
        .filter(entry => !quantity || (quantity === "one" ? entry.values.quantity === 1 : entry.values.quantity > 1))
        .filter(entry => !attribute || tagMatches(entry, attribute))
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

// The price of every copy, so that each total is the sum of its column; an X stays as it is
function ownershipCell(entry, key) {
    const amount = amountOf(entry, key);

    if (amount === null) {
        return textCell(isOwned(entry, key) ? entry.values[key] : "", "number");
    }

    return amountCell(amount);
}

function amountCell(amount) {
    return textCell(amount === null ? "" : numberFormat.format(amount), "number");
}

// Green when the value is above what was paid, red when below
function differenceCell(amount) {
    const cell = amountCell(amount);
    setSign(cell, amount);

    return cell;
}

function setSign(node, amount) {
    node.classList.toggle("gain", amount > 0.005);
    node.classList.toggle("loss", amount < -0.005);
}

// Yes: at least one tag; No: none; otherwise, that one tag
function tagMatches(entry, wanted) {
    const tagged = TAGS.some(key => entry.values[key] === true);

    if (wanted === "any") {
        return tagged;
    }

    if (wanted === "none") {
        return !tagged;
    }

    return entry.values[wanted] === true;
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
    button.disabled = !canEdit();

    return button;
}

// The name opens PriceCharting
function titleCell(entry) {
    const cell = document.createElement("td");
    cell.className = "title";
    const link = document.createElement("a");
    link.href = priceChartingLink(entry);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.title = t("action.priceCharting");
    link.textContent = entry.title;
    cell.append(link);

    return cell;
}

// Refreshes Item, Manual and Box from PriceCharting, and dates them today
function priceChartingButton(entry) {
    const label = t("action.updatePrices");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "icon-button";
    button.title = t("action.priceCharting");
    button.setAttribute("aria-label", `${label} ${entry.title}`);
    button.disabled = !canEdit();
    const image = document.createElement("img");
    image.src = "/static/pricecharting.ico";
    image.alt = "";
    image.width = 16;
    image.height = 16;
    button.append(image);
    button.addEventListener("click", () => updatePrices(entry, button));

    return button;
}

async function updatePrices(entry, button) {
    button.disabled = true;
    button.classList.add("busy");

    try {
        await fetchPrices(entry);
        showMessage("");
    }
    catch (error) {
        showMessage(error.message);
        button.disabled = false;
        button.classList.remove("busy");
    }
}

// Asks the server to refresh an entry from PriceCharting, then shows what it saved right away
async function fetchPrices(entry) {
    const saved = await request(`/collection/${ROUTES[entry.kind]}/${entry.id}/prices`, { method: "POST" }, { title: entry.title });

    for (const key of [...OWNERSHIP, "date", "pricecharting"]) {
        entry.values[key] = saved[key];
    }

    render();
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
            titleCell(entry),
            textCell(regionOf(entry) ?? ""),
            textCell(entry.values.quantity, "number"),
            ...OWNERSHIP.map(key => ownershipCell(entry, key)),
            textCell(entry.values.date ?? "", "date"),
            amountCell(subtotalOf(entry)),
            ownershipCell(entry, "paid"),
            differenceCell(totalOf(entry)),
            detailsCell(entry),
            textCell(entry.owner),
            actions
        );
        rows.append(row);
    }
}

function render() {
    saveView();
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

// Tags whose entries stay out of the totals: not owned, or with no (or little) collector value
const UNCOUNTED_TAGS = ["wishlist", "reproduction", "virtual", "damaged"];

// Totals of the visible entries, except those with an uncounted tag; an X means owned, but has no price to add
function renderTotals(visible) {
    visible = visible.filter(entry => !UNCOUNTED_TAGS.some(key => entry.values[key]));
    element("total-quantity").textContent = visible.reduce((sum, entry) => sum + entry.values.quantity, 0);

    // Each total is the sum of its column as shown
    const columns = [...PRICES.map(key => [key, entry => amountOf(entry, key)]), ...Object.entries(COMPUTED)];

    for (const [key, amount] of columns) {
        const total = visible.reduce((sum, entry) => sum + (amount(entry) ?? 0), 0);
        element(`total-${key}`).textContent = numberFormat.format(total);

        if (key === "total") {
            setSign(element("total-total"), total);
        }
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
    fillSelect("filter-quantity", [["one", t("filter.one")], ["more", t("filter.more")]]);
    PRICES.forEach(key => fillSelect(`filter-${key}`, [["owned", t("filter.owned")], ["missing", t("filter.missing")]]));
    fillSelect("filter-date", [["owned", t("filter.owned")], ["missing", t("filter.missing")], ...Object.keys(DATE_AGES).map(age => [age, t(`filter.${age}`)])]);
    fillSelect("filter-attribute", [["any", t("filter.owned")], ["none", t("filter.missing")], ...sortedTags(TAGS).map(key => [key, t(`flag.${key}`)])]);
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

function showMessage(text, info = false) {
    element("message").textContent = text;
    element("message").hidden = !text;
    element("message").classList.toggle("info", info);
}

// The server explains some refusals with a code, which has its own message
async function errorCode(response) {
    try {
        const detail = (await response.json()).detail;

        return typeof detail === "string" && `error.${detail}` in TRANSLATIONS[language] ? `error.${detail}` : null;
    }
    catch {
        return null;
    }
}

async function request(url, options = {}, parameters = {}) {
    let response;

    try {
        response = await fetch(url, options);
    }
    catch {
        throw new Error(t("error.server"));
    }

    // The session has expired, or the account signed out elsewhere
    if (response.status === 401) {
        location.replace("/login");

        throw new Error(t("error.server"));
    }

    if (response.status === 404) {
        throw new Error(t("error.missing"));
    }

    if (!response.ok) {
        const code = await errorCode(response);

        if (code) {
            throw new Error(t(code, parameters));
        }

        throw new Error(response.status === 422 ? t("error.invalid") : t("error.status", { status: response.status }));
    }

    return response.json();
}

// Collaborators can only look: the buttons that change the collection stay visible, but disabled
function canEdit() {
    return account?.role === "administrator";
}

function renderAccount() {
    const name = account ? [account.first_name, account.last_name].filter(Boolean).join(" ") || account.username : "";
    element("account-name").textContent = account ? t("account", { username: name, role: t(`role.${account.role}`) }) : "";
    element("add").disabled = !canEdit();
    element("update-visible-prices").disabled = !canEdit();
    setLinkEnabled(element("nav-users"), canEdit());
}

// A link a collaborator cannot follow: visible, but disabled like the buttons
function setLinkEnabled(link, enabled) {
    if (enabled) {
        link.href = link.dataset.href ?? link.getAttribute("href");
        link.removeAttribute("aria-disabled");
    }
    else {
        link.dataset.href ??= link.getAttribute("href");
        link.removeAttribute("href");
        link.setAttribute("aria-disabled", "true");
    }
}

async function signOut() {
    try {
        await fetch("/auth/logout", { method: "POST" });
    }
    finally {
        location.replace("/login");
    }
}

async function loadEntries() {
    account ??= await request("/auth/me");
    renderAccount();
    entries = await request("/collection/entries");
    owners = await request("/collection/owners");
    fillFilters();

    // Only once the lists have their choices can the saved ones be selected again
    if (!viewRestored) {
        restoreView();
        viewRestored = true;
    }

    render();
}

function restoreView() {
    let saved;

    try {
        saved = JSON.parse(localStorage.getItem(VIEW_STORAGE_KEY));
    }
    catch {
        return;  // Storage can be unavailable or hold something else: start from the default view
    }

    for (const [id, value] of Object.entries(saved?.filters ?? {})) {
        const control = FILTER_IDS.includes(id) ? element(id) : null;

        // A choice that no longer exists, like a deleted owner, falls back to All
        if (control && (control.tagName !== "SELECT" || [...control.options].some(option => option.value === value))) {
            control.value = value;
        }
    }

    if (COLUMNS.some(column => column.key === saved?.sort?.key && column.sortable !== false) && [1, -1].includes(saved.sort.direction)) {
        sort = saved.sort;
    }
}

function saveView() {
    if (!viewRestored) {
        return;  // Saving before the saved view is back would erase it
    }

    try {
        localStorage.setItem(VIEW_STORAGE_KEY, JSON.stringify({ filters: Object.fromEntries(FILTER_IDS.map(id => [id, element(id).value])), sort }));
    }
    catch {
        // The view then only lasts until the page is reloaded
    }
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
            ...priceFields(entry.values),
            tagsField(TAGS, entry.values),
            selectField("owner_id", t("column.owner"), owners, entry.values.owner_id),
            field("pricecharting", t("priceChartingLink"), entry.values.pricecharting, { type: "url" })
        );
    }
    else {
        fields.append(
            consoleField("system", entry.console),
            field("title", t("column.title"), entry.title, { required: true }),
            regionField(regionOf(entry)),
            field("quantity", t("column.quantity"), entry.values.quantity, { type: "number", min: 0 }),
            ...priceFields(entry.values),
            tagsField(TAGS, entry.values),
            selectField("owner_id", t("column.owner"), owners, entry.values.owner_id),
            field("pricecharting", t("priceChartingLink"), entry.values.pricecharting, { type: "url" })
        );
    }

    element("editor").showModal();
}

// New entries start from the current filters, so adding to a filtered view stays visible
function openAddForm() {
    editing = null;
    const filteredOwner = owners.find(owner => owner.name === element("filter-owner").value);
    element("editor-heading").textContent = t("editor.addHeading");
    element("editor-error").hidden = true;
    element("editor-fields").replaceChildren(
        consoleField("group_name", storedConsoleName(element("filter-console").value) || null),
        field("name", t("column.title"), "", { required: true }),
        regionField(element("filter-region").value),
        field("quantity", t("column.quantity"), 1, { type: "number", min: 0 }),
        ...priceFields({}),
        tagsField(TAGS, {}),
        selectField("owner_id", t("column.owner"), owners, (filteredOwner ?? owners[0])?.id),
        field("pricecharting", t("priceChartingLink"), null, { type: "url" })
    );
    element("editor").showModal();
}

// Item, Manual and Box, the date of those prices, then what was paid
// Changing Item, Manual or Box dates the prices today; the date can still be changed afterwards
function priceFields(values) {
    const fields = PRICES.map(key => field(key, t(`column.${key}`), priceText(values[key])));
    const date = field("date", t("column.date"), values.date, { type: "date" });
    fields.splice(OWNERSHIP.length, 0, date);

    for (const wrapper of fields.slice(0, OWNERSHIP.length)) {
        wrapper.querySelector("input").addEventListener("input", () => date.querySelector("input").value = today());
    }

    return fields;
}

// Today in the viewer's time zone, as yyyy-mm-dd
function today() {
    return isoDate(new Date());
}

function isoDate(day) {
    return [day.getFullYear(), day.getMonth() + 1, day.getDate()].map(part => String(part).padStart(2, "0")).join("-");
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
            source: null,  // An entry keeps its source; a new one gets the owner's
            quantity: form.quantity.value === "" ? 1 : Number(form.quantity.value),
            date: form.date.value || null,
            pricecharting: form.pricecharting.value.trim() || null
        };

        for (const key of TAGS) {
            payload[key] = form[key].checked ? true : null;
        }

        for (const key of PRICES) {
            payload[key] = cellValue(form[key], values[key]);
        }

        return payload;
    }

    const payload = {
        system: choiceFieldValue(form, "system"),
        title: form.title.value,
        region: form.region.value || null,
        owner_id: Number(form.owner_id.value),
        source: null,
        quantity: form.quantity.value === "" ? 1 : Number(form.quantity.value),
        date: form.date.value || null,
        pricecharting: form.pricecharting.value.trim() || null
    };

    for (const key of TAGS) {
        payload[key] = form[key].checked ? true : null;
    }

    for (const key of PRICES) {
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

const BULK_PAUSE = 1000;  // Milliseconds between two entries, to go easy on PriceCharting

// Updates every visible entry that owns a part, one after the other; a second click stops after the current one
async function updateVisiblePrices() {
    const button = element("update-visible-prices");

    if (bulkUpdate) {
        bulkUpdate.stopped = true;

        return;
    }

    const targets = visibleEntries().filter(entry => OWNERSHIP.some(key => isOwned(entry, key)));

    if (!targets.length) {
        showMessage(t("bulk.none"), true);

        return;
    }

    if (!confirm(t("confirm.updateVisible", { count: targets.length }))) {
        return;
    }

    bulkUpdate = { stopped: false };
    button.classList.add("busy");
    button.title = t("action.stopUpdate");
    button.setAttribute("aria-label", button.title);
    const failed = [];
    let updated = 0;

    for (const [index, entry] of targets.entries()) {
        if (bulkUpdate.stopped) {
            break;
        }

        showMessage(t("bulk.progress", { done: index, count: targets.length }), true);

        try {
            await fetchPrices(entry);
            updated++;
        }
        catch {
            failed.push(entry.title);
        }

        if (index < targets.length - 1 && !bulkUpdate.stopped) {
            await new Promise(resolve => setTimeout(resolve, BULK_PAUSE));
        }
    }

    const summary = t(bulkUpdate.stopped ? "bulk.stopped" : "bulk.done", { updated, count: targets.length });
    bulkUpdate = null;
    button.classList.remove("busy");
    button.title = t("action.priceCharting");
    button.setAttribute("aria-label", button.title);

    showMessage(failed.length ? `${summary} ${t("bulk.failed", { titles: failed.join(", ") })}` : summary, !failed.length);
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

document.querySelectorAll("[data-language]").forEach(button => button.addEventListener("click", () => setLanguage(button.dataset.language, true)));
element("filters").addEventListener("input", render);
element("filter-reset").append(icon(ICONS.reset));
element("update-visible-prices").addEventListener("click", updateVisiblePrices);
element("filter-reset").addEventListener("click", () => {
    FILTER_IDS.forEach(id => element(id).value = "");
    render();
});
element("add").append(icon(ICONS.add));
element("logout").append(icon(ICONS.logout));
element("help").append(icon(ICONS.help));
element("legend").addEventListener("beforetoggle", placeLegend);
element("add").addEventListener("click", openAddForm);
element("logout").addEventListener("click", signOut);
element("editor-form").addEventListener("submit", saveEditor);
element("editor-cancel").addEventListener("click", () => element("editor").close());

setLanguage(initialLanguage());
loadEntries().catch(error => {
    loadFailed = true;
    render();
    showMessage(error.message);
});
