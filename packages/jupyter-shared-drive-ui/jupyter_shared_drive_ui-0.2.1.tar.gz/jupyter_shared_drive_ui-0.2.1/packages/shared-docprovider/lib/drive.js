// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
import { PromiseDelegate } from '@lumino/coreutils';
import { WebrtcProvider as YWebrtcProvider } from 'y-webrtc';
import { Signal } from '@lumino/signaling';
import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { WebrtcProvider } from './provider';
import { Path } from './path';
import { YDrive } from './ydrive';
import { IndexeddbPersistence } from 'y-indexeddb';
const signalingServers = JSON.parse(PageConfig.getOption('signalingServers'));
/**
 * A collaborative implementation for an `IDrive`, talking to other peers using WebRTC.
 */
export class SharedDrive {
    /**
     * Construct a new drive object.
     *
     * @param user - The user manager to add the identity to the awareness of documents.
     */
    constructor(app, defaultFileBrowser, translator, globalAwareness, name) {
        this._onSync = (synced) => {
            if (synced.synced) {
                this._ready.resolve();
                this._fileSystemProvider?.off('synced', this._onSync);
            }
        };
        this._onCreate = (options) => {
            if (typeof options.format !== 'string') {
                const factory = this.sharedModelFactory.documentFactories.get(options.contentType);
                const sharedModel = factory(options);
                return sharedModel;
            }
            const fileId = this._ydrive.getId(options.path);
            const key = `${options.format}:${options.contentType}:${fileId}`;
            // Check if shared model alread exists.
            const fileProvider = this._fileProviders.get(key);
            if (fileProvider) {
                return fileProvider.sharedModel;
            }
            const factory = this.sharedModelFactory.documentFactories.get(options.contentType);
            const sharedModel = factory(options);
            sharedModel.changed.connect((_, event) => {
                if (!event.stateChange) {
                    sharedModel.ystate.set('dirty', false);
                }
            });
            const provider = new WebrtcProvider({
                url: '',
                path: fileId,
                format: options.format,
                contentType: options.contentType,
                model: sharedModel,
                user: this._user,
                translator: this._trans,
                signalingServers: this._signalingServers
            });
            this._fileProviders.set(key, { provider, sharedModel });
            sharedModel.disposed.connect(() => {
                const fileProvider = this._fileProviders.get(key);
                if (fileProvider) {
                    fileProvider.provider.dispose();
                    this._fileProviders.delete(key);
                }
            });
            const indexeddbProvider = new IndexeddbPersistence(fileId, sharedModel.ydoc);
            indexeddbProvider.on('synced', () => {
                console.log(`content from the database is loaded for: ${fileId}`);
            });
            return sharedModel;
        };
        this._fileChanged = new Signal(this);
        this._isDisposed = false;
        this._ydrive = new YDrive();
        this._ready = new PromiseDelegate();
        this._signalingServers = [];
        this._user = app.serviceManager.user;
        this._defaultFileBrowser = defaultFileBrowser;
        this._trans = translator;
        this._globalAwareness = globalAwareness;
        //this._username = this._globalAwareness?.getLocalState()?.user.identity.name;
        //this._username = this._globalAwareness?.getLocalState()?.username;
        this._fileProviders = new Map();
        this.sharedModelFactory = new SharedModelFactory(this._onCreate);
        this.serverSettings = ServerConnection.makeSettings();
        signalingServers.forEach((url) => {
            if (url.startsWith('ws://') ||
                url.startsWith('wss://') ||
                url.startsWith('http://') ||
                url.startsWith('https://')) {
                // It's an absolute URL, keep it as-is.
                this._signalingServers.push(url);
            }
            else {
                // It's a Jupyter server relative URL, build the absolute URL.
                this._signalingServers.push(URLExt.join(this.serverSettings.wsUrl, url));
            }
        });
        this.name = name;
        this._app = app;
        this._fileSystemProvider = new YWebrtcProvider('fileSystem', this._ydrive.ydoc, {
            signaling: this._signalingServers,
            awareness: this._globalAwareness || undefined
        });
        this._fileSystemProvider.on('synced', this._onSync);
        const indexeddbProvider = new IndexeddbPersistence('', this._ydrive.ydoc);
        indexeddbProvider.on('synced', () => {
            console.log('content from the database is loaded for file system');
        });
    }
    //get providers(): Map<string, WebrtcProvider> {
    get providers() {
        // FIXME
        const providers = new Map();
        for (const key in this._fileProviders) {
            providers.set(key, this._fileProviders.get(key).provider);
        }
        return providers;
    }
    async getDownloadUrl(path) {
        return '';
    }
    async delete(localPath) {
        this._ydrive.delete(localPath);
    }
    async restoreCheckpoint(path, checkpointID) { }
    async deleteCheckpoint(path, checkpointID) { }
    async exportFile(toPath) {
        const _fromPath = this._app.shell.currentWidget.context.contentsModel.path.slice(this.name.length + 1);
        const type = this._app.shell.currentWidget.context.contentsModel
            .type;
        const format = this._app.shell.currentWidget.context.contentsModel.format ??
            'text';
        const fileId = this._ydrive.getId(_fromPath);
        const key = `${format}:${type}:${fileId}`;
        const fileProvider = this._fileProviders.get(key);
        const content = fileProvider?.sharedModel.getSource();
        if (fileProvider) {
            const options = {
                type,
                format,
                content
            };
            await this._defaultFileBrowser.model.manager.services.contents.save(toPath, options);
        }
    }
    async importFile(fromPath, toPath) {
        const model = await this._defaultFileBrowser.model.manager.services.contents.get(fromPath, {
            content: true
        });
        if (this._ydrive.exists(toPath) && this._ydrive.isDir(toPath)) {
            if (toPath === '') {
                toPath = model.name;
            }
            else {
                toPath = toPath + '/' + model.name;
            }
        }
        this._ydrive.createFile(toPath);
        const sharedModel = this.sharedModelFactory.createNew({
            path: toPath,
            format: model.format,
            contentType: model.type,
            collaborative: true
        });
        if (sharedModel) {
            sharedModel.setSource(model.content);
        }
    }
    async newUntitled(options = {}) {
        let ext = '';
        let isDir = false;
        if (options.type === 'directory') {
            isDir = true;
        }
        else if (options.type === 'notebook') {
            ext = '.ipynb';
        }
        else {
            ext = '.txt';
        }
        const newPath = this._ydrive.newUntitled(isDir, options.path, ext);
        const newName = new Path(newPath).name;
        const model = {
            name: newName,
            path: newPath,
            type: options.type ?? 'file',
            writable: true,
            created: '',
            last_modified: '',
            mimetype: '',
            content: null,
            format: null
        };
        this._fileChanged.emit({
            type: 'new',
            oldValue: null,
            newValue: model
        });
        return model;
    }
    async rename(path, newPath) {
        this._ydrive.move(path, newPath);
        const model = {
            name: new Path(newPath).name,
            path: newPath,
            type: 'file',
            writable: true,
            created: '',
            last_modified: '',
            mimetype: '',
            content: null,
            format: null
        };
        return model;
    }
    async copy(path, toDir) {
        throw new Error('Copy/paste not supported');
    }
    async createCheckpoint(path) {
        return {
            id: '',
            last_modified: ''
        };
    }
    async listCheckpoints(path) {
        return [];
    }
    /**
     * A signal emitted when a file operation takes place.
     */
    get fileChanged() {
        return this._fileChanged;
    }
    /**
     * Test whether the manager has been disposed.
     */
    get isDisposed() {
        return this._isDisposed;
    }
    /**
     * Dispose of the resources held by the manager.
     */
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this._fileProviders.forEach(fp => fp.provider.dispose());
        this._fileProviders.clear();
        this._isDisposed = true;
        Signal.clearData(this);
    }
    /**
     * Get a file or directory.
     *
     * @param localPath: The path to the file.
     *
     * @param options: The options used to fetch the file.
     *
     * @returns A promise which resolves with the file content.
     */
    async get(localPath, options) {
        let model;
        await this._ready;
        if (!this._ydrive.isDir(localPath)) {
            // It's a file.
            return {
                name: new Path(localPath).name,
                path: localPath,
                type: 'file',
                writable: true,
                created: '',
                last_modified: '',
                mimetype: '',
                content: null,
                format: null
            };
        }
        // It's a directory.
        const content = [];
        for (const [name, info] of this._ydrive.listDir(localPath)) {
            const type = info.isDir ? 'directory' : 'file';
            content.push({
                name,
                path: `${localPath}/${name}`,
                type,
                writable: true,
                created: '',
                last_modified: '',
                mimetype: '',
                content: null,
                format: null
            });
        }
        model = {
            name: new Path(localPath).name,
            path: localPath,
            type: 'directory',
            writable: true,
            created: '',
            last_modified: '',
            mimetype: '',
            content,
            format: null
        };
        return model;
    }
    /**
     * Save a file.
     *
     * @param localPath - The desired file path.
     *
     * @param options - Optional overrides to the model.
     *
     * @returns A promise which resolves with the file content model when the
     *   file is saved.
     */
    async save(localPath, options = {}) {
        const fetchOptions = {
            type: options.type,
            format: options.format,
            content: false
        };
        return this.get(localPath, fetchOptions);
    }
}
/**
 * Yjs sharedModel factory for real-time collaboration.
 */
class SharedModelFactory {
    /**
     * Shared model factory constructor
     *
     * @param _onCreate Callback on new document model creation
     */
    constructor(_onCreate) {
        this._onCreate = _onCreate;
        this.documentFactories = new Map();
    }
    /**
     * Register a SharedDocumentFactory.
     *
     * @param type Document type
     * @param factory Document factory
     */
    registerDocumentFactory(type, factory) {
        if (this.documentFactories.has(type)) {
            throw new Error(`The content type ${type} already exists`);
        }
        this.documentFactories.set(type, factory);
    }
    /**
     * Create a new `ISharedDocument` instance.
     *
     * It should return `undefined` if the factory is not able to create a `ISharedDocument`.
     */
    createNew(options) {
        if (typeof options.format !== 'string') {
            console.warn(`Only defined format are supported; got ${options.format}.`);
            return;
        }
        if (this.documentFactories.has(options.contentType)) {
            const sharedModel = this._onCreate(options);
            return sharedModel;
        }
        return;
    }
}
