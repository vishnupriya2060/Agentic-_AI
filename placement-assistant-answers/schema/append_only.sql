-- Lab 2: history cannot be rewritten, whichever program connects.

CREATE TRIGGER IF NOT EXISTS message_no_update
BEFORE UPDATE ON message
BEGIN
    SELECT RAISE(ABORT, 'message is append-only: UPDATE rejected');
END;

CREATE TRIGGER IF NOT EXISTS message_no_delete
BEFORE DELETE ON message
BEGIN
    SELECT RAISE(ABORT, 'message is append-only: DELETE rejected');
END;
