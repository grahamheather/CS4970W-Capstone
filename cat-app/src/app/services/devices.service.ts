import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Device } from '../models/device';
import { map, mergeMap } from 'rxjs/operators';
import { DeviceSettings } from '../models/device-settings';

@Injectable({
  providedIn: 'root'
})
export class DevicesService {
  private baseUrl: string = 'http://ec2-18-222-77-3.us-east-2.compute.amazonaws.com';

  constructor(private http: HttpClient) { }

  getAllDevices(): Observable<Device[]> {
    return this.http.get<Device[]>(`${this.baseUrl}/devices`)
      .pipe(
        map(devices => {
          devices.map(device => {
            if(device.createdDate) {
              device.createdDate = new Date(device.createdDate);
            }
            if(device.settings) {
              if(device.settings.createdDate) {
                device.settings.createdDate = new Date(device.settings.createdDate);
              }
              if(device.settings.properties) {
                device.settings.properties = JSON.parse(device.settings.properties);
              }
            }
          })
          return devices;
        })
      );
  }

  updateDevice(device: Device): Observable<Device> {
    return this.http
      .patch(`${this.baseUrl}/devices/${device.deviceId}`, this.urlEncode(device), {
        headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded')
      });
  }

  private urlEncode(a: any): string {
    let pairs: string[][] = [];
    const keys = Object.keys(a);
    Object.values(a)
      .forEach((value: any, i) => {
        if(!value) { return; }
        pairs.push([keys[i], value]);
      });
    return new URLSearchParams(pairs).toString();
  }

  deleteDevice(device: Device): Observable<Device> {
    return this.http.delete(`${this.baseUrl}/devices/${device.deviceId}`);
  }

  updateDeviceSettings(settings: DeviceSettings): Observable<DeviceSettings> {
    if(!settings.properties) {
      settings.properties = {};
    }
    return this.http
      .put(`${this.baseUrl}/devices/${settings.deviceId}/settings`, `settings=${JSON.stringify(settings.properties)}`, {
        headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded')
      }).pipe(
        map((settings: DeviceSettings) => {
          settings.createdDate = new Date(settings.createdDate);
          return settings;
        })
      );
  }

  createDevice(device: Device): Observable<Device> {
    let settings = '{}';
    if(device.settings && device.settings.properties) {
      settings = JSON.stringify(device.settings.properties);
    }
    device.settings = null;

    return this.http.post(`${this.baseUrl}/devices`, `${this.urlEncode(device)}&settings=${JSON.stringify(settings)}`, {
      headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded')
    }).pipe(
      map((dev: Device) => {
        dev.createdDate = new Date(dev.createdDate);
        if(dev.settings) {
          if(dev.settings.createdDate) {
            dev.settings.createdDate = new Date(dev.settings.createdDate);
          }
          if(dev.settings.properties) {
            dev.settings.properties = JSON.parse(dev.settings.properties);
          }
        }
        return dev;
      })
    );
  }
}
