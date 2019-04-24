import { Component, OnInit } from '@angular/core';
import { ParamMap, ActivatedRoute } from '@angular/router';
import { DevicesService } from '../services/devices.service';
import { switchMap } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { Device } from '../models/device';

@Component({
  selector: 'app-device-recordings-page',
  templateUrl: './device-recordings-page.component.html',
  styleUrls: ['./device-recordings-page.component.scss']
})
export class DeviceRecordingsPageComponent implements OnInit {
  device$: Observable<Device>;

  constructor(private route: ActivatedRoute, private devicesService: DevicesService) { }

  ngOnInit() {
    this.device$ = this.route.paramMap.pipe(
      switchMap((params: ParamMap) =>
        this.devicesService.getDevice(params.get('id'))
      )
    );
  }

}
