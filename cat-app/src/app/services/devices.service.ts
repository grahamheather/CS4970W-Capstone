import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Device } from '../models/device';
import { map, mergeMap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class DevicesService {

  private url: string = 'http://ec2-18-222-77-3.us-east-2.compute.amazonaws.com/devices';

  constructor(private http: HttpClient) { }

  getAllDevices(): Observable<Device[]> {
    return this.http.get<Device[]>(this.url)
      .pipe(
        map(devices => {
          devices.map(device => {
            if(device.createdDate) {
              device.createdDate = new Date(device.createdDate);
            }
            if(device.settings && device.settings.createdDate) {
              device.settings.createdDate = new Date(device.settings.createdDate);
            }
          })
          return devices;
        })
      );
  }

  updateDevice(device: Device): Observable<Device> {
    const values = Object.values(device);
    const pairs = Object.keys(device)
      .filter((key: string, i: number) => {
        let tempValues = values;
        if(!values[i]) {
          values.splice(i);
          return false; 
        }
        return true;
      })
      .map((key: string, i: number) => {
        return [key, values[i]];
      });
    const body = new URLSearchParams(pairs);

    console.log('pairs: ', pairs);
    console.log('Body: ', body);
    return this.http.patch(`${this.url}/${device.deviceId}`, body);
  }
}
