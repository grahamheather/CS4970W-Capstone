import * as Debug from 'debug';
import { BaseController } from './base-controller';
import { TeamCatDataAccess } from 'data-access/teamcat-data-access';
import { Request, Response, NextFunction } from 'express';
import { Recording } from 'models/recording';
import { RecordingData } from 'models/recording-data';
const debug = Debug(`${process.env.npm_package_name}:recordings-controller`);

export class RecordingsController extends BaseController {
    private readonly _teamcatDb: TeamCatDataAccess;

    constructor(teamcatDb: TeamCatDataAccess) {
        super();
        this._teamcatDb = teamcatDb;

        this.router.get('/', (req, res, next) => this.getRecordingsByDate(req, res, next));
        this.router.get('/', (req, res, next) => this.getAllRecordings(req, res, next));
        this.router.get('/:id', (req, res, next) => this.getRecordingById(req, res, next));

        this.router.post('/', (req, res, next) => this.createRecording(req, res, next));

        this.router.delete('/:id', (req, res, next) => this.deleteRecording(req, res, next));

        this.setUpErrorHandlers();
    }

    private getRecordingsByDate(req: Request, res: Response, next: NextFunction): void {
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
        
        this._teamcatDb.getRecordingsByDate(afterDate, beforeDate)
            .subscribe(rec => {
                res.json(rec);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private getAllRecordings(req: Request, res: Response, next: NextFunction): void {
        if(Object.keys(req.query).length !== 0) {
            next();
            return;
        }

        this._teamcatDb.getAllRecordings()
            .subscribe(rec => {
                res.json(rec);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private getRecordingById(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.getRecordingById(req.params.id)
            .subscribe(rec => {
                if(!rec) {
                    next(this.notFound({displayMessage: `No recording found with id: ${req.params.id}`}));
                    return;
                }
                res.json(rec);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private createRecording(req: Request, res: Response, next: NextFunction): void {
        if(!req.body.data || !req.body.deviceId || !req.body.recordingTime || !req.body.settingsId) {
            next();
            return;
        }
        if(!this.validateUuid(req.body.deviceId)) {
            next(this.badRequest({displayMessage: 'deviceId must be a valid UUID'}));
            return;
        }
        if(!this.validateUuid(req.body.settingsId)) {
            next(this.badRequest({displayMessage: 'settingsId must be a valid UUID'}));
            return;
        }
        const recordingTime = req.body.recordingTime ? new Date(req.body.recordingTime) : null;
        if(recordingTime && !this.validateDate(recordingTime)) {
            next(this.badRequest({displayMessage: 'recordingTime must be a valid date'}));
            return;
        }

        let data: RecordingData;
        try {
            data = JSON.parse(req.body.data);
        } catch(err){ 
            next(this.badRequest({displayMessage: 'Recording data must be valid JSON', error: err}));
            return;
        }

        const recording: Recording = {
            deviceId: req.body.deviceId,
            recordingTime: req.body.recordingTime,
            settingsId: req.body.settingsId,
            speakerId: req.body.speakerId,
            data: data
        };

        this._teamcatDb.insertRecording(recording)
            .subscribe(rec => {
                res.status(201);
                res.setHeader('Location', rec.recordingId);
                res.json(rec);
            }, err => {
                next(this.internalServerError(err));
            });
    }

    private deleteRecording(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.deleteRecording(req.params.id)
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
}