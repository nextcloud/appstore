export function getOrDefault(map, key, defaultValue) {
    const value = map.get(key);
    if (value === undefined) {
        return defaultValue;
    }
    else {
        return value;
    }
}
export class Maybe {
    constructor(value) {
        this.value = value;
    }
    map(func) {
        if (this.value !== null && this.value !== undefined) {
            return new Maybe(func(this.value));
        }
        else {
            return new Maybe();
        }
    }
    flatMap(func) {
        if (this.value !== null && this.value !== undefined) {
            return func(this.value);
        }
        else {
            return new Maybe();
        }
    }
    filter(predicate) {
        if (this.value !== null && this.value !== undefined &&
            predicate(this.value)) {
            return this;
        }
        else {
            return new Maybe();
        }
    }
    orElse(value) {
        if (this.value !== null && this.value !== undefined) {
            return this.value;
        }
        else {
            return value;
        }
    }
    orThrow(exceptionCreator) {
        if (this.value !== null && this.value !== undefined) {
            return this.value;
        }
        else {
            throw exceptionCreator();
        }
    }
    isPresent() {
        return this.value !== null && this.value !== undefined;
    }
    ifPresent(func) {
        if (this.value !== null && this.value !== undefined) {
            func(this.value);
        }
    }
}
//# sourceMappingURL=Utils.js.map