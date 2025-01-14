import * as Y from 'yjs';
/**
 * A class for accessing the file system.
 * It consists of a shared document that has a root `Y.Map` under 'root'.
 * The root map's keys are the top-level file and directory names.
 * For keys corresponding to files, the value is an ID (string).
 * For keys corresponding to directories, the value is another `Y.Map` with the same structure
 * as the root map, describing the content of the directory, and so on.
 */
export declare class YDrive {
    constructor();
    get ydoc(): Y.Doc;
    private _newDir;
    exists(path: string): boolean;
    isDir(path: string): boolean;
    getId(path: string): string;
    listDir(path: string): Map<string, any>;
    get(path: string): Y.Map<any> | string;
    newUntitled(isDir: boolean, path?: string, ext?: string): string;
    createFile(path: string): void;
    createDirectory(path: string): void;
    delete(path: string): void;
    move(fromPath: string, toPath: string): void;
    private _ydoc;
    private _yroot;
}
