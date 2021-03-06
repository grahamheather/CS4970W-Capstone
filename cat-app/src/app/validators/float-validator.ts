import { NG_VALIDATORS, FormControl, Validator, ValidationErrors } from '@angular/forms';
import { Directive } from '@angular/core';  

@Directive({
    selector: '[float]',
    providers: [
        {
            provide: NG_VALIDATORS,
            useExisting: FloatValidator,  
            multi: true
        }  
    ]  
})
export class FloatValidator implements Validator {
    validate(c: FormControl): ValidationErrors | null {
        if(Number.isNaN(Number.parseFloat(c.value))) {
            return { 
                float: { 
                    valid: false,
                    message: 'Value must be a valid floating-point number'
                } 
            };
        }
        return null;
    }
}
