import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Device } from '../models/device';
import { DeviceSettings } from '../models/device-settings';
import { NgForm } from '@angular/forms';

@Component({
  selector: 'app-device-settings-edit',
  templateUrl: './device-settings-edit.component.html',
  styleUrls: ['./device-settings-edit.component.scss']
})
export class DeviceSettingsEditComponent implements OnInit {
  @Input() device: Device;
  @Output() updateSettings: EventEmitter<DeviceSettings> = new EventEmitter<DeviceSettings>();
  @Output() cancelEdit: EventEmitter<void> = new EventEmitter<void>();

  constructor() { }

  ngOnInit() {
  }

  private updateValues<T>(source: T, dest: T): void {
    const objValues = Object.values(source);
    Object.keys(source)
      .forEach((key, i) => {
        dest[key] = objValues[i];
      });
  }

  getSettings(form: NgForm): DeviceSettings {
    const settings: DeviceSettings = {
      deviceId: form.value.deviceId,
      properties: {}
    };
    delete form.value.deviceId;
    this.updateValues(form.value, settings.properties);
    return settings;
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

  private getUtcTime(date: Date): string {
    if(!date) { return ""; }
    const hours = this.zeroPadNumber(date.getUTCHours(), 2);
    const mins = this.zeroPadNumber(date.getUTCMinutes(), 2);
    const secs = this.zeroPadNumber(date.getUTCSeconds(), 2);
    const mils = this.zeroPadNumber(date.getUTCMilliseconds(), 3);
    return `${hours}:${mins}:${secs}.${mils}`;
  }
}
