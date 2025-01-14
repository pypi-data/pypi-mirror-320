from dataclasses import fields, asdict
from datetime import datetime


class BaseModel:
    """
    Base class for models with common functionality for field initialization,
    type conversion, and SQL generation.
    """

    def __init__(self, **kwargs):
        """
        Initialize the model with given keyword arguments.
        """
        self._additional_fields = {}
        cls_fields = self._get_class_fields()
        init_values = self._filter_known_fields(cls_fields, kwargs)
        self._set_field_values(cls_fields, init_values)

    def _get_class_fields(self):
        """
        Retrieve the class fields with their aliases.
        """
        return {f.metadata.get('alias', f.name): f for f in fields(self)}

    def _filter_known_fields(self, cls_fields, kwargs):
        """
        Filter the known fields from the provided keyword arguments.
        """
        return {cls_fields[k].name: v for k, v in kwargs.items() if k in cls_fields}

    def _set_field_values(self, cls_fields, init_values):
        """
        Set the field values for the model.
        """
        for f in fields(self):
            value = self._convert_field_type(f.type, init_values.get(f.name, f.default))
            setattr(self, f.name, value)

    def _convert_field_type(self, field_type, value):
        """
        Convert the field type to the appropriate type.
        """
        if value is None:
            return value
        if field_type is datetime and isinstance(value, str):
            return self._parse_datetime(value)
        return self._try_convert(field_type, value)

    def _parse_datetime(self, value):
        """
        Parse a string to a datetime object.
        """
        try:
            return datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return value

    def _try_convert(self, field_type, value):
        """
        Try to convert the value to the specified field type.
        """
        try:
            return field_type(value)
        except (TypeError, ValueError):
            return value

    def _to_sql(self, field_name):
        """
        Check if the field should be included in SQL operations.
        """
        return next(f for f in fields(self) if f.name == field_name).metadata.get('to_sql', True)

    def _format_field_value(self, value):
        """
        Format the field value for SQL.
        """
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S.%f')
        return value

    def _get_primary_key(self):
        """
        Retrieve the primary key field name.
        """
        for f in fields(self):
            if f.metadata.get('primary_key', False):
                return f.name
        raise ValueError("No primary key defined")

    def to_dict(self):
        """
        Convert the model to a dictionary, excluding fields not meant for SQL.
        """
        return {k: v for k, v in asdict(self).items() if self._to_sql(k)}

    def add_to_sql(self, additional_fields):
        """
        Add additional fields to be included in SQL operations.
        """
        self._additional_fields.update(additional_fields)

    def to_sql(self):
        """
        Generate a dictionary with the values ready for SQL operations.
        """
        data = self.to_dict()
        data.update(self._additional_fields)
        return {k: self._format_field_value(v) for k, v in data.items()}

    def to_query(self, schema_db=None):
        """
        Generate an SQL insert/update statement for the model.
        """
        data = self.to_sql()
        columns = ', '.join(data.keys())
        values = ', '.join(f"'{v}'" if isinstance(v, str) else str(v) for v in data.values())
        primary_key = self._get_primary_key()
        updates = ', '.join(
            f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}" for k, v in data.items() if k != primary_key)

        table = f"{schema_db}.{self.__class__.__name__.lower()}" if schema_db else self.__class__.__name__.lower()

        return (f"INSERT INTO {table} ({columns}) VALUES ({values}) "
                f"ON CONFLICT ({primary_key}) DO UPDATE SET {updates};")


def sql_bulk(models, schema_db=None, table_name=None):
    """
    Generate a bulk SQL insert statement for a list of models.

    :param models: List of model instances.
    :param schema_db: Optional schema database name.
    :param table_name: Optional table name.
    :return: Bulk SQL insert statement.
    """
    if not models:
        return ""

    table_name = table_name if table_name else models[0].__class__.__name__.lower()
    full_table_name = f"{schema_db}.{table_name}" if schema_db else table_name
    columns = ', '.join(models[0].to_sql().keys())
    values_tuples = []

    for model in models:
        values = ', '.join(f"'{v}'" if isinstance(v, str) else str(v) for v in model.to_sql().values())
        values_tuples.append(f"({values})")

    values_clause = ', '.join(values_tuples)
    return f"INSERT INTO {full_table_name} ({columns}) VALUES {values_clause};"
