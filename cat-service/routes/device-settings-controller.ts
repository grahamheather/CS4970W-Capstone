import { Request, Response, NextFunction } from 'express';
import { TeamCatDataAccess } from '../data-access/teamcat-data-access'
import * as Debug from 'debug';
import { BaseController } from './base-controller';
import { Device } from 'models/device';
import { DeviceSettings } from 'models/device-settings';
const debug = Debug(`${process.env.npm_package_name}:device-settings-controller`);

export class DeviceSettingsController extends BaseController {
    private readonly _teamcatDb: TeamCatDataAccess;

    constructor(teamcatDb: TeamCatDataAccess) {
        super();
        this._teamcatDb = teamcatDb;

        this.router.get('/', (req, res, next) => this.getAllDeviceSettings(req, res, next));
        this.router.get('/:id', (req, res, next) => this.getDeviceSettingsById(req, res, next));

        this.setUpErrorHandlers();
    }

    private getAllDeviceSettings(req: Request, res: Response, next: NextFunction): void {
        this._teamcatDb.getAllDeviceSettings()
            .subscribe(settings => {
                res.json(settings);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private getDeviceSettingsById(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.getDeviceSettingsById(req.params.id)
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
}
