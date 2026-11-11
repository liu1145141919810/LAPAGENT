const { spawn } = require('child_process');
const path = require('path');
const log = require('./logger.cjs');

let backendStatus = "Stopped";
let composeProcess = null;
let composePromise = null;

const BACKEND_DIR = path.resolve(__dirname, '../../backend');

async function runCompose(args, action) {
    const child = spawn(
        'docker',
        ['compose', ...args],
        {
            cwd: BACKEND_DIR,
            stdio: ['ignore', 'pipe', 'pipe']
        }
    );
    composeProcess = child;
    child.stdout.on('data', data => {
        log.info(`Compose stdout: ${data.toString().trimEnd()}`);
    });
    child.stderr.on('data', data => {
        log.warn(`Compose stderr: ${data.toString().trimEnd()}`);
    });
    const operation = new Promise((resolve, reject) => {
        child.once('error', error => {
            reject(error);
        });

        child.once('close', (code, signal) => {
            if (code === 0) {
                resolve(code);
            } else {
                reject(new Error(
                    `Compose exited with code ${code}, signal=${signal}`
                ));
            }
        });
    });
    composePromise = operation;
    try {
        const code = await operation;
        return code;
    } catch (error) {
        log.error(`Failed to ${action} backend:`, error);
        throw error;
    } finally {
        if (composeProcess === child) {
            composeProcess = null;
        }
        if (composePromise === operation) {
            composePromise = null;
        }
    }
}

async function startBackend() {
    if (backendStatus === "Started") {
        log.info('Backend is already running.');
        return;
    }
    try {
        await runCompose(['up', '-d'], 'start');
        backendStatus = "Started";
    } catch (error) {
        backendStatus = "Stopped";
        throw error;
    }
}

async function stopBackend() {
    if (composePromise) {
        try {
            await composePromise;
        } catch (error) {
            log.warn('Previous Docker Compose operation failed:', error);
        }
    }
    if (composeProcess) {
        throw new Error('Docker Compose operation is still running');
    }
    try {
        await runCompose(['down', '--timeout', '10'], 'stop');
        backendStatus = "Stopped";
    } catch (error) {
        throw error;
    }
}
module.exports = { startBackend, stopBackend };