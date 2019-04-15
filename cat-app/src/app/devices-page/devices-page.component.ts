import { Component, OnInit, ViewChild } from '@angular/core';
import { MatBottomSheet } from '@angular/material';
import { AddDeviceSheetComponent } from '../add-device-sheet/add-device-sheet.component';
import { DevicesService } from '../services/devices.service';
import { Device } from '../models/device';
import { DeviceCard } from '../models/device-card';
import { map } from 'rxjs/operators';
import { FormGroupDirective, NgForm } from '@angular/forms';
import { DeviceSettings } from '../models/device-settings';

@Component({
  selector: 'app-devices-page',
  templateUrl: './devices-page.component.html',
  styleUrls: ['./devices-page.component.scss']
})
export class DevicesPageComponent implements OnInit {
  private loading: boolean = true;
  private readonly ipv4Pattern: string = "\\b(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9]))\\b";
  @ViewChild('editDeviceForm') editDeviceForm: FormGroupDirective;
  deviceCards: DeviceCard[];

  constructor(private bottomSheet: MatBottomSheet, private devicesService: DevicesService) {
    this.devicesService.getAllDevices()
      .pipe(
        map(devices => 
          devices.map(device => {
            const card: DeviceCard = {
              device: device
            }
            return card;
          })
        )
      ).subscribe(devices => {
        this.loading = false;
        this.deviceCards = devices;
      }, err => {
        this.loading = false;
      });
  }

  ngOnInit() {}

  private updateSettings(form: NgForm, card: DeviceCard): void {
    card.editing = false;
    card.loading = true;

    const settings: DeviceSettings = {
      deviceId: form.value.deviceId,
      properties: {}
    };
    delete form.value.deviceId;
    this.updateValues(form.value, settings.properties);

    console.log(settings);

    this.devicesService.updateDeviceSettings(settings)
      .subscribe((res: DeviceSettings) => {
        card.loading = false;
        this.updateValues(res, card.device.settings);
        console.log(res);
        console.log(card.device.settings);
      }, err => {
        card.loading = false;
      });
  }

  private deleteDevice(card: DeviceCard, index: number) {
    card.loading = true;
    this.devicesService.deleteDevice(card.device)
      .subscribe((dev: Device) => {
        this.deviceCards.splice(index, 1);
      }, err => {
        card.loading = false;
      });
  }

  private updateDevice(form: NgForm, card: DeviceCard): void {
    card.editing = false;
    card.loading = true;

    const device: Device = {
      description: form.value.description,
      deviceId: form.value.deviceId,
      handle: form.value.handle,
      ipAddress: form.value.ipAddress,
      location: form.value.location
    }
    this.devicesService.updateDevice(device)
      .subscribe((res: Device) => {
        card.loading = false;
        this.updateValues(res, card.device);
      }, (err => {
        card.loading = false;
      }));
  }

  private updateValues<T>(source: T, dest: T): void {
    const objValues = Object.values(source);
    Object.keys(source)
      .forEach((key, i) => {
        dest[key] = objValues[i];
      });
  }

  openAddDeviceSheet(): void {
    this.bottomSheet.open(AddDeviceSheetComponent);
    this.bottomSheet._openedBottomSheetRef.afterDismissed()
      .subscribe((dev: Device) => {
        if(!dev) { return; }
        const card: DeviceCard = {
          device: dev
        }
        this.deviceCards.unshift(card);
      });
  }

  private formatDate(date: Date): string {
    return date.toLocaleDateString('en-US', { 
      timeZone: 'UTC',
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit', 
      timeZoneName: 'short', 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric'
    });
  }

  private getUtcTime(date: Date): string {
    if(!date) { return ""; }
    const hours = this.zeroPadNumber(date.getUTCHours(), 2);
    const mins = this.zeroPadNumber(date.getUTCMinutes(), 2);
    const secs = this.zeroPadNumber(date.getUTCSeconds(), 2);
    const mils = this.zeroPadNumber(date.getUTCMilliseconds(), 3);
    return `${hours}:${mins}:${secs}.${mils}`;
  }

  private zeroPadNumber(number: number, digits: number): string {
    let padded: string = "";
    for(let i = 0; i < digits; i++) {
      if(number < 10 * i) {
        padded += "0";
      }
    }
    return padded + number.toString();
  }
}
