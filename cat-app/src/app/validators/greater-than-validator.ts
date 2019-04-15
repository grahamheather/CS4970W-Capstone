import {  
    NG_VALIDATORS,  
    FormControl,  
    Validator,  
    ValidationErrors
   } from '@angular/forms';
import { Directive, Input } from '@angular/core';  

@Directive({
    selector: '[greaterThan]',
    providers: [
        {
            provide: NG_VALIDATORS,
            useExisting: GreaterThanValidator,  
            multi: true
        }  
    ]  
})
export class GreaterThanValidator implements Validator {
    @Input('greaterThan') value: Number;

    validate(c: FormControl): ValidationErrors | null {
        if(c.value < this.value) {
            return { 
                greaterThan: { 
                    valid: false,
                    message: `Value must be greater than ${this.value}`
                } 
            };
        }
        return null;
    }
}
