import logic.ws_handler

ROUTES = { # Every string of route has a corresponding function found in root/core/logic/db_handler.py
    'handshake': logic.ws_handler.handle_handshake,
    'create_user': logic.ws_handler.handle_create,
    'read_user': logic.ws_handler.handle_read,
    'update_user': logic.ws_handler.handle_update,
    'delete_user': logic.ws_handler.handle_delete
}