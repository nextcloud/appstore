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
    constructor(private value: T | null | undefined) {
    }

    public map<V>(func: (val: T) => V | null | undefined): Maybe<V> {
        if (this.value !== null && this.value !== undefined) {
            return new Maybe<V>(func(this.value));
        } else {
            return new Maybe<V>(null);
        }
    }

    public orElse(value: T): T {
        if (this.value !== null && this.value !== undefined) {
            return this.value;
        } else {
            return value;
        }
    }

    public isPresent(): boolean {
        return this.value !== null && this.value !== undefined;
    }
}
