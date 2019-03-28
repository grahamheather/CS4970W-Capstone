import { Device } from './device';

export interface DeviceCard {
    device: Device;
    showSettings?: boolean;
    editing?: DeviceCard;
}