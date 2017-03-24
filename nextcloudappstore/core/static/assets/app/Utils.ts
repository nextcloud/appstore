export function getOrDefault<K, V>(map: Map<K, V>, key: K, defaultValue: V): V {
    const value = map.get(key);
    if (value === undefined) {
        return defaultValue;
    } else {
        return value;
    }
}

/**
 * Yeah, we're doing this ;D
 */
export class Maybe<T> {
    constructor(private readonly value?: T | null | undefined) {
    }

    public map<V>(func: (val: T) => V | null | undefined): Maybe<V> {
        if (this.value !== null && this.value !== undefined) {
            return new Maybe<V>(func(this.value));
        } else {
            return new Maybe<V>();
        }
    }

    public flatMap<V>(func: (val: T) => Maybe<V>): Maybe<V> {
        if (this.value !== null && this.value !== undefined) {
            return func(this.value);
        } else {
            return new Maybe<V>();
        }
    }

    public filter(predicate: (val: T) => boolean): Maybe<T> {
        if (this.value !== null && this.value !== undefined &&
            predicate(this.value)) {
            return this;
        } else {
            return new Maybe<T>();
        }
    }

    public orElse(value: T): T {
        if (this.value !== null && this.value !== undefined) {
            return this.value;
        } else {
            return value;
        }
    }

    public orThrow(exceptionCreator: () => Error): T {
        if (this.value !== null && this.value !== undefined) {
            return this.value;
        } else {
            throw exceptionCreator();
        }
    }

    public isPresent(): boolean {
        return this.value !== null && this.value !== undefined;
    }

    public ifPresent(func: (val: T) => void) {
        if (this.value !== null && this.value !== undefined) {
            func(this.value);
        }
    }
}
