"use strict";

// The Systems page: administrators rename the systems the collection stores
const TEXT = {
    fr: {
        "pageTitle": "PyCharting – Systèmes",
        "heading": "PyCharting",
        "language": "Langue",
        "nav.home": "Accueil",
        "nav.systems": "Systèmes",
        "nav.users": "Utilisateurs",
        "action.logout": "Se déconnecter",
        "action.save": "Enregistrer",
        "account": "{username} · {role}",
        "role.administrator": "Administrateur",
        "role.collaborator": "Collaborateur",
        "column.system": "Système",
        "column.displayed": "Affiché",
        "column.entries": "Entrées",
        "column.pricecharting": "PriceCharting",
        "column.actions": "Actions",
        "entries": "{items} article(s), {rows} ligne(s)",
        "known": "Connu",
        "unknown": "Inconnu",
        "known.title": "PriceCharting connaît ce nom : les prix de ses entrées viennent de sa page de console.",
        "unknown.title": "PriceCharting ne connaît pas ce nom : les prix de ses entrées viennent d'une simple recherche.",
        "hint": "Renommer un système renomme toutes ses entrées. Lui donner un nom déjà utilisé réunit les deux. Le nom est ce qui est demandé à PriceCharting : un nom qu'il ne connaît pas laisse ses entrées à une simple recherche.",
        "confirm.rename": "Renommer « {current} » en « {name} » ? {count} entrée(s) changent.",
        "confirm.merge": "« {name} » existe déjà. Réunir « {current} » avec lui ? {count} entrée(s) changent.",
        "renamed": "{count} entrée(s) sont maintenant sous « {name} ».",
        "error.unchanged": "Ce nom est déjà celui du système.",
        "error.read_only": "Seuls les administrateurs peuvent renommer les systèmes.",
        "error.invalid": "Un nom est requis.",
        "error.missing": "Ce système n'existe plus. Rechargez la page.",
        "error.server": "Le serveur ne répond pas.",
        "error.status": "Erreur du serveur ({status}).",
        "footer.poweredBy": "Propulsé par Ubuntu, Python, NGINX, Let's Encrypt et Namecheap.",
        "footer.privacy": "Ce site ne conserve aucune donnée sur ses visiteurs.",
        "footer.copyright": "© SLCTI. Tous droits réservés."
    },
    en: {
        "pageTitle": "PyCharting – Systems",
        "heading": "PyCharting",
        "language": "Language",
        "nav.home": "Home",
        "nav.systems": "Systems",
        "nav.users": "Users",
        "action.logout": "Sign out",
        "action.save": "Save",
        "account": "{username} · {role}",
        "role.administrator": "Administrator",
        "role.collaborator": "Collaborator",
        "column.system": "System",
        "column.displayed": "Shown as",
        "column.entries": "Entries",
        "column.pricecharting": "PriceCharting",
        "column.actions": "Actions",
        "entries": "{items} item(s), {rows} row(s)",
        "known": "Known",
        "unknown": "Unknown",
        "known.title": "PriceCharting knows this name: its entries are priced from its console page.",
        "unknown.title": "PriceCharting does not know this name: its entries are priced from a plain search.",
        "hint": "Renaming a system renames every one of its entries. Giving it a name already in use brings the two together. The name is what PriceCharting is asked about: one it does not know leaves its entries to a plain search.",
        "confirm.rename": "Rename “{current}” to “{name}”? {count} entry/entries change.",
        "confirm.merge": "“{name}” already exists. Bring “{current}” together with it? {count} entry/entries change.",
        "renamed": "{count} entry/entries are now under “{name}”.",
        "error.unchanged": "This is already the system's name.",
        "error.read_only": "Only administrators can rename the systems.",
        "error.invalid": "A name is required.",
        "error.missing": "This system no longer exists. Reload the page.",
        "error.server": "The server is not responding.",
        "error.status": "Server error ({status}).",
        "footer.poweredBy": "Powered by Ubuntu, Python, NGINX, Let's Encrypt and Namecheap.",
        "footer.privacy": "This site keeps no data about its visitors.",
        "footer.copyright": "© SLCTI. All rights reserved."
    }
};
const LANGUAGE_STORAGE_KEY = "pycharting.language";  // Shared with the other pages
const ICONS = {
    save: ["M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z", "M17 21v-8H7v8", "M7 3v5h8"],
    home: ["M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z", "M9 22V12h6v10"],
    // A screen on its stand: the system an entry is played on
    systems: ["M3 4h18a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Z", "M12 16v4", "M8 20h8"],
    users: ["M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2", "M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z"],
    logout: ["M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4", "M16 17l5-5-5-5", "M21 12H9"]
};

const element = id => document.getElementById(id);

let language = "fr";
let collator;
let account = null;  // The signed-in administrator: { id, username, role }
let systems = [];

function t(key, parameters = {}) {
    return TEXT[language][key].replace(/\{(\w+)\}/g, (_, name) => parameters[name]);
}

function initialLanguage() {
    try {
        const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);

        if (stored in TEXT) {
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
    collator = new Intl.Collator(language, { sensitivity: "base", numeric: true });
    document.documentElement.lang = language;
    document.title = t("pageTitle");
    document.querySelectorAll("[data-language]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.language === language)));
    document.querySelectorAll("[data-i18n]").forEach(node => node.textContent = t(node.dataset.i18n));
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

    renderAccount();
    renderSystems();
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

function showMessage(text, info = false) {
    element("message").textContent = text;
    element("message").hidden = !text;
    element("message").classList.toggle("info", info);
}

// The server explains its refusals with a code, which has its own message
async function request(url, options = {}) {
    let response;

    try {
        response = await fetch(url, options);
    }
    catch {
        throw new Error(t("error.server"));
    }

    if (response.status === 401) {
        location.replace("/login");

        throw new Error(t("error.server"));
    }

    if (!response.ok) {
        let detail = null;

        try {
            detail = (await response.json()).detail;
        }
        catch {
            // No explanation: the status says enough
        }

        const key = typeof detail === "string" && `error.${detail}` in TEXT[language] ? `error.${detail}` : response.status === 404 ? "error.missing" : response.status === 422 ? "error.invalid" : null;

        throw new Error(key ? t(key) : t("error.status", { status: response.status }));
    }

    return response.json();
}

// The person's name when it is known, otherwise the username
function displayName(user) {
    return [user.first_name, user.last_name].filter(Boolean).join(" ") || user.username;
}

function renderAccount() {
    element("account-name").textContent = account ? t("account", { username: displayName(account), role: t(`role.${account.role}`) }) : "";
}

function cell(...children) {
    const td = document.createElement("td");
    td.append(...children);

    return td;
}

function textCell(text) {
    return cell(document.createTextNode(text));
}

function nameInput(system) {
    const input = document.createElement("input");
    input.value = system.name;
    input.maxLength = 100;
    input.autocomplete = "off";
    input.autocapitalize = "none";
    input.spellcheck = false;
    input.setAttribute("aria-label", `${t("column.system")} ${system.name}`);

    return input;
}

// Whether PriceCharting knows the name, which decides how the prices of its entries are found
function pricechartingCell(system) {
    const span = document.createElement("span");
    span.className = system.pricecharting ? "known" : "unknown";
    span.textContent = system.pricecharting ? t("known") : t("unknown");
    span.title = system.pricecharting ? t("known.title") : t("unknown.title");

    return cell(span);
}

function saveButton(system, input) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "icon-button";
    button.title = t("action.save");
    button.setAttribute("aria-label", `${t("action.save")} ${system.name}`);
    button.append(icon(ICONS.save));
    button.addEventListener("click", () => renameSystem(system, input));

    return button;
}

// One row per system name the collection stores, next to the name the collection shows for it
function renderSystems() {
    const body = element("systems");
    body.replaceChildren();

    for (const system of systems) {
        const input = nameInput(system);
        const actions = cell(saveButton(system, input));
        actions.className = "actions";
        const row = document.createElement("tr");
        row.append(
            cell(input),
            textCell(consoleDisplayName(system.name)),  // consoles.js, shared with the collection
            textCell(t("entries", { items: system.items, rows: system.rows })),
            pricechartingCell(system),
            actions
        );
        body.append(row);
    }
}

async function loadSystems() {
    systems = await request("/collection/systems");
    systems.sort((left, right) => collator.compare(left.name, right.name));
    renderSystems();
}

async function renameSystem(system, input) {
    const name = input.value.trim();

    if (!name) {
        showMessage(t("error.invalid"));

        return;
    }

    if (name === system.name) {
        showMessage(t("error.unchanged"));

        return;
    }

    const count = system.items + system.rows;
    const merging = systems.some(other => other !== system && other.name === name);

    if (!confirm(t(merging ? "confirm.merge" : "confirm.rename", { current: system.name, name, count }))) {
        return;
    }

    try {
        const result = await request("/collection/systems", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ current: system.name, name }) });
        await loadSystems();
        showMessage(t("renamed", { count: result.entries, name }), true);
    }
    catch (error) {
        input.value = system.name;
        showMessage(error.message);
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

document.querySelectorAll("[data-language]").forEach(button => button.addEventListener("click", () => setLanguage(button.dataset.language, true)));
element("nav-home").append(icon(ICONS.home));
element("nav-systems").append(icon(ICONS.systems));
element("nav-users").append(icon(ICONS.users));
element("logout").append(icon(ICONS.logout));
element("logout").addEventListener("click", signOut);
setLanguage(initialLanguage());

(async () => {
    try {
        account = await request("/auth/me");
        renderAccount();
        await loadSystems();
    }
    catch (error) {
        showMessage(error.message);
    }
})();
