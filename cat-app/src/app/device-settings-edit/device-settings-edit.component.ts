import { Component, OnInit, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
import { Device } from '../models/device';
import { DeviceSettings } from '../models/device-settings';
import { NgForm } from '@angular/forms';

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
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

  getSettings(form: NgForm): DeviceSettings {
    const settings: DeviceSettings = {
      deviceId: form.value.deviceId,
      properties: {}
    };
    delete form.value.deviceId;
    Object.assign(settings.properties, form.value);
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
