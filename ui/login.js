"use strict";

// The sign-in page, reached from the collection, which anyone may look at without an account
const TEXT = {
    fr: {
        "pageTitle": "PyCharting – Connexion",
        "heading": "PyCharting",
        "language": "Langue",
        "login.heading": "Connexion",
        "login.username": "Nom d'utilisateur",
        "login.password": "Mot de passe",
        "login.submit": "Se connecter",
        "login.back": "← Articles à vendre",
        "error.invalid_credentials": "Nom d'utilisateur ou mot de passe invalide.",
        "error.too_many_attempts": "Trop de tentatives. Réessayez dans 15 minutes.",
        "error.server": "Le serveur ne répond pas.",
        "footer.poweredBy": "Propulsé par Ubuntu, Python, NGINX, Let's Encrypt et Namecheap.",
        "footer.privacy": "Ce site ne conserve aucune donnée sur ses visiteurs.",
        "footer.copyright": "© SLCTI. Tous droits réservés."
    },
    en: {
        "pageTitle": "PyCharting – Sign in",
        "heading": "PyCharting",
        "language": "Language",
        "login.heading": "Sign in",
        "login.username": "Username",
        "login.password": "Password",
        "login.submit": "Sign in",
        "login.back": "← Items for sale",
        "error.invalid_credentials": "Invalid username or password.",
        "error.too_many_attempts": "Too many attempts. Try again in 15 minutes.",
        "error.server": "The server is not responding.",
        "footer.poweredBy": "Powered by Ubuntu, Python, NGINX, Let's Encrypt and Namecheap.",
        "footer.privacy": "This site keeps no data about its visitors.",
        "footer.copyright": "© SLCTI. All rights reserved."
    }
};
const LANGUAGE_STORAGE_KEY = "pycharting.language";  // Shared with the collection page

let language = "fr";

function setLanguage(value, remember = false) {
    language = value;
    document.documentElement.lang = language;
    document.title = TEXT[language].pageTitle;
    document.querySelectorAll("[data-language]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.language === language)));
    document.querySelectorAll("[data-i18n]").forEach(node => node.textContent = TEXT[language][node.dataset.i18n]);
    document.querySelectorAll("[data-i18n-label]").forEach(node => node.setAttribute("aria-label", TEXT[language][node.dataset.i18nLabel]));

    if (remember) {
        try {
            localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
        }
        catch {
            // The choice then only lasts until the page is reloaded
        }
    }
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

function showError(key) {
    const error = document.getElementById("login-error");
    error.textContent = TEXT[language][key];
    error.hidden = false;
}

async function signIn(event) {
    event.preventDefault();
    const form = event.target;
    const button = form.querySelector("button[type=submit]");
    button.disabled = true;
    document.getElementById("login-error").hidden = true;

    try {
        const response = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: form.username.value, password: form.password.value })
        });

        if (response.ok) {
            location.replace("/");

            return;
        }

        showError(response.status === 429 ? "error.too_many_attempts" : response.status === 401 ? "error.invalid_credentials" : "error.server");
        form.password.value = "";
        form.password.focus();
    }
    catch {
        showError("error.server");
    }

    button.disabled = false;
}

document.querySelectorAll("[data-language]").forEach(button => button.addEventListener("click", () => setLanguage(button.dataset.language, true)));
document.getElementById("login-form").addEventListener("submit", signIn);
setLanguage(initialLanguage());
