import { Component, OnInit, ViewChild } from '@angular/core';
import { MatBottomSheet, MatBottomSheetConfig } from '@angular/material';
import { AddDeviceSheetComponent } from '../add-device-sheet/add-device-sheet.component';
import { DevicesService } from '../services/devices.service';
import { Device } from '../models/device';
import { Observable } from 'rxjs';
import { DeviceCard } from '../models/device-card';
import { map } from 'rxjs/operators';
import { Moment } from 'moment';
import { FormGroupDirective, NgForm } from '@angular/forms';

@Component({
  selector: 'app-devices',
  templateUrl: './devices.component.html',
  styleUrls: ['./devices.component.scss']
})
export class DevicesComponent implements OnInit {
  private readonly ipv4Pattern: string = "\\b(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9]))\\b";
  @ViewChild('editDeviceForm') editDeviceForm: FormGroupDirective;
  deviceCards$: Observable<DeviceCard[]>;

  constructor(private bottomSheet: MatBottomSheet, private devicesService: DevicesService) {
    this.deviceCards$ = this.devicesService.getAllDevices()
      .pipe(
        map(devices => 
          devices.map(device => {
            const card: DeviceCard = {
              device: device
            }
            return card;
          })
        )
      );
  }

  ngOnInit() {}

  private updateDevice(form: NgForm): void {
    console.log(form.value);
    this.devicesService.updateDevice(form.value)
      .subscribe(res => {
        console.log(res);
      });
  }

  openAddDeviceSheet(): void {
    this.bottomSheet.open(AddDeviceSheetComponent);
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

  private setDate(moment: Moment, date: Date): void {
    date.setUTCDate(moment.date());
    date.setUTCMonth(moment.month());
    date.setUTCFullYear(moment.year());
  }

  private setTime(time: string, date: Date): void {
    date.setUTCHours(Number.parseInt(time.substring(0, 2)));
    date.setUTCMinutes(Number.parseInt(time.substring(3, 5)));
    date.setUTCSeconds(Number.parseInt(time.substring(6, 8)));
  }

  private getUtcTime(date: Date): string {
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

  private showSettings(card: DeviceCard): void {
    card.showSettings = true;
  }

  private hideSettings(card: DeviceCard): void {
    card.showSettings = false;
  }

  private beginEdit(card: DeviceCard): void {
    card.editing = {
      ...card,
      device: {
        ...card.device,
        settings: {
          ...card.device.settings
        }
      }
    }
  }
}
