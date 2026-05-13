import path from 'node:path'
import started from 'electron-squirrel-startup'
import { ipcMain } from 'electron'
import { app, BrowserWindow } from 'electron'
import { initDb, db, getProfiles, addProfile, deleteProfile } from './database.js'

if (started) {
  app.quit();
}

const createWindow = () => {

  const preloadPath = path.join(app.getAppPath(), '.vite/build/preload.js');
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: preloadPath, 
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`));
  }

  /* Open the DevTools.
  mainWindow.webContents.openDevTools(); */
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {

  initDb()
  createWindow()

  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.

ipcMain.handle('get-profiles', async () => {
    const profileList = getProfiles()
    return profileList
})

ipcMain.handle('add-profile', async (event, name) => {
    const newProfile = addProfile(name)
    return newProfile
})

ipcMain.handle('delete-profile', async (event, name) => {
    const currentProfile = deleteProfile(name)
    return currentProfile
})

ipcMain.on('open-profile-page', () => {

  const preloadPath = path.join(app.getAppPath(), '.vite/build/preload.js');
  const profileWindow = new BrowserWindow({
    width: 400,
    height: 600,
    resizable: false,
    title: "Select Profile",
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    profileWindow.loadURL(`${MAIN_WINDOW_VITE_DEV_SERVER_URL}#profiles`);
  } else {
    profileWindow.loadFile(path.join(app.getAppPath(), `.vite/renderer/${MAIN_WINDOW_VITE_NAME}/index.html`), {
      hash: 'profiles'
    })
  }
})