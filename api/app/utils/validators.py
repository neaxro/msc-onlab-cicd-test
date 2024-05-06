def validate_non_empty_array(self, array, field_name):
        if not array or not all(item for item in array):
            raise Exception(f"Field '{field_name}' must be a non-empty array with non-empty elements.")