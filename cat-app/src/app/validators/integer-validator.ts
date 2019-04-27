import { NG_VALIDATORS, FormControl, Validator, ValidationErrors } from '@angular/forms';
import { Directive } from '@angular/core';  

@Directive({
    selector: '[integer]',
    providers: [
        {
            provide: NG_VALIDATORS,
            useExisting: IntegerValidator,  
            multi: true
        }  
    ]  
})
export class IntegerValidator implements Validator {
    validate(c: FormControl): ValidationErrors | null {
        const parsed = Number.parseInt(c.value);
        if(Number.isNaN(parsed)) {
            return { 
                integer: { 
                    valid: false,
                    message: 'Value must be a valid integer'
                } 
            };
        }
        if(c.value !== parsed) {
            c.patchValue(parsed);
        }
        return null;
    }
}
