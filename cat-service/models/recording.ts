import { RecordingData } from "./recording-data";

export interface Recording {
    recordingId?: string;
    deviceId?: string;
    speakerId?: string;
    settingsId?: string;
    recordingTime?: Date;
    data?: RecordingData;
}