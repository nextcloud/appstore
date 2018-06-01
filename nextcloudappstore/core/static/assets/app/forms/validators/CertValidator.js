import { Invalid } from './Invalid';
import { Valid } from './Valid';
export class CertValidator {
    validate(certificate) {
        if (certificate.startsWith('-----BEGIN CERTIFICATE-----') &&
            certificate.endsWith('-----END CERTIFICATE-----')) {
            return new Valid();
        }
        else {
            return new Invalid('msg-invalid-certificate');
        }
    }
}
//# sourceMappingURL=CertValidator.js.map