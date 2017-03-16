describe('Testing the window error result parser', () => {
    let func = window.exports.parseJSONError;

    it('should parse a general error', () => {
        expect(func(['Signature is invalid']))
            .toEqual({
                'global': ['Signature is invalid'],
                'fields': {}
            });
    });

});
