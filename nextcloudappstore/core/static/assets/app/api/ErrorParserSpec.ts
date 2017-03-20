import {parseJSONError} from './ErrorParser';

describe('Testing the window error result parser', () => {

    it('should parse a general error', () => {
        expect(parseJSONError(['Signature is invalid']))
            .toEqual({
                fields: new Map<string, string[]>(),
                global: ['Signature is invalid'],
            });
    });

    it('should parse a field error', () => {
        const parsed = parseJSONError({
            signature: [
                'Field must not be empty',
                'Field must be a signature',
            ],
        });
        expect(parsed.global).toEqual([]);
        expect(parsed.fields.get('signature')).toEqual([
            'Field must not be empty',
            'Field must be a signature',
        ]);
    });

});
