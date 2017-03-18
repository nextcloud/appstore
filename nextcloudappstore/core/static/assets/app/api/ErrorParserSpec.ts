import {parseJSONError, toIdErrorMap} from './ErrorParser';

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

    it('should turn a JSON field error to an id and message map', () => {
        const expected = new Map<string, string[]>();
        expected.set('id_signature', [
            'Field must not be empty',
            'Field must be a signature',
        ]);
        expected.set('id_test', [
            'Field must not be empty',
        ]);

        const result = toIdErrorMap(parseJSONError({
            signature: [
                'Field must not be empty',
                'Field must be a signature',
            ],
            test: [
                'Field must not be empty',
            ],
        }));
        expect(result.size).toEqual(3);
        expect(result.get('id_signature'))
            .toEqual(expected.get('id_signature'));
        expect(result.get('id_test'))
            .toEqual(expected.get('id_test'));
        expect(result.get('global_error'))
            .toEqual([]);
    });

    it('should turn a JSON field error to an id and message map', () => {
        const expected = new Map<string, string[]>();
        expected.set('global_error', [
            'Field must not be empty',
            'Field must be a signature',
        ]);

        const result = toIdErrorMap(parseJSONError([
            'Field must not be empty',
            'Field must be a signature',
        ]));
        expect(result.size).toEqual(1);
        expect(result.get('global_error'))
            .toEqual(expected.get('global_error'));
    });

});
