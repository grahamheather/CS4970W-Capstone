import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { Recording } from '../models/recording';
import { BehaviorSubject, Observable } from 'rxjs';
import { RecordingsService } from '../services/recordings.service';

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-recording-sheet',
  templateUrl: './recording-sheet.component.html',
  styleUrls: ['./recording-sheet.component.scss']
})
export class RecordingSheetComponent implements OnInit {
  private loadingSubject: BehaviorSubject<boolean> = new BehaviorSubject(true);
  private errorSubject: BehaviorSubject<boolean> = new BehaviorSubject(false);
  private recordingSubject: BehaviorSubject<Recording> = new BehaviorSubject<Recording>(null);
  loading$: Observable<boolean> = this.loadingSubject.asObservable();
  error$: Observable<boolean> = this.errorSubject.asObservable();
  recording$: Observable<Recording> = this.recordingSubject.asObservable();

  constructor(private recordingsService: RecordingsService) {}

  ngOnInit() {
  }

  getRecording(recordingId: string): void {
    this.recordingsService.getRecording(recordingId).subscribe(rec => {
      this.recordingSubject.next(rec);
    }, () => {
      this.loadingSubject.next(false);
      this.errorSubject.next(true);
    }, () => {
      this.loadingSubject.next(false);
    });
  }

  private formatDate(date: Date): string {
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
