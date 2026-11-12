const { app, BrowserWindow } = require('electron');
const path = require('path');
const {
  startBackend,stopBackend
} = require('./backendManager.cjs')
const log = require('./logger.cjs');

let isQuitting = false;
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

app.on('before-quit', async (event) => {
  if (isQuitting) {
    return;
  }
  event.preventDefault();
  isQuitting = true;
  try {
    await stopBackend();
    log.info("Backend stopped successfully.");
  } catch(error){
    log.error('Failed to stop backend:', error);
  } finally {
    app.exit(0);
  }
});