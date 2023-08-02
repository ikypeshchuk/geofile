from marshmallow import Schema, fields


class FileUploadSchema(Schema):
    url = fields.Url(required=True)
