import { Request, Response, NextFunction } from 'express';
import { TeamCatDataAccess } from '../data-access/teamcat-data-access'
import * as Debug from 'debug';
import { BaseController } from './base-controller';
import { SpeakerData } from 'models/speaker-data';
import { Speaker } from 'models/speaker';
const debug = Debug(`${process.env.npm_package_name}:speakers-controller`);

export class SpeakersController extends BaseController {
    private readonly _teamcatDb: TeamCatDataAccess;

    constructor(teamcatDb: TeamCatDataAccess) {
        super();
        this._teamcatDb = teamcatDb;

        this.router.get('/', (req, res, next) => this.getSpeakersByDate(req, res, next));
        this.router.get('/', (req, res, next) => this.getAllSpeakers(req, res, next));
        this.router.get('/:id', (req, res, next) => this.getSpeakerById(req, res, next));
        this.router.get('/:id/recordings', (req, res, next) => this.getRecordingsBySpeaker(req, res, next));

        this.router.delete('/:id', (req, res, next) => this.deleteSpeaker(req, res, next));

        this.router.put('/:id', (req, res, next) => this.updateSpeaker(req, res, next));

        this.router.post('/', (req, res, next) => this.createSpeaker(req, res, next));

        this.setUpErrorHandlers();
    }

    private getAllSpeakers(req: Request, res: Response, next: NextFunction): void {
        this._teamcatDb.getAllSpeakers()
            .subscribe(speaker => {
                res.json(speaker);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private getSpeakersByDate(req: Request, res: Response, next: NextFunction): void {
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
        
        this._teamcatDb.getSpeakersByDate(afterDate, beforeDate)
            .subscribe(sp => {
                res.json(sp);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }

    private getSpeakerById(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.getSpeakerById(req.params.id)
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

    private deleteSpeaker(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.deleteSpeaker(req.params.id)
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

    private createSpeaker(req: Request, res: Response, next: NextFunction): void {
        if(!req.body.speakerId || !req.body.data) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.speakerId)) {
            next(this.badRequest({displayMessage: 'deviceId must be a valid UUID'}));
            return;
        }

        let data: SpeakerData;
        try {
            data = JSON.parse(req.body.data);
        } catch(err){ 
            next(this.badRequest({displayMessage: 'Speaker data must be valid JSON', error: err}));
            return;
        }

        const speaker: Speaker = {
            speakerId: req.body.speakerId,
            data: data
        };

        this._teamcatDb.insertSpeaker(speaker)
            .subscribe(sp => {
                res.status(201);
                res.setHeader('Location', sp.speakerId);
                res.json(sp);
            }, err => {
                next(this.internalServerError(err));
            });
    }

    private updateSpeaker(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        let data;
        try {
            data = JSON.parse(req.body.data);
        } catch(err){ 
            next(this.badRequest({displayMessage: 'Speaker data must be valid JSON', error: err}));
            return;
        }

        const speaker: Speaker = {
            speakerId: req.params.id,
            data: data
        }

        this._teamcatDb.updateSpeaker(speaker)
            .subscribe(sp => {
                res.json(sp);
            }, err => {
                if(err.name === 'NotFoundError') {
                    next(this.notFound({error: err, displayMessage: err.message}));
                }
                next(this.internalServerError(err));
            });
    }

    private getRecordingsBySpeaker(req: Request, res: Response, next: NextFunction): void {
        if(!req.params.id) {
            next();
            return;
        }
        if(!this.validateUuid(req.params.id)) {
            next(this.badRequest({displayMessage: 'Id must be a valid UUID'}));
            return;
        }

        this._teamcatDb.getRecordingsBySpeaker(req.params.id)
            .subscribe(rec => {
                if(!rec) {
                    next(this.notFound({displayMessage: `No recordings found with speaker id: ${req.params.id}`}));
                    return;
                }
                res.json(rec);
            }, (err: Error) => {
                next(this.internalServerError({error: err}));
            });
    }
}