import mariadb = require('mariadb');
import * as Debug from 'debug';
import { Device } from 'models/device';
import { Observable, from, of } from 'rxjs';
import { mergeMap, map, finalize, tap, catchError, retry } from 'rxjs/operators';
import { DeviceSettings } from 'models/device-settings';
import { Recording } from 'models/recording';
import { Speaker } from 'models/speaker';
const debug = Debug(`${process.env.npm_package_name}:teamcat-data-access`);

export class TeamCatDataAccess {
    private _pool = mariadb.createPool({ 
        host: 'teamcat.cjmsq3fjput7.us-east-2.rds.amazonaws.com', 
        database: 'teamcat',
        user: 'teamcatmaster',
        password: process.env.TeamcatDbPw, 
        connectionLimit: 5
    });

    constructor() {
        this.testConn();
    }

    private getConn(): Observable<any> {
        return from(this._pool.getConnection());
    }

    private callStoredProc(procDef: string, params: any[]): Observable<any> {
        const query = `CALL ${procDef}`;
        return this.getConn()
            .pipe(
                mergeMap(conn => from(conn.query(query, params))
                    .pipe(
                        finalize(conn.end)
                    )
                )
            );
    }

    private mapSpeakers(results: Array<Array<any>>): Speaker[] {
        return results[0].map(elem => {
            const speaker: Speaker = {
                speakerId:      elem.speaker_id,
                deviceId:       elem.device_id,
                createdDate:    elem.created_date,
                data:           elem.json_data
            }
            return speaker;
        });
    }

    private mapRecordings(results: Array<Array<any>>): Recording[] {
        return results[0].map(elem => {
            const recording: Recording = {
                recordingId:    elem.recording_id,
                deviceId:       elem.device_id,
                speakerId:      elem.speaker_id,
                settingsId:     elem.settings_id,
                recordingTime:  elem.recording_time,
                data:           elem.json_data
            };
            return recording;
        });
    }

    private mapDevices(results: Array<Array<any>>): Device[] {
        return results[0].map(elem => {
            const device: Device = {
                deviceId:    elem.device_id,
                handle:      elem.handle,
                createdDate: elem.created_date,
                description: elem.description,
                location:    elem.location,
                ipAddress:   elem.ip_address,
                settings: {
                    createdDate: elem.settings_created_date,
                    deviceId: elem.device_id,
                    settingsId: elem.settings_id,
                    properties: elem.json_settings
                }
            };
            return device;
        });
    }

    private mapDeviceSettings(results: Array<Array<any>>): DeviceSettings[] {
        return results[0].map(elem => {
            const settings: DeviceSettings = {
                deviceId:       elem.device_id,
                createdDate:    elem.created_date,
                settingsId:     elem.settings_id,
                properties:     elem.json_settings
            };
            return settings;
        });
    }

    testConn(): void {
        this.getConn().subscribe(conn => {
            debug('Connected to database successfully!');
            conn.end();
        }, err => {
            debug('Could not connect to database: \n', err);
        });
    }

    getDeviceById(deviceId: string): Observable<Device> {
        return this.callStoredProc('p_get_device(?)', [deviceId])
            .pipe(
                map(res => this.mapDevices(res)[0] || null)
            );
    }

    getDevicesByDate(afterDate?: Date, beforeDate?: Date): Observable<Device[]> {
        return this.callStoredProc('p_get_device_by_date(?,?)', [afterDate || null, beforeDate || null])
            .pipe(
                map(this.mapDevices)
            );
    }

    getAllDevices(): Observable<Device[]> {
        return this.callStoredProc('p_get_all_devices', [])
            .pipe(
                map(this.mapDevices)
            );
    }

    getDevicesByHandle(handle: string): Observable<Device[]> {
        return this.callStoredProc('p_get_device_by_handle(?)', [handle])
            .pipe(
                map(this.mapDevices)
            );
    }

    insertDevice(device: Device): Observable<Device> {
        return this.callStoredProc('p_insert_device(?,?,?,?,?)', [
            device.handle, 
            device.description || null, 
            device.location || null,
            device.ipAddress || null,
            device.settings.properties || null
        ]).pipe(
            map(res => {
                device.deviceId = res[0][0].device_id;
                device.createdDate = res[0][0].created_date;
                if(!device.settings) {
                    device.settings = { };
                }
                device.settings.deviceId = res[0][0].device_id;
                device.settings.settingsId = res[0][0].settings_id;
                device.settings.createdDate = res[0][0].created_date;
                return device;
            })
        );
    }

    updateDevice(device: Device): Observable<Device> {
        return this.callStoredProc('p_update_device(?,?,?,?,?)', [
            device.deviceId,
            device.handle || null,
            device.description || null,
            device.location || null,
            device.ipAddress || null
        ]).pipe(
            map(res => {
                if(!res.affectedRows) {
                    const error = new Error(`No device found with id: ${device.deviceId}`);
                    error.name = "NotFoundError";
                    throw error;
                }
                return device;
            })
        );
    }

    deleteDevice(deviceId: string): Observable<Device> {
        return this.callStoredProc('p_delete_device(?)', [deviceId])
            .pipe(
                map(res => {
                    if(!res.affectedRows) {
                        const error = new Error(`No device found with id: ${deviceId}`);
                        error.name = "NotFoundError";
                        throw error;
                    }
                    return null;
                })
            );
    }

    getDeviceSettingsById(settingsId: string): Observable<DeviceSettings> {
        return this.callStoredProc('p_get_device_settings(?)', [settingsId])
            .pipe(
                map(res => this.mapDeviceSettings(res)[0] || null)
            );
    }

    getDeviceSettingsByDevice(deviceId: string): Observable<DeviceSettings[]> {
        return this.callStoredProc('p_get_device_settings_by_device(?)', [deviceId])
            .pipe(
                map(this.mapDeviceSettings)
            );
    }

    getAllDeviceSettings(): Observable<DeviceSettings[]> {
        return this.callStoredProc('p_get_all_device_settings', [])
            .pipe(
                map(this.mapDeviceSettings)
            );
    }

    updateDeviceSettings(settings: DeviceSettings): Observable<DeviceSettings> {
        return this.callStoredProc('p_update_device_settings(?,?)', [settings.deviceId, settings.properties || null])
            .pipe(
                map(res => {
                    if(!res[0][0].created_date) {
                        const error = new Error(`No device found with id: ${settings.deviceId}`);
                        error.name = "NotFoundError";
                        throw error;
                    }
                    settings.settingsId = res[0][0].settings_id;
                    settings.createdDate = res[0][0].created_date;
                    return settings;
                })
            );
    }

    getAllRecordings(): Observable<Recording[]> {
        return this.callStoredProc('p_get_all_recordings', [])
            .pipe(
                map(this.mapRecordings)
            );
    }

    getRecordingsByDate(afterDate?: Date, beforeDate?: Date): Observable<Recording[]> {
        return this.callStoredProc('p_get_recordings_by_date(?,?)', [afterDate || null, beforeDate || null])
            .pipe(
                map(this.mapRecordings)
            );
    }

    getRecordingById(recordingId: string): Observable<Recording> {
        return this.callStoredProc('p_get_recordings(?)', [recordingId])
            .pipe(
                map(res => this.mapRecordings(res)[0] || null)
            );
    }

    insertRecording(recording: Recording): Observable<Recording> {
        return this.callStoredProc('p_insert_recording(?,?,?,?,?)', [
            recording.deviceId || null, 
            recording.speakerId || null, 
            recording.settingsId || null,
            recording.recordingTime || null,
            recording.data || null
        ]).pipe(
            map(res => {
                recording.recordingId = res[0][0].recording_id;
                recording.recordingTime = res[0][0].recording_time;
                return recording;
            })
        );
    }

    deleteRecording(recordingId: string): Observable<Recording> {
        return this.callStoredProc('p_delete_recording(?)', [recordingId])
            .pipe(
                map(res => {
                    if(!res.affectedRows) {
                        const error = new Error(`No recording found with id: ${recordingId}`);
                        error.name = "NotFoundError";
                        throw error;
                    }
                    return null;
                })
            );
    }

    getRecordingsByDevice(deviceId: string): Observable<Recording[]> {
        return this.callStoredProc('p_get_recordings_by_device(?)', [deviceId])
            .pipe(
                map(this.mapRecordings)
            );
    }

    getAllSpeakers(): Observable<Speaker[]> {
        return this.callStoredProc('p_get_all_speakers', [])
            .pipe(
                map(this.mapSpeakers)
            );
    }

    getSpeakersByDate(afterDate?: Date, beforeDate?: Date): Observable<Speaker[]> {
        return this.callStoredProc('p_get_speakers_by_date(?,?)', [afterDate || null, beforeDate || null])
            .pipe(
                map(this.mapSpeakers)
            );
    }

    getSpeakerById(speakerId: string): Observable<Speaker> {
        return this.callStoredProc('p_get_speakers(?)', [speakerId])
            .pipe(
                map(res => this.mapSpeakers(res)[0] || null)
            );
    }

    deleteSpeaker(speakerId: string): Observable<Speaker> {
        return this.callStoredProc('p_delete_speaker(?)', [speakerId])
            .pipe(
                map(res => {
                    if(!res.affectedRows) {
                        const error = new Error(`No speaker found with id: ${speakerId}`);
                        error.name = "NotFoundError";
                        throw error;
                    }
                    return null;
                })
            );
    }

    insertSpeaker(speaker: Speaker): Observable<Speaker> {
        return this.callStoredProc('p_insert_recording(?,?)', [
            speaker.deviceId, 
            speaker.data || null
        ]).pipe(
            map(res => {
                speaker.speakerId = res[0][0].speaker_id;
                speaker.createdDate = res[0][0].created_date;
                return speaker;
            })
        );
    }

    updateSpeaker(speaker: Speaker): Observable<Speaker> {
        return this.callStoredProc('p_update_speakers(?,?)', [
            speaker.speakerId, 
            speaker.data || null
        ]).pipe(
            map(res => {
                if(!res.affectedRows) {
                    const error = new Error(`No device found with id: ${speaker.speakerId}`);
                    error.name = "NotFoundError";
                    throw error;
                }
                return speaker;
            })
        );
    }

    getRecordingsBySpeaker(speakerId: string): Observable<Recording[]> {
        return this.callStoredProc('p_get_recordings_by_speaker(?)', [speakerId])
            .pipe(
                map(this.mapRecordings)
            );
    }

    getSpeakersByDevice(deviceId: string): Observable<Speaker[]> {
        return this.callStoredProc('p_get_speakers_by_device(?)', [deviceId])
            .pipe(
                map(this.mapSpeakers)
            );
    }
}