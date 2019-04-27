import { NG_VALIDATORS, FormControl, Validator, ValidationErrors } from '@angular/forms';
import { Directive } from '@angular/core';

@Directive({
  selector: '[ipv4]',
  providers: [
    {
      provide: NG_VALIDATORS,
      useExisting: Ipv4ValidatorDirective,
      multi: true
    }
  ]
})
export class Ipv4ValidatorDirective implements Validator {
  validate(c: FormControl): ValidationErrors | null {
    const ipv4: string = c.value;
    const error = {
      ipv4: {
        valid: false,
        message: 'Invalid IPv4 address'
      }
    };
    if(!ipv4) {
      return null;
    }
    if(ipv4.length < 7 || ipv4.length > 15) {
      return error;
    }
    const octets = ipv4.split('.');
    if(octets.length != 4) {
      return error;
    }
    if(!octets.every(octet => {
      if(octet.length < 1) {
        return false;
      }
      // Ensure each octet consists of only digits
      for(let i = 0; i < octet.length; i++) {
        const char = octet.charAt(i);
        if(!'0123456789'.includes(char)) {
          return false;
        }
      }
      const octetValue = Number.parseInt(octet);
      if(octetValue < 0 || octetValue > 255) {
        return false;
      }
      return true;
    })) {
      return error;
    }
    return null;
  }
}
