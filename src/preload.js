const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  openProfilePage: () => ipcRenderer.send('open-profile-page'),
  getProfiles: () => ipcRenderer.invoke('get-profiles'),
  addProfile: (name) => ipcRenderer.invoke('add-profile', name),
  deleteProfile: (name) => ipcRenderer.invoke('delete-profile', name),
})