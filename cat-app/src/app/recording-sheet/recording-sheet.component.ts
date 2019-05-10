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
  private recordingSubject: BehaviorSubject<Recording> = new BehaviorSubject<Recording>(null);
  recording$: Observable<Recording> = this.recordingSubject.asObservable();

  constructor(private recordingsService: RecordingsService) {}

  ngOnInit() {
  }

  // TODO: need loading bar
  getRecording(recordingId: string): void {
    this.recordingsService.getRecording(recordingId).subscribe(rec => {
      this.recordingSubject.next(rec);
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
