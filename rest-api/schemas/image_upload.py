from marshmallow import Schema, fields


class ImageUploadSchema(Schema):
    name = fields.String()
    data = fields.Raw()
    file_type = fields.String()
