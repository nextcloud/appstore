import {CertValidator} from './CertValidator';
import {Invalid} from './Invalid';
import {Valid} from './Valid';

describe('Testing the public certificate', () => {

    it('should parse a correct certificate', () => {
        const validator = new CertValidator();
        const input = '-----BEGIN CERTIFICATE-----\n' +
            '-----END CERTIFICATE-----';

        const result = validator.validate(input);
        expect(result instanceof Valid).toBe(true);
    });

    it('should fail for an incorrect certificate', () => {
        const validator = new CertValidator();
        const input = '-----BEGIN CERTIFICATE----\n' +
            '-----END CERTIFICATE-----';

        const result = validator.validate(input);
        expect(result instanceof Invalid).toBe(true);
        expect((result as Invalid).errorMsgId)
            .toBe('msg-invalid-certificate');
    });

});
