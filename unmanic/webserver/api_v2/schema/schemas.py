#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.schemas.py

    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     01 Aug 2021, (11:45 AM)

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved

           Permission is hereby granted, free of charge, to any person obtaining a copy
           of this software and associated documentation files (the "Software"), to deal
           in the Software without restriction, including without limitation the rights
           to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
           copies of the Software, and to permit persons to whom the Software is
           furnished to do so, subject to the following conditions:

           The above copyright notice and this permission notice shall be included in all
           copies or substantial portions of the Software.

           THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
           EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
           MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
           IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
           DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
           OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
           OR OTHER DEALINGS IN THE SOFTWARE.

"""
from marshmallow import Schema, fields, validate


class BaseSchema(Schema):
    class Meta:
        ordered = True


# RESPONSES
# =========

class BaseSuccessSchema(BaseSchema):
    success = fields.Boolean(
        required=True,
        description='This is always "True" when a request succeeds',
        example=True,
    )


class BaseErrorSchema(BaseSchema):
    error = fields.Str(
        required=True,
        description="Return status code and reason",
    )
    messages = fields.Dict(
        required=True,
        description="Attached request body validation errors",
        example={"name": ["The thing that went wrong."]},
    )
    traceback = fields.List(
        cls_or_instance=fields.Str,
        required=False,
        description="Attached exception traceback (if developer mode is enabled)",
        example=[
            "Traceback (most recent call last):\n",
            "...",
            "json.decoder.JSONDecodeError: Expecting value: line 3 column 14 (char 45)\n"
        ],
    )


class BadRequestSchema(BaseErrorSchema):
    """STATUS_ERROR_EXTERNAL = 400"""
    error = fields.Str(
        required=True,
        description="Return status code and reason",
        example="400: Failed request schema validation",
    )


class BadEndpointSchema(BaseSchema):
    """STATUS_ERROR_ENDPOINT_NOT_FOUND = 404"""
    error = fields.Str(
        required=True,
        description="Return status code and reason",
        example="404: Endpoint not found",
    )


class BadMethodSchema(BaseSchema):
    """STATUS_ERROR_METHOD_NOT_ALLOWED = 405"""
    error = fields.Str(
        required=True,
        description="Return status code and reason",
        example="405: Method 'GET' not allowed",
    )


class InternalErrorSchema(BaseErrorSchema):
    """STATUS_ERROR_INTERNAL = 500"""
    error = fields.Str(
        required=True,
        description="Return status code and reason",
        example="500: Caught exception message",
    )


# GENERIC
# =======

class RequestTableDataSchema(BaseSchema):
    """Table request schema"""

    start = fields.Int(
        required=False,
        description="Start row number to select from",
        example=0,
        load_default=0,
    )
    length = fields.Int(
        required=False,
        description="Number of rows to select",
        example=10,
        load_default=10,
    )
    search_value = fields.Str(
        required=False,
        description="String to filter search results by",
        example="items with this text in the value",
        load_default="",
    )
    order_by = fields.Str(
        required=False,
        description="Column to order results by",
        example="finish_time",
        load_default="",
    )
    order_direction = fields.Str(
        required=False,
        description="Order direction ('asc' or 'desc')",
        example="desc",
        validate=validate.OneOf(["asc", "desc"]),
    )


class RequestTableUpdateByIdList(BaseSchema):
    """Schema for updating tables by ID"""

    id_list = fields.List(
        cls_or_instance=fields.Int,
        required=True,
        description="Start row number to select from",
        example=0,
        validate=validate.Length(min=1),
    )


class TableRecordsSuccessSchema(BaseSchema):
    """Schema for table results"""

    recordsTotal = fields.Int(
        required=False,
        description="Total number of records in this table",
        example=329,
    )
    recordsFiltered = fields.Int(
        required=False,
        description="Total number of records after filters have been applied",
        example=10,
        load_default=10,
    )
    results = fields.List(
        cls_or_instance=fields.Raw,
        required=False,
        description="Results",
        example=[],
    )


# DOCS
# ====

class DocumentContentSuccessSchema(BaseSchema):
    """Schema for updating tables by ID"""

    content = fields.List(
        cls_or_instance=fields.Str,
        required=True,
        description="Document contents read line-by-line into a list",
        example=[
            "First line\n",
            "Second line\n",
            "\n",
        ],
        validate=validate.Length(min=1),
    )


# HISTORY
# =======

class RequestHistoryTableDataSchema(RequestTableDataSchema):
    """Schema for requesting completed tasks from the table"""

    order_by = fields.Str(
        example="finish_time",
        load_default="finish_time",
    )


class CompletedTasksResultsSchema(BaseSchema):
    """Schema for completed tasks results returned by the table"""

    id = fields.Int(
        required=True,
        description="Item ID",
        example=1,
    )
    task_label = fields.Str(
        required=True,
        description="Item label",
        example="example.mp4",
    )
    task_success = fields.Boolean(
        required=True,
        description="Item success status",
        example=True,
    )
    finish_time = fields.Int(
        required=True,
        description="Item finish time",
        example=1627392616.6400812,
    )


class CompletedTasksSchema(TableRecordsSuccessSchema):
    """Schema for updating completed task table by ID"""

    successCount = fields.Int(
        required=True,
        description="Total count of times with a success status in the results list",
        example=337,
    )
    failedCount = fields.Int(
        required=True,
        description="Total count of times with a failed status in the results list",
        example=2,
    )
    results = fields.Nested(
        CompletedTasksResultsSchema,
        required=True,
        description="Results",
        many=True,
        validate=validate.Length(min=1),
    )


# PENDING
# =======

class RequestPendingTableDataSchema(RequestTableDataSchema):
    """Schema for requesting pending tasks from the table"""

    order_by = fields.Str(
        example="priority",
        load_default="priority",
    )


class PendingTasksResultsSchema(BaseSchema):
    """Schema for pending task results returned by the table"""

    id = fields.Int(
        required=True,
        description="Item ID",
        example=1,
    )
    task_label = fields.Str(
        required=True,
        description="Item label",
        example="example.mp4",
    )
    task_success = fields.Boolean(
        required=True,
        description="Item success status",
        example=True,
    )
    finish_time = fields.Int(
        required=True,
        description="Item finish time",
        example=1627392616.6400812,
    )


class PendingTasksSchema(TableRecordsSuccessSchema):
    """Schema for updating pending task table by ID"""

    results = fields.Nested(
        CompletedTasksResultsSchema,
        required=True,
        description="Results",
        many=True,
        validate=validate.Length(min=0),
    )


class RequestPendingTasksReorderSchema(RequestTableUpdateByIdList):
    """Schema for moving pending items to top or bottom of table by ID"""

    position = fields.Str(
        required=True,
        description="Position to move given list of items to ('top' or 'bottom')",
        example="top",
        validate=validate.OneOf(["top", "bottom"]),
    )


# SESSION
# =======

class SessionStateSuccessSchema(BaseSchema):
    """Schema for returning session data"""

    level = fields.Int(
        required=True,
        description="User level",
        example=0,
    )
    picture_uri = fields.Str(
        required=False,
        description="User picture",
        example="https://c8.patreon.com/2/200/561356054",
    )
    name = fields.Str(
        required=False,
        description="User name",
        example="ExampleUsername123",
    )
    email = fields.Str(
        required=False,
        description="User email",
        example="example@gmail.com",
    )
    created = fields.Number(
        required=False,
        description="Session time created",
        example=1627793093.676484,
    )
    uuid = fields.Str(
        required=True,
        description="Installation uuid",
        example="b429fcc7-9ce1-bcb3-2b8a-b094747f226e",
    )


# VERSION
# =======

class VersionReadSuccessSchema(BaseSchema):
    """Schema for returning the application version"""

    version = fields.Str(
        required=True,
        description="Application version",
        example="1.0.0",
    )
