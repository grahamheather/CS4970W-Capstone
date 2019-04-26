import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { map, mergeMap, delay } from 'rxjs/operators';
import { Recording } from '../models/recording';

@Injectable({
  providedIn: 'root'
})
export class RecordingsService {
  private baseUrl: string = 'http://ec2-18-222-77-3.us-east-2.compute.amazonaws.com';

  constructor(private http: HttpClient) { }

  getRecordingsByDevice(deviceId: string): Observable<Recording[]> {
    return this.http.get<Recording[]>(`${this.baseUrl}/devices/${deviceId}/recordings`)
        .pipe(
            map(recs => {
                recs.map(rec => {
                    let recording: Recording = {};
                    Object.assign(recording, rec);
                    if(rec.recordingTime) {
                        rec.recordingTime = new Date(rec.recordingTime);
                    }
                    if(rec.data) {
                        rec.data = JSON.parse(rec.data);
                    }
                    return recording;
                });
                return recs;
            })
        );
  }
}