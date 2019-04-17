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

  private getDevice(form: NgForm) {
    const device = {
      description: form.value.description,
      handle: form.value.handle,
      ipAddress: form.value.ipAddress,
      location: form.value.location
    }
    return device;
  }

  closeSheet() {
    this.bottomSheetRef.dismiss();
  }
}
