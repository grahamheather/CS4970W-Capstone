import 'source-map-support/register';
import * as Debug from 'debug';
const debug = Debug(`${process.env.npm_package_name}:app`);
import express = require('express');
import path = require('path');
import swaggerUi = require('swagger-ui-express');
import * as swaggerDoc from './swagger.json';
import index from './routes/index';
import { DevicesController } from './routes/devices-controller';
import { Response, Request, NextFunction } from 'express';
import { TeamCatDataAccess } from './data-access/teamcat-data-access';
import { CatError } from 'models/cat-error';
import bodyParser = require('body-parser');
import { DeviceSettingsController } from './routes/device-settings-controller';
import { RecordingsController } from './routes/recordings-controller';
import { SpeakersController } from './routes/speakers-controller';

var app = express();
var teamcatDb = new TeamCatDataAccess();
var devicesController = new DevicesController(teamcatDb);
var deviceSettingsController = new DeviceSettingsController(teamcatDb);
var recordingsController = new RecordingsController(teamcatDb);
var speakersController = new SpeakersController(teamcatDb);

// view engine setup
app.set('views', path.join(__dirname, '../views'));
app.set('view engine', 'pug');

app.use(express.static(path.join(__dirname, '../public')));
app.use(bodyParser.urlencoded());

app.use('/', index);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDoc));
app.use('/devices/settings', deviceSettingsController.router);
app.use('/devices', devicesController.router);
app.use('/recordings', recordingsController.router);
app.use('/speakers', speakersController.router);

// catch 404 and forward to error handler
app.use((req: Request, res: Response, next: NextFunction) => {
    const error: CatError = {
        statusMessage: 'Not found',
        status: 404,
        error: new Error('Not found')
    }
    next(error);
});

app.use((err: CatError, req: Request, res: Response, next: NextFunction) => {
    debug(err.error);

    res.statusMessage = err.statusMessage || 'Internal server error';
    res.statusCode = err.status || 500;
    
    // Hide stacktrace in prod
    if (app.get('env') !== 'development') {
        err.error = {
            name: undefined,
            message: undefined
        }
    }

    if(req.method !== "GET" || !req.accepts('text/html')) {
        res.json({ message: err.message });
        return;
    }

    res.render('error', {
        title: process.env.npm_package_name, 
        browserRefreshUrl: process.env.BROWSER_REFRESH_URL,
        error: err
    });
});

app.set('port', process.env.PORT || 3000);

var server = app.listen(app.get('port'), () => {
    debug('Express server listening on port ' + server.address().port);
    if (process.send) {
        process.send('online');
    }
});
