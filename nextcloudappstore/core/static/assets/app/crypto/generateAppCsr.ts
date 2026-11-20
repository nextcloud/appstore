/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import 'reflect-metadata';
import * as x509 from '@peculiar/x509';

const APP_ID_PATTERN = /^[a-z_]+$/;

export class InvalidAppIdError extends Error {
    constructor(appId: string) {
        super(
            `Invalid app id "${appId}": must contain only lowercase ASCII letters and underscores`,
        );
        this.name = 'InvalidAppIdError';
    }
}

export interface AppKeyAndCsr {
    appId: string;
    privateKeyPem: string;
    csrPem: string;
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

function toPem(buffer: ArrayBuffer, label: string): string {
    const b64 = arrayBufferToBase64(buffer);
    const lines = b64.match(/.{1,64}/g) || [];
    return `-----BEGIN ${label}-----\n${lines.join('\n')}\n-----END ${label}-----\n`;
}

export function isValidAppId(appId: string): boolean {
    return APP_ID_PATTERN.test(appId);
}

/**
 * Generates an RSA-4096 key and PKCS#10 CSR equivalent to:
 * openssl req -nodes -newkey rsa:4096 -keyout APP_ID.key -out APP_ID.csr -subj "/CN=APP_ID"
 */
export async function generateAppCsr(appId: string): Promise<AppKeyAndCsr> {
    if (!isValidAppId(appId)) {
        throw new InvalidAppIdError(appId);
    }

    const alg: RsaHashedKeyGenParams = {
        name: 'RSASSA-PKCS1-v1_5',
        hash: 'SHA-256',
        publicExponent: new Uint8Array([1, 0, 1]),
        modulusLength: 4096,
    };

    const keys = await crypto.subtle.generateKey(alg, true, ['sign', 'verify']);
    const csr = await x509.Pkcs10CertificateRequestGenerator.create({
        name: `CN=${appId}`,
        keys,
        signingAlgorithm: alg,
    });

    const pkcs8 = await crypto.subtle.exportKey('pkcs8', keys.privateKey);
    return {
        appId,
        privateKeyPem: toPem(pkcs8, 'PRIVATE KEY'),
        csrPem: csr.toString('pem'),
    };
}
