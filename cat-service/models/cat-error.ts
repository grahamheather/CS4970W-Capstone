export interface CatError {
    statusMessage: string;
    status: number;
    message?: string;
    error: Error;
}
