import { Request, Response, NextFunction } from 'express';
import { TeamCatDataAccess } from '../data-access/teamcat-data-access'
import * as Debug from 'debug';
import { BaseController } from './base-controller';
import { Device } from 'models/device';
import { DeviceSettings } from 'models/device-settings';
const debug = Debug(`${process.env.npm_package_name}:devices-controller`);

export class DevicesController extends BaseController {
    private readonly _teamcatDb: TeamCatDataAccess;

    constructor(teamcatDb: TeamCatDataAccess) {
        super();
        this._teamcatDb = teamcatDb;

        this.router.get('/', (req, res, next) => this.getDeviceByHandle(req, res, next));
        this.router.get('/', (req, res, next) => this.getDeviceByDate(req, res, next));
        this.router.get('/', (req, res, next) => this.getAllDevices(req, res, next));
        this.router.get('/:id', (req, res, next) => this.getDeviceById(req, res, next));
        this.router.get('/:id/settings', (req, res, next) => this.getDeviceSettingsByDevice(req, res, next));
        this.router.get('/:id/recordings', (req, res, next) => this.getRecordingsByDevice(req, res, next));
        this.router.get('/:id/speakers', (req, res, next) => this.getSpeakersByDevice(req, res, next));

        this.router.post('/', (req, res, next) => this.createDevice(req, res, next));

        this.router.patch('/:id', (req, res, next) => this.updateDevice(req, res, next));
        
        this.router.put('/:id/settings', (req, res, next) => this.updateDeviceSettings(req, res, next));

        this.router.delete('/:id', (req, res, next) => this.deleteDevice(req, res, next));

        this.setUpErrorHandlers();
    }

    private getSpeakersByDevice(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.getSpeakersByDevice(req.params.id)
            .subscribe(sp => {
                if(!sp) {
                    next(this.notFound({displayMessage: `No speaker found with id: ${req.params.id}`}));
                    return;
                }
                res.json(sp);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private getRecordingsByDevice(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.getRecordingsByDevice(req.params.id)
            .subscribe(rec => {
                if(!rec) {
                    next(this.notFound({displayMessage: `No recordings found with device id: ${req.params.id}`}));
                    return;
                }
                res.json(rec);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private updateDeviceSettings(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        let settingsProps;
        try {
            settingsProps = JSON.parse(req.body.settings);
        } catch(err){ 
            next(this.badRequest({displayMessage: 'Device settings must be valid JSON', error: err}));
            return;
        }

        const settings: DeviceSettings = {
            deviceId: req.params.id,
            properties: settingsProps
        }

        this._teamcatDb.updateDeviceSettings(settings)
            .subscribe(settings => {
                res.json(settings);
            }, err => {
                if(err.name === 'NotFoundError') {
                    next(this.notFound({error: err, displayMessage: err.message}));
                }
                next(this.internalServerError(err));
            });
    }

    private getDeviceSettingsByDevice(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.getDeviceSettingsByDevice(req.params.id)
            .subscribe(settings => {
                if(!settings) {
                    next(this.notFound({displayMessage: `No device settings found with id: ${req.params.id}`}));
                    return;
                }
                res.json(settings);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private deleteDevice(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.deleteDevice(req.params.id)
            .subscribe(() => {
                res.status(204);
                res.end();
            }, err => {
                if(err.name === 'NotFoundError') {
                    next(this.notFound({error: err, displayMessage: err.message}));
                }
                next(this.internalServerError(err));
            });
    }

    private updateDevice(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }
        if(req.body.handle && this.isWhitespace(req.body.handle)) {
            next(this.badRequest({displayMessage: 'Device handle cannot be whitespace'}));
            return;
        }

        const device: Device = {
            deviceId: req.params.id,
            handle: req.body.handle,
            description: req.body.description,
            location: req.body.location,
            ipAddress: req.body.ipAddress
        };

        this._teamcatDb.updateDevice(device)
            .subscribe(device => {
                res.json(device);
            }, err => {
                if(err.name === 'NotFoundError') {
                    next(this.notFound({error: err, displayMessage: err.message}));
                }
                next(this.internalServerError(err));
            });
    }

    private createDevice(req: Request, res: Response, next: NextFunction): void {
        if(!req.body.handle) {
            next();
            return;
        }
        if((req.body.handle as string).length > 50) {
            next(this.badRequest({displayMessage: 'Handle must be <= 50 characters'}));
            return;
        }
        if(this.isWhitespace(req.body.handle)) {
            next(this.badRequest({displayMessage: 'Device handle cannot be whitespace'}));
            return;
        }

        let settings;
        if(req.body.settings){
            try {
                settings = JSON.parse(req.body.settings);
            } catch(err){ 
                next(this.badRequest({displayMessage: 'Device settings must be valid JSON', error: err}));
                return;
            }
        }

        const device: Device = {
            handle: req.body.handle,
            description: req.body.description,
            location: req.body.location,
            ipAddress: req.body.ipAddress,
            settings: {
                properties: settings
            }
        };

        this._teamcatDb.insertDevice(device)
            .subscribe(device => {
                res.status(201);
                res.setHeader('Location', device.deviceId);
                res.json(device);
            }, err => {
                next(this.internalServerError(err));
            });
    }

    private getDeviceById(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.getDeviceById(req.params.id)
            .subscribe(device => {
                if(!device) {
                    next(this.notFound({displayMessage: `No device found with id: ${req.params.id}`}));
                    return;
                }
                res.json(device);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private getDeviceByDate(req: Request, res: Response, next: NextFunction): void {
        if(!req.query.afterDate && !req.query.beforeDate) {
            next();
            return;
        }
        const afterDate = req.query.afterDate ? new Date(req.query.afterDate) : null;
        if(afterDate && !this.validateDate(afterDate)) {
            next(this.badRequest({displayMessage: 'afterDate must be a valid date'}));
            return;
        }
        const beforeDate = req.query.beforeDate ? new Date(req.query.beforeDate) : null;
        if(beforeDate && !this.validateDate(beforeDate)) {
            next(this.badRequest({displayMessage: 'beforeDate must be a valid date'}));
            return;
        }
        
        this._teamcatDb.getDevicesByDate(afterDate, beforeDate)
            .subscribe(device => {
                res.json(device);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private getAllDevices(req: Request, res: Response, next: NextFunction): void {
        if(Object.keys(req.query).length !== 0) {
            next();
            return;
        }

        this._teamcatDb.getAllDevices()
            .subscribe(device => {
                res.json(device);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private getDeviceByHandle(req: Request, res: Response, next: NextFunction): void {
        if(!req.query.handle) {
            next();
            return;
        }
        if((req.query.handle as string).length > 50) {
            next(this.badRequest({displayMessage: 'Handle must be <= 50 characters'}));
            return;
        }
        if(Object.keys(req.query).length > 1) {
            next(this.badRequest({displayMessage: 'Other parameters not allowed when handle is set'}));
            return;
        }

        this._teamcatDb.getDevicesByHandle(req.query.handle)
            .subscribe(device => {
                res.json(device);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }
}