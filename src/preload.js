const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  openProfilePage: () => ipcRenderer.send('open-profile-page'),
  getProfiles: () => ipcRenderer.invoke('get-profiles'),
  getTags: (query) => ipcRenderer.invoke('get-tags', query)
});

