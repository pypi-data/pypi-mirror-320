import { User } from '@jupyterlab/services';
import { TranslationBundle } from '@jupyterlab/translation';
import { IDisposable } from '@lumino/disposable';
import { DocumentChange, YDocument } from '@jupyter/ydoc';
/**
 * An interface for a document provider.
 */
export interface IDocumentProvider extends IDisposable {
    /**
     * Returns a Promise that resolves when the document provider is ready.
     */
    readonly ready: Promise<void>;
}
/**
 * A class to provide Yjs synchronization over WebRTC.
 */
export declare class WebrtcProvider implements IDocumentProvider {
    /**
     * Construct a new WebrtcProvider
     *
     * @param options The instantiation options for a WebrtcProvider
     */
    constructor(options: WebrtcProvider.IOptions);
    /**
     * Test whether the object has been disposed.
     */
    get isDisposed(): boolean;
    /**
     * A promise that resolves when the document provider is ready.
     */
    get ready(): Promise<void>;
    /**
     * Dispose of the resources held by the object.
     */
    dispose(): void;
    private _connect;
    private _onUserChanged;
    private _onSync;
    private _awareness;
    private _contentType;
    private _format;
    private _isDisposed;
    private _path;
    private _ready;
    private _sharedModel;
    private _yWebrtcProvider;
    private _signalingServers;
}
/**
 * A namespace for WebSocketProvider statics.
 */
export declare namespace WebrtcProvider {
    /**
     * The instantiation options for a WebSocketProvider.
     */
    interface IOptions {
        /**
         * The server URL
         */
        url: string;
        /**
         * The document file path
         */
        path: string;
        /**
         * Content type
         */
        contentType: string;
        /**
         * The source format
         */
        format: string;
        /**
         * The shared model
         */
        model: YDocument<DocumentChange>;
        /**
         * The user data
         */
        user: User.IManager;
        /**
         * The jupyterlab translator
         */
        translator: TranslationBundle;
        /**
         * The list of WebRTC signaling servers
         */
        signalingServers: string[];
    }
}
