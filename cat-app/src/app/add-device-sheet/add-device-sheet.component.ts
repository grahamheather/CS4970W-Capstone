import { Component, OnInit, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
import { MatBottomSheetRef } from '@angular/material';
import { NgForm } from '@angular/forms';
import { Device } from '../models/device';
import { BehaviorSubject, Observable } from 'rxjs';

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-add-device-sheet',
  templateUrl: './add-device-sheet.component.html',
  styleUrls: ['./add-device-sheet.component.scss']
})
export class AddDeviceSheetComponent implements OnInit {
  private loadingSubject: BehaviorSubject<boolean> = new BehaviorSubject(false);
  loading$: Observable<boolean> = this.loadingSubject.asObservable();
  @Output() addDevice: EventEmitter<Device> = new EventEmitter<Device>();

  constructor(private bottomSheetRef: MatBottomSheetRef<AddDeviceSheetComponent>) { }

  ngOnInit() {
  }

  isLoading(value: boolean) {
    this.loadingSubject.next(value);
  }

  getDevice(form: NgForm) {
    const device = {
      description: form.value.description,
      handle: form.value.handle,
      ipAddress: form.value.ipAddress,
      location: form.value.location,
      settings: { properties: {} }
    }
    delete form.value.description;
    delete form.value.handle;
    delete form.value.ipAddress;
    delete form.value.location;
    Object.assign(device.settings.properties, form.value);
    return device;
  }

  closeSheet() {
    this.bottomSheetRef.dismiss();
  }
}
