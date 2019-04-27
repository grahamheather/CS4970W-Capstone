import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { MatBottomSheet, MatBottomSheetConfig } from '@angular/material';
import { AddDeviceSheetComponent } from '../add-device-sheet/add-device-sheet.component';
import { DevicesService } from '../services/devices.service';
import { Device } from '../models/device';
import { DeviceCard } from '../models/device-card';
import { map } from 'rxjs/operators';
import { DeviceSettings } from '../models/device-settings';
import { BehaviorSubject, Observable } from 'rxjs';

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-devices-page',
  templateUrl: './devices-page.component.html',
  styleUrls: ['./devices-page.component.scss']
})
export class DevicesPageComponent implements OnInit {
  private addDeviceSheet: AddDeviceSheetComponent;
  private bottomSheetConfig: MatBottomSheetConfig = new MatBottomSheetConfig();
  private loadingSubject: BehaviorSubject<boolean> = new BehaviorSubject(true);
  private deviceCardsSubject: BehaviorSubject<DeviceCard[]> = new BehaviorSubject([]);
  loading$: Observable<boolean> = this.loadingSubject.asObservable();
  deviceCards$: Observable<DeviceCard[]> = this.deviceCardsSubject.asObservable();

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
        this.deviceCardsSubject.next(devices);
      }, err => {}, () => {
        this.loadingSubject.next(false);
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
    this.addDeviceSheet.isLoading(true);

    this.devicesService.createDevice(device)
      .subscribe((res: Device) => {
        const card: DeviceCard = {
          device: res
        }
        const deviceCards = this.deviceCardsSubject.value;
        deviceCards.unshift(card);

        this.deviceCardsSubject.next(deviceCards);
        this.addDeviceSheet.closeSheet();
      }, err => {}, () => {
        this.addDeviceSheet.isLoading(false);
      }); 
  }

  private updateSettings(settings: DeviceSettings, card: DeviceCard): void {
    card.editing = false;
    card.loading = true;
    this.deviceCardsSubject.next(this.deviceCardsSubject.value);

    this.devicesService.updateDeviceSettings(settings)
      .subscribe((res: DeviceSettings) => {
        Object.assign(card.device.settings, res);
      }, err => {}, () => {
        card.loading = false;
        this.deviceCardsSubject.next(this.deviceCardsSubject.value);
      });
  }

  private deleteDevice(card: DeviceCard, index: number) {
    card.loading = true;
    this.deviceCardsSubject.next(this.deviceCardsSubject.value);

    this.devicesService.deleteDevice(card.device)
      .subscribe((dev: Device) => {
        const deviceCards = this.deviceCardsSubject.value;
        deviceCards.splice(index, 1);
      }, err => {}, () => {
        card.loading = false;
        this.deviceCardsSubject.next(this.deviceCardsSubject.value);
      });
  }

  private updateDevice(device: Device, card: DeviceCard): void {
    card.editing = false;
    card.loading = true;
    this.deviceCardsSubject.next(this.deviceCardsSubject.value);

    this.devicesService.updateDevice(device)
      .subscribe((res: Device) => {
        Object.assign(card.device, res);
      }, err => {}, () => {
        card.loading = false;
        this.deviceCardsSubject.next(this.deviceCardsSubject.value);
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
