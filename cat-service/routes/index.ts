import express = require('express');
const router = express.Router();

router.get('/', (req: express.Request, res: express.Response) => {
    res.render('index', { title: process.env.npm_package_name, browserRefreshUrl: process.env.BROWSER_REFRESH_URL });
});

export default router;