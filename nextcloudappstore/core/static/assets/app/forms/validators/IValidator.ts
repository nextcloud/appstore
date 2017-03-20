import {Invalid} from './Invalid';
import {Valid} from './Valid';

export interface IValidator {
    validate(value: string): Valid | Invalid;
}
