import { Component, OnInit, Output, EventEmitter, Input } from '@angular/core';
import { MatBottomSheetRef } from '@angular/material';
import { NgForm } from '@angular/forms';
import { Device } from '../models/device';

@Component({
  selector: 'app-add-device-sheet',
  templateUrl: './add-device-sheet.component.html',
  styleUrls: ['./add-device-sheet.component.scss']
})
export class AddDeviceSheetComponent implements OnInit {
  private readonly ipv4Pattern: string = "\\b(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9]))\\b";
  loading: boolean;
  @Output() addDevice: EventEmitter<Device> = new EventEmitter<Device>();

  constructor(private bottomSheetRef: MatBottomSheetRef<AddDeviceSheetComponent>) { }

  ngOnInit() {
  }

  private updateValues<T>(source: T, dest: T): void {
    const objValues = Object.values(source);
    Object.keys(source)
      .forEach((key, i) => {
        dest[key] = objValues[i];
      });
  }

  private getDevice(form: NgForm) {
    const device = {
      description: form.value.description,
      handle: form.value.handle,
      ipAddress: form.value.ipAddress,
      location: form.value.location,
      settings: { properties: {} }
    }
    delete form.value.description;
    delete form.value.handle;
    delete form.value.ipAddress;
    delete form.value.location;
    this.updateValues(form.value, device.settings.properties);
    return device;
  }

  closeSheet() {
    this.bottomSheetRef.dismiss();
  }
}
