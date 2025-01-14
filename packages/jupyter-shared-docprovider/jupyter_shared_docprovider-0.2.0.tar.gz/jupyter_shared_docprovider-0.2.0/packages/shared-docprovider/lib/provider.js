/* -----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/
import { PromiseDelegate } from '@lumino/coreutils';
import { Signal } from '@lumino/signaling';
import { WebrtcProvider as YWebrtcProvider } from 'y-webrtc';
/**
 * A class to provide Yjs synchronization over WebRTC.
 */
export class WebrtcProvider {
    /**
     * Construct a new WebrtcProvider
     *
     * @param options The instantiation options for a WebrtcProvider
     */
    constructor(options) {
        this._onSync = (synced) => {
            if (synced.synced) {
                this._ready.resolve();
                //this._yWebrtcProvider?.off('status', this._onSync);
            }
        };
        this._ready = new PromiseDelegate();
        this._isDisposed = false;
        this._path = options.path;
        this._contentType = options.contentType;
        this._format = options.format;
        this._sharedModel = options.model;
        this._awareness = options.model.awareness;
        this._yWebrtcProvider = null;
        this._signalingServers = options.signalingServers;
        const user = options.user;
        user.ready
            .then(() => {
            this._onUserChanged(user);
        })
            .catch(e => console.error(e));
        user.userChanged.connect(this._onUserChanged, this);
        this._connect().catch(e => console.warn(e));
    }
    /**
     * Test whether the object has been disposed.
     */
    get isDisposed() {
        return this._isDisposed;
    }
    /**
     * A promise that resolves when the document provider is ready.
     */
    get ready() {
        return this._ready.promise;
    }
    /**
     * Dispose of the resources held by the object.
     */
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this._isDisposed = true;
        //this._yWebrtcProvider?.off('status', this._onSync);
        this._yWebrtcProvider?.destroy();
        Signal.clearData(this);
    }
    async _connect() {
        this._yWebrtcProvider = new YWebrtcProvider(`${this._format}:${this._contentType}:${this._path}}`, this._sharedModel.ydoc, {
            signaling: this._signalingServers,
            awareness: this._awareness
        });
        this._yWebrtcProvider.on('synced', this._onSync);
    }
    _onUserChanged(user) {
        this._awareness.setLocalStateField('user', user.identity);
    }
}
