export declare class Path {
    constructor(path: string);
    get parts(): Array<string>;
    get parent(): string;
    get name(): string;
    private _parts;
}
