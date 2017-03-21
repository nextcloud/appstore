/**
 * Turns a float into a class name for the comment section
 * @param value
 * @returns {any}
 */
export function createRatingClass(value: number): string {
    // because floats
    if (value >= .999999999) {
        return 'good';
    } else if (value <= 0.000000001) {
        return 'bad';
    } else {
        return 'ok';
    }
}
