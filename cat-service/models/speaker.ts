import { SpeakerData } from "./speaker-data";

export interface Speaker {
    speakerId?: string;
    deviceId?: string;
    createdDate?: Date;
    data?: SpeakerData;
}