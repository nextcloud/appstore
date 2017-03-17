import {parseJSONError} from './Form';

describe('Testing the window error result parser', () => {

    it('should parse a general error', () => {
        expect(parseJSONError(['Signature is invalid']))
            .toEqual({
                fields: {},
                global: ['Signature is invalid'],
            });
    });

    it('should parse a field error', () => {
        expect(parseJSONError({
            signature: [
                'Field must not be empty',
                'Field must be a signature',
            ],
        })).toEqual({
            fields: {
                signature: [
                    'Field must not be empty',
                    'Field must be a signature',
                ],
            },
            global: [],
        });
    });

});
