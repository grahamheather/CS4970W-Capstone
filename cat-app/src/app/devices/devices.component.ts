import { Component, OnInit } from '@angular/core';
import { MatBottomSheet, MatBottomSheetConfig } from '@angular/material';
import { AddDeviceSheetComponent } from '../add-device-sheet/add-device-sheet.component';
import { DevicesService } from '../services/devices.service';
import { Device } from '../models/device';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-devices',
  templateUrl: './devices.component.html',
  styleUrls: ['./devices.component.scss']
})
export class DevicesComponent implements OnInit {

  devices$: Observable<Device[]>;

  constructor(private bottomSheet: MatBottomSheet, private devicesService: DevicesService) {
    this.devices$ = this.devicesService.getAllDevices();
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
}
