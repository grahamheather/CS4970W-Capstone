import { Component, OnInit, Input, EventEmitter, Output } from '@angular/core';
import { Device } from '../models/device';

@Component({
  selector: 'app-device-settings',
  templateUrl: './device-settings.component.html',
  styleUrls: ['./device-settings.component.scss']
})
export class DeviceSettingsComponent implements OnInit {
  @Input() device: Device;
  @Input() loading: Boolean;
  @Output() viewDevice: EventEmitter<void> = new EventEmitter<void>();
  @Output() viewEdit: EventEmitter<void> = new EventEmitter<void>();

  constructor() { }

  ngOnInit() {
  }

  formatDate(date: Date): string {
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
