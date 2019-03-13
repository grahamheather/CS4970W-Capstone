import { CatError } from "models/cat-error";
import { Request, Response, NextFunction, Router } from "express";

export abstract class BaseController {
    private readonly uuidPattern = new RegExp('^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', 'i');
    readonly router: Router = Router();

    protected validateUuid(uuid: string): boolean {
        return this.uuidPattern.test(uuid);
    }

    protected validateDate(date: Date): boolean {
        return !isNaN(date.valueOf());
    }

    protected isWhitespace(string: string): boolean {
        return string.trim() === "";
    }

    protected require(...params: any[]): boolean {
        return params.every(val => val != null);
    }

    protected setUpErrorHandlers(): void {
        this.router.use('/', (req, res, next) => this.handleBadRequest(req, res, next));
        this.router.use('/', (error, req, res, next) => this.handleError(error, req, res, next));
    }

    private handleBadRequest(req: Request, res: Response, next: NextFunction): void {
        next(this.badRequest({error: new Error('Bad request')}));
    }

    private handleError(err: any, req: Request, res: Response, next: NextFunction): void {
        if((err as CatError).statusMessage) {
            next(err);
            return;
        }
        next(this.internalServerError({error: err}));
    }

    protected notFound(params: {error?: Error, displayMessage?: string}): CatError {
        const error: CatError = {
            statusMessage: 'Not found',
            status: 404,
            message: params.displayMessage,
            error: params.error || new Error(params.displayMessage || 'Not found')
        }
        return error;
    }

    protected badRequest(params: {error?: Error, displayMessage?: string}): CatError {
        const error: CatError = {
            statusMessage: 'Bad request',
            status: 400,
            message: params.displayMessage,
            error: params.error || new Error(params.displayMessage || 'Bad request')
        }
        return error;
    }

    protected internalServerError(params: {error?: Error, displayMessage?: string}): CatError {
        const error: CatError = {
            statusMessage: 'Internal server error',
            status: 500,
            message: params.displayMessage,
            error: params.error || new Error(params.displayMessage || 'Internal server error')
        }
        return error;
    }
}