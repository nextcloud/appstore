define(['app/Form'], function (Form) {
    describe('Testing the window error result parser', () => {

        it('should parse a general error', () => {
            expect(Form.parseJSONError(['Signature is invalid']))
                .toEqual({
                    'global': ['Signature is invalid'],
                    'fields': {}
                });
        });

    });
});
