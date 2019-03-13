import { DeviceSettings } from "./device-settings";

export interface Device {
    deviceId?: string;
    handle?: string;
    createdDate?: Date;
    description?: string;
    location?: string;
    ipAddress?: string;
    settings?: DeviceSettings;
}