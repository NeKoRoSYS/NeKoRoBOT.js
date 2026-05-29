export enum BackendAction {
    HANDSHAKE = 'handshake',
    CREATE = 'create_user',
    READ = 'read_user',
    UPDATE = 'update_user',
    DELETE = 'delete_user'
}

export enum BackendEvent {
    CREATED = 'created',
    READ = 'read',
    UPDATED = 'updated',
    DELETED = 'deleted'
}

export interface BaseRequest {
    interaction_id: string;
    discord_id: string;
    action: BackendAction;
}

export interface HandshakeRequest extends BaseRequest {
    action: BackendAction.HANDSHAKE;
    token: string;
}

export interface CreateRequest extends BaseRequest {
    action: BackendAction.CREATE;
    username: string;
    bio?: string;
}

export interface ReadRequest extends BaseRequest {
    action: BackendAction.READ;
}

export interface UpdateRequest extends BaseRequest {
    action: BackendAction.UPDATE;
    bio: string;
}

export interface DeleteRequest extends BaseRequest {
    action: BackendAction.DELETE;
}

export type BackendRequest = HandshakeRequest | CreateRequest | ReadRequest | UpdateRequest | DeleteRequest;

export interface ErrorResponse {
    error: true;
    message: string;
    interaction_id?: string;
}

export interface BackendSuccessResponse {
    error?: false;
    interaction_id: string;
    event: BackendEvent;
    message?: string;
}

export interface CrudResponse extends BackendSuccessResponse {
    data?: {
        discord_id: string;
        username: string;
        bio: string;
    };
}

export type BackendResponse = ErrorResponse | CrudResponse;

export class BackendError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'BackendError';
    }
}