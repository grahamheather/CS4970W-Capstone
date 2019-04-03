import { Component, OnInit } from '@angular/core';
import { MatBottomSheetRef } from '@angular/material';
import { DevicesService } from '../services/devices.service';
import { NgForm } from '@angular/forms';
import { Device } from '../models/device';

@Component({
  selector: 'app-add-device-sheet',
  templateUrl: './add-device-sheet.component.html',
  styleUrls: ['./add-device-sheet.component.scss']
})
export class AddDeviceSheetComponent implements OnInit {
  private readonly ipv4Pattern: string = "\\b(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9]))\\b";
  private loading: boolean = false;

  constructor(private bottomSheetRef: MatBottomSheetRef<AddDeviceSheetComponent>, private devicesService: DevicesService) { }

  ngOnInit() {
  }

  createDevice(form: NgForm) {
    this.loading = true;

    const device = {
      description: form.value.description,
      handle: form.value.handle,
      ipAddress: form.value.ipAddress,
      location: form.value.location
    }

    this.devicesService.createDevice(device)
      .subscribe((res: Device) => {
        this.closeSheet(res);
        this.loading = false;
      }, err => {
        this.loading = false;
      }); 
  }

  closeSheet(out?: Device) {
    this.bottomSheetRef.dismiss(out);
  }
}
