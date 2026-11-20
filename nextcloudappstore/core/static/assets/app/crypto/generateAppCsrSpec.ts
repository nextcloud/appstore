/**
 * SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import 'reflect-metadata';
import * as x509 from '@peculiar/x509';
import {
    generateAppCsr,
    InvalidAppIdError,
    isValidAppId,
} from './generateAppCsr';

describe('generateAppCsr', () => {
    it('accepts lowercase app ids with underscores', () => {
        expect(isValidAppId('news')).toBe(true);
        expect(isValidAppId('twofactor_gateway')).toBe(true);
        expect(isValidAppId('News')).toBe(false);
        expect(isValidAppId('news-app')).toBe(false);
        expect(isValidAppId('')).toBe(false);
    });

    it('rejects invalid app ids', async () => {
        try {
            await generateAppCsr('Invalid-Id');
            fail('expected InvalidAppIdError');
        } catch (e) {
            expect(e instanceof InvalidAppIdError).toBe(true);
        }
    });

    it('generates PEM key and CSR with matching CN', async () => {
        const appId = 'testdummy';
        const result = await generateAppCsr(appId);

        expect(result.appId).toBe(appId);
        expect(result.privateKeyPem.startsWith('-----BEGIN PRIVATE KEY-----')).toBe(true);
        expect(result.privateKeyPem.trim().endsWith('-----END PRIVATE KEY-----')).toBe(true);
        expect(result.csrPem.indexOf('-----BEGIN CERTIFICATE REQUEST-----')).not.toBe(-1);
        expect(result.csrPem.indexOf('-----END CERTIFICATE REQUEST-----')).not.toBe(-1);

        const csr = new x509.Pkcs10CertificateRequest(result.csrPem);
        expect(csr.subject).toBe(`CN=${appId}`);
    }, 60000);
});
