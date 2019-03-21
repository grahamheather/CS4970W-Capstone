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
            if(!device.createdDate) { return; }
            device.createdDate = new Date(device.createdDate);
          })
          return devices;
        })
      );
  }
}
