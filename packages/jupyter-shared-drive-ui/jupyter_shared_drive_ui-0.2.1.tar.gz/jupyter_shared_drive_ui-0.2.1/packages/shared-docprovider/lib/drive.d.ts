import { JupyterFrontEnd } from '@jupyterlab/application';
import { ISignal } from '@lumino/signaling';
import { TranslationBundle } from '@jupyterlab/translation';
import { Contents } from '@jupyterlab/services';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { ServerConnection } from '@jupyterlab/services';
import { ICollaborativeDrive, ISharedModelFactory } from '@jupyter/collaborative-drive';
import { Awareness } from 'y-protocols/awareness';
/**
 * A collaborative implementation for an `IDrive`, talking to other peers using WebRTC.
 */
export declare class SharedDrive implements ICollaborativeDrive {
    /**
     * Construct a new drive object.
     *
     * @param user - The user manager to add the identity to the awareness of documents.
     */
    constructor(app: JupyterFrontEnd, defaultFileBrowser: IDefaultFileBrowser, translator: TranslationBundle, globalAwareness: Awareness | null, name: string);
    get providers(): Map<string, any>;
    private _onSync;
    getDownloadUrl(path: string): Promise<string>;
    delete(localPath: string): Promise<void>;
    restoreCheckpoint(path: string, checkpointID: string): Promise<void>;
    deleteCheckpoint(path: string, checkpointID: string): Promise<void>;
    exportFile(toPath: string): Promise<void>;
    importFile(fromPath: string, toPath: string): Promise<void>;
    newUntitled(options?: Contents.ICreateOptions): Promise<Contents.IModel>;
    rename(path: string, newPath: string): Promise<Contents.IModel>;
    copy(path: string, toDir: string): Promise<Contents.IModel>;
    createCheckpoint(path: string): Promise<Contents.ICheckpointModel>;
    listCheckpoints(path: string): Promise<Contents.ICheckpointModel[]>;
    /**
     * The server settings of the drive.
     */
    serverSettings: ServerConnection.ISettings;
    /**
     * The name of the drive, which is used at the leading
     * component of file paths.
     */
    readonly name: string;
    /**
     * A signal emitted when a file operation takes place.
     */
    get fileChanged(): ISignal<this, Contents.IChangedArgs>;
    /**
     * Test whether the manager has been disposed.
     */
    get isDisposed(): boolean;
    /**
     * SharedModel factory for the SharedDrive.
     */
    readonly sharedModelFactory: ISharedModelFactory;
    /**
     * Dispose of the resources held by the manager.
     */
    dispose(): void;
    /**
     * Get a file or directory.
     *
     * @param localPath: The path to the file.
     *
     * @param options: The options used to fetch the file.
     *
     * @returns A promise which resolves with the file content.
     */
    get(localPath: string, options?: Contents.IFetchOptions): Promise<Contents.IModel>;
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
    save(localPath: string, options?: Partial<Contents.IModel>): Promise<Contents.IModel>;
    private _onCreate;
    private _user;
    private _defaultFileBrowser;
    private _trans;
    private _fileProviders;
    private _globalAwareness;
    private _fileChanged;
    private _isDisposed;
    private _ydrive;
    private _fileSystemProvider;
    private _ready;
    private _signalingServers;
    private _app;
}
