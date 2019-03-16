import { Component, OnInit } from '@angular/core';
import { MatBottomSheet, MatBottomSheetConfig } from '@angular/material';
import { AddDeviceSheetComponent } from '../add-device-sheet/add-device-sheet.component';

@Component({
  selector: 'app-devices',
  templateUrl: './devices.component.html',
  styleUrls: ['./devices.component.scss']
})
export class DevicesComponent implements OnInit {

  constructor(private bottomSheet: MatBottomSheet) {}

  ngOnInit() {}

  openAddDeviceSheet(): void {
    this.bottomSheet.open(AddDeviceSheetComponent);
  }
}
