// This file serves as a in-memory storage for
// last used route that can be fetched on login page
'use strict';

let urlRedirect = '';

export function setUrlRedirect(url: string): void {
    urlRedirect = url;
}

export function getUrlRedirect(): string {
    return urlRedirect;
}
