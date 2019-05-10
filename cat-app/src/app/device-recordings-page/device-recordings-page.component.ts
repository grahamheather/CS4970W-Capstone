import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { ParamMap, ActivatedRoute } from '@angular/router';
import { DevicesService } from '../services/devices.service';
import { switchMap, tap, shareReplay } from 'rxjs/operators';
import { Observable, combineLatest, BehaviorSubject, of } from 'rxjs';
import { Device } from '../models/device';
import { RecordingsService } from '../services/recordings.service';
import { Recording } from '../models/recording';
import { RecordingSheetComponent } from '../recording-sheet/recording-sheet.component';
import { MatBottomSheetConfig, MatBottomSheet } from '@angular/material';

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-device-recordings-page',
  templateUrl: './device-recordings-page.component.html',
  styleUrls: ['./device-recordings-page.component.scss']
})
export class DeviceRecordingsPageComponent implements OnInit {
  private bottomSheetConfig: MatBottomSheetConfig = new MatBottomSheetConfig();
  private loadingSubject = new BehaviorSubject<boolean>(true);
  device$: Observable<Device>;
  recordings$: Observable<Recording[]>;
  loading$: Observable<boolean> = this.loadingSubject.asObservable();

  constructor(private route: ActivatedRoute, private devicesService: DevicesService, private recordingsService: RecordingsService, private bottomSheet: MatBottomSheet) {
    this.bottomSheetConfig.panelClass = [
      'scrollable'
    ];
   }

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
    combineLatest(this.recordings$, this.device$).subscribe(
      () => this.loadingSubject.next(false),
      () => this.loadingSubject.next(false)
    );
  }

  openRecordingSheet(recordingId: string): void {
    const sheetRef = this.bottomSheet.open(RecordingSheetComponent, this.bottomSheetConfig);
    const recordingSheet = sheetRef.instance;

    recordingSheet.getRecording(recordingId);
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
