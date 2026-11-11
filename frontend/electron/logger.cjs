const log = require('electron-log');
const path = require('path');

log.transports.file.resolvePath = () => 
    path.join(__dirname, '../../logs/lapagent_frontend.log');
module.exports = log;