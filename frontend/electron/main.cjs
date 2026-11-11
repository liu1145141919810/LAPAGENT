const { app, BrowserWindow } = require('electron');
const path = require('path');
const {
  startBackend,stopBackend
} = require('./backendManager.cjs')
const log = require('./logger.cjs');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,

    icon: path.join(__dirname, '..', 'asset', 'icon.png'),
  });

  win.loadFile(path.join(__dirname, '..', 'sources', 'HTML', 'index.html'));
}
app.whenReady().then(async () => {
  try {
    await startBackend();
    log.info('Starting backend...');
    createWindow();
  } catch(error){
    app.quit();
  }
});
app.on('before-quit', async () => {
  try {
    await stopBackend();
  } catch(error){
    log.error('Failed to stop backend:', error);
  }
});