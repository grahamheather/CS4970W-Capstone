import { Component, OnInit, ViewChild, EventEmitter } from '@angular/core';
import { MatBottomSheet, MatBottomSheetConfig } from '@angular/material';
import { AddDeviceSheetComponent } from '../add-device-sheet/add-device-sheet.component';
import { DevicesService } from '../services/devices.service';
import { Device } from '../models/device';
import { DeviceCard } from '../models/device-card';
import { map } from 'rxjs/operators';
import { DeviceSettings } from '../models/device-settings';

@Component({
  selector: 'app-devices-page',
  templateUrl: './devices-page.component.html',
  styleUrls: ['./devices-page.component.scss']
})
export class DevicesPageComponent implements OnInit {
  loading: boolean = true;
  deviceCards: DeviceCard[];
  private addDeviceSheet: AddDeviceSheetComponent;
  private bottomSheetConfig: MatBottomSheetConfig = new MatBottomSheetConfig();

  constructor(private bottomSheet: MatBottomSheet, private devicesService: DevicesService) {
    this.bottomSheetConfig.panelClass = [
      'scrollable'
    ];

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

  createDevice(device: Device) {
    this.addDeviceSheet.loading = true;

    this.devicesService.createDevice(device)
      .subscribe((res: Device) => {
        const card: DeviceCard = {
          device: res
        }
        this.deviceCards.unshift(card);

        this.addDeviceSheet.loading = false;

        this.addDeviceSheet.closeSheet();
      }, err => {
        this.addDeviceSheet.loading = false;
      }); 
  }

  private updateSettings(settings: DeviceSettings, card: DeviceCard): void {
    card.editing = false;
    card.loading = true;

    this.devicesService.updateDeviceSettings(settings)
      .subscribe((res: DeviceSettings) => {
        card.loading = false;
        this.updateValues(res, card.device.settings);
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

  private updateDevice(device: Device, card: DeviceCard): void {
    card.editing = false;
    card.loading = true;

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
    const sheetRef = this.bottomSheet.open(AddDeviceSheetComponent, this.bottomSheetConfig);
    this.addDeviceSheet = sheetRef.instance;
    const sub = this.addDeviceSheet.addDevice
      .subscribe(dev => {
        this.createDevice(dev);
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
