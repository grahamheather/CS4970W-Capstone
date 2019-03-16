import { Component, OnInit } from '@angular/core';
import { MatBottomSheetRef } from '@angular/material';

@Component({
  selector: 'app-add-device-sheet',
  templateUrl: './add-device-sheet.component.html',
  styleUrls: ['./add-device-sheet.component.scss']
})
export class AddDeviceSheetComponent implements OnInit {

  constructor(private bottomSheetRef: MatBottomSheetRef<AddDeviceSheetComponent>) { }

  ngOnInit() {
  }
}
