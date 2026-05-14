const { contextBridge, ipcRenderer } = require('electron');


contextBridge.exposeInMainWorld('electron', {
  openProfilePage: () => ipcRenderer.send('open-profile-page'),
  closeProfilePage: () => ipcRenderer.send('close-profile-page'),
  db: (type, info) => ipcRenderer.invoke('db-query', { type, info })
})