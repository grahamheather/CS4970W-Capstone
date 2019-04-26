import { Component, OnInit } from '@angular/core';
import { ParamMap, ActivatedRoute } from '@angular/router';
import { DevicesService } from '../services/devices.service';
import { switchMap, map, delay, tap, shareReplay } from 'rxjs/operators';
import { Observable, combineLatest, empty, of, BehaviorSubject } from 'rxjs';
import { Device } from '../models/device';
import { RecordingsService } from '../services/recordings.service';
import { Recording } from '../models/recording';

@Component({
  selector: 'app-device-recordings-page',
  templateUrl: './device-recordings-page.component.html',
  styleUrls: ['./device-recordings-page.component.scss']
})
export class DeviceRecordingsPageComponent implements OnInit {
  private loadingSubject = new BehaviorSubject<boolean>(true);
  device$: Observable<Device>;
  recordings$: Observable<Recording[]>;
  loading$: Observable<boolean> = this.loadingSubject.asObservable();

  constructor(private route: ActivatedRoute, private devicesService: DevicesService, private recordingsService: RecordingsService) { }

  ngOnInit() {
    this.device$ = this.route.paramMap.pipe(
      tap(() => this.loadingSubject.next(true)),
      switchMap((params: ParamMap) =>
        this.devicesService.getDevice(params.get('id'))
      ),
      shareReplay()
    );
    this.recordings$ = this.route.paramMap.pipe(
      tap(() => this.loadingSubject.next(true)),
      switchMap((params: ParamMap) =>
        this.recordingsService.getRecordingsByDevice(params.get('id'))
      ),
      shareReplay()
    );
    // TODO: remove after debugging
    // this.recordings$ = of([{recordingId: 'id 1', data: { test: 'test1'}}, {recordingId:'id2', data: {test: 'test2'}}]);
    combineLatest(this.recordings$, this.device$).subscribe(
      () => this.loadingSubject.next(false)
    );
  }

  openRecordingSheet(recordings: Recording[], recordingId: string): void {
    const recording = recordings.find(e => {
      return e.recordingId === recordingId;
    });
    console.log('Recording: ', recording);
  }

  formatDate(date: Date): string {
    if(!date) return '';
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
