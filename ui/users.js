"use strict";

// The Users page: administrators see, add, change and delete the accounts
const TEXT = {
    fr: {
        "pageTitle": "PyCharting – Utilisateurs",
        "heading": "PyCharting",
        "language": "Langue",
        "nav.home": "Accueil",
        "nav.users": "Utilisateurs",
        "action.logout": "Se déconnecter",
        "action.add": "Ajouter",
        "action.save": "Enregistrer",
        "action.delete": "Supprimer",
        "account": "{username} · {role}",
        "you": "{username} (vous)",
        "role.administrator": "Administrateur",
        "role.collaborator": "Collaborateur (lecture seule)",
        "role.buyer": "Acheteur (articles à vendre)",
        "column.username": "Nom d'utilisateur",
        "column.firstName": "Prénom",
        "column.lastName": "Nom",
        "column.role": "Rôle",
        "column.password": "Nouveau mot de passe",
        "column.actions": "Actions",
        "new.username": "Nouveau compte",
        "new.password": "8 caractères ou plus",
        "unchanged": "Inchangé",
        "confirm.delete": "Supprimer le compte « {username} » ?",
        "saved": "« {username} » est enregistré.",
        "added": "« {username} » est ajouté.",
        "deleted": "« {username} » est supprimé.",
        "error.user_exists": "Ce nom d'utilisateur existe déjà.",
        "error.self": "Vous ne pouvez ni retirer votre propre rôle d'administrateur ni supprimer votre compte.",
        "error.read_only": "Seuls les administrateurs peuvent gérer les comptes.",
        "error.invalid": "Un nom et un mot de passe de 8 caractères ou plus sont requis.",
        "error.nothing": "Rien n'a changé pour ce compte.",
        "error.missing": "Ce compte n'existe plus. Rechargez la page.",
        "error.server": "Le serveur ne répond pas.",
        "error.status": "Erreur du serveur ({status}).",
        "footer.poweredBy": "Propulsé par Ubuntu, Python, NGINX, Let's Encrypt et Namecheap.",
        "footer.privacy": "Ce site ne conserve aucune donnée sur ses visiteurs.",
        "footer.copyright": "© SLCTI. Tous droits réservés."
    },
    en: {
        "pageTitle": "PyCharting – Users",
        "heading": "PyCharting",
        "language": "Language",
        "nav.home": "Home",
        "nav.users": "Users",
        "action.logout": "Sign out",
        "action.add": "Add",
        "action.save": "Save",
        "action.delete": "Delete",
        "account": "{username} · {role}",
        "you": "{username} (you)",
        "role.administrator": "Administrator",
        "role.collaborator": "Collaborator (read-only)",
        "role.buyer": "Buyer (items for sale)",
        "column.username": "Username",
        "column.firstName": "First name",
        "column.lastName": "Last name",
        "column.role": "Role",
        "column.password": "New password",
        "column.actions": "Actions",
        "new.username": "New account",
        "new.password": "8 characters or more",
        "unchanged": "Unchanged",
        "confirm.delete": "Delete the account “{username}”?",
        "saved": "“{username}” is saved.",
        "added": "“{username}” is added.",
        "deleted": "“{username}” is deleted.",
        "error.user_exists": "This username already exists.",
        "error.self": "You can neither remove your own administrator role nor delete your own account.",
        "error.read_only": "Only administrators can manage the accounts.",
        "error.invalid": "A name and a password of 8 characters or more are required.",
        "error.nothing": "Nothing changed for this account.",
        "error.missing": "This account no longer exists. Reload the page.",
        "error.server": "The server is not responding.",
        "error.status": "Server error ({status}).",
        "footer.poweredBy": "Powered by Ubuntu, Python, NGINX, Let's Encrypt and Namecheap.",
        "footer.privacy": "This site keeps no data about its visitors.",
        "footer.copyright": "© SLCTI. All rights reserved."
    }
};
const LANGUAGE_STORAGE_KEY = "pycharting.language";  // Shared with the other pages
const ROLES = ["administrator", "collaborator", "buyer"];
const ICONS = {
    add: ["M12 5v14", "M5 12h14"],
    save: ["M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z", "M17 21v-8H7v8", "M7 3v5h8"],
    delete: ["M3 6h18", "M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2", "M19 6l-1 14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1L5 6", "M10 11v6", "M14 11v6"],
    logout: ["M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4", "M16 17l5-5-5-5", "M21 12H9"]
};

const element = id => document.getElementById(id);

let language = "fr";
let account = null;  // The signed-in administrator: { id, username, role }
let users = [];

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

    renderAccount();
    renderUsers();
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

function textInput(value, label) {
    const input = document.createElement("input");
    input.value = value ?? "";
    input.maxLength = 100;
    input.autocomplete = "off";
    input.setAttribute("aria-label", label);

    return input;
}

function roleSelect(current, disabled) {
    const select = document.createElement("select");
    select.setAttribute("aria-label", t("column.role"));
    select.disabled = disabled;

    for (const role of ROLES) {
        select.add(new Option(t(`role.${role}`), role));
    }

    select.value = current;

    return select;
}

function iconButton(action, label, className, onClick, disabled = false) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.title = t(`action.${action}`);
    button.setAttribute("aria-label", `${t(`action.${action}`)} ${label}`);
    button.append(icon(ICONS[action]));
    button.disabled = disabled;
    button.addEventListener("click", onClick);

    return button;
}

function cell(...children) {
    const td = document.createElement("td");
    td.append(...children);

    return td;
}

// One row per account; administrators cannot demote or delete themselves
function renderUsers() {
    const body = element("users");
    body.replaceChildren();

    for (const user of users) {
        const self = user.id === account?.id;
        const firstName = textInput(user.first_name, `${t("column.firstName")} ${user.username}`);
        const lastName = textInput(user.last_name, `${t("column.lastName")} ${user.username}`);
        const role = roleSelect(user.role, self);
        const password = document.createElement("input");
        password.type = "password";
        password.autocomplete = "new-password";
        password.minLength = 8;
        password.placeholder = t("unchanged");
        password.setAttribute("aria-label", `${t("column.password")} ${user.username}`);
        const actions = cell(
            iconButton("save", user.username, "icon-button", () => saveUser(user, firstName, lastName, role, password)),
            iconButton("delete", user.username, "icon-button danger", () => deleteUser(user), self)
        );
        actions.className = "actions";
        const row = document.createElement("tr");
        row.append(cell(self ? t("you", { username: user.username }) : user.username), cell(firstName), cell(lastName), cell(role), cell(password), actions);
        body.append(row);
    }
}

async function loadUsers() {
    users = await request("/accounts");
    renderUsers();
}

async function saveUser(user, firstName, lastName, role, password) {
    const change = {};

    if (firstName.value.trim() !== (user.first_name ?? "") || lastName.value.trim() !== (user.last_name ?? "")) {
        change.first_name = firstName.value.trim();
        change.last_name = lastName.value.trim();
    }

    if (role.value !== user.role) {
        change.role = role.value;
    }

    if (password.value) {
        change.password = password.value;
    }

    if (!Object.keys(change).length) {
        showMessage(t("error.nothing"));

        return;
    }

    try {
        await request(`/accounts/${user.id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(change) });

        // One's own name also shows in the header
        if (user.id === account.id) {
            account = await request("/auth/me");
            renderAccount();
        }

        await loadUsers();
        showMessage(t("saved", { username: user.username }), true);
    }
    catch (error) {
        showMessage(error.message);
    }
}

async function deleteUser(user) {
    if (!confirm(t("confirm.delete", { username: user.username }))) {
        return;
    }

    try {
        await request(`/accounts/${user.id}`, { method: "DELETE" });
        await loadUsers();
        showMessage(t("deleted", { username: user.username }), true);
    }
    catch (error) {
        showMessage(error.message);
    }
}

async function addUser() {
    const row = element("new-user");
    const username = row.querySelector("[name=username]");
    const firstName = row.querySelector("[name=first_name]");
    const lastName = row.querySelector("[name=last_name]");
    const role = row.querySelector("[name=role]");
    const password = row.querySelector("[name=password]");

    if (!username.value.trim() || password.value.length < 8) {
        showMessage(t("error.invalid"));

        return;
    }

    try {
        await request("/accounts", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username: username.value.trim(), first_name: firstName.value.trim(), last_name: lastName.value.trim(), role: role.value, password: password.value }) });
        showMessage(t("added", { username: username.value.trim() }), true);
        username.value = "";
        firstName.value = "";
        lastName.value = "";
        password.value = "";
        role.value = "collaborator";
        await loadUsers();
    }
    catch (error) {
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
element("logout").append(icon(ICONS.logout));
element("logout").addEventListener("click", signOut);
element("add-user").append(icon(ICONS.add));
element("add-user").addEventListener("click", addUser);
setLanguage(initialLanguage());

(async () => {
    try {
        account = await request("/auth/me");
        renderAccount();
        await loadUsers();
    }
    catch (error) {
        showMessage(error.message);
    }
})();
