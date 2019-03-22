import { Component, OnInit } from '@angular/core';
import { MatBottomSheet, MatBottomSheetConfig } from '@angular/material';
import { AddDeviceSheetComponent } from '../add-device-sheet/add-device-sheet.component';
import { DevicesService } from '../services/devices.service';
import { Device } from '../models/device';
import { Observable } from 'rxjs';
import { DeviceCard } from '../models/device-card';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-devices',
  templateUrl: './devices.component.html',
  styleUrls: ['./devices.component.scss']
})
export class DevicesComponent implements OnInit {

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

  private showSettings(card: DeviceCard): void {
    card.showSettings = true;
  }

  private hideSettings(card: DeviceCard): void {
    card.showSettings = false;
  }
}
