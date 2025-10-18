from datatig.exceptions import SiteConfigurationException
from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldEnumConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "enum"

    def _load_extra_config(self, config: dict) -> None:
        in_choices = config.get("choices", [])
        choices = []
        for choice in in_choices:
            if isinstance(choice, str) or isinstance(choice, int):
                choices.append({"value": choice, "title": choice})
            elif isinstance(choice, dict):
                if "value" not in choice:
                    raise SiteConfigurationException("No key in choice")
                if "title" not in choice:
                    choice["title"] = str(choice["value"])
                choices.append(choice)
            else:
                raise SiteConfigurationException("Choices format not known")
        if len(choices) == 0:
            raise SiteConfigurationException("No choices specified")
        self._extra_config["choices"] = choices
        if len(self._get_all_choice_values()) != len(
            set(self._get_all_choice_values())
        ):
            raise SiteConfigurationException("Choice values are not unique")

    def _get_all_choice_values(self) -> list:
        out = []
        for choice in self._extra_config["choices"]:
            out.append(choice["value"])
        return out

    def get_json_schema(self) -> dict:
        out = {
            "enum": self._get_all_choice_values(),
            "title": self._title,
            "description": self._description,
            "options": {
                "enum_titles": [c["title"] for c in self._extra_config["choices"]]
            },
        }
        return out

    def get_new_item_json(self):
        return None

    def get_value_object(self, record, data):
        v = FieldEnumValueModel(field=self, record=record)
        obj = JSONDeepReaderWriter(data)
        v.set_value(obj.read(self._key))
        return v

    def get_frictionless_csv_field_specifications(self):
        return [
            {
                "name": "field_" + self.get_id(),
                "title": self.get_title(),
                "type": "string",
            },
            {
                "name": "field_" + self.get_id() + "___title",
                "title": self.get_title(),
                "type": "string",
            },
        ]

    def get_choices(self) -> list:
        return self._extra_config["choices"]


class FieldEnumValueModel(FieldValueModel):
    def set_value(self, value):
        self._value = str(value) if value is not None else None

    def has_value(self) -> bool:
        return isinstance(self._value, str)

    def get_value(self):
        return self._value

    def get_value_title(self):
        for choice in self._field.get_choices():
            if choice["value"] == self._value:
                return choice["title"]
        return self._value

    def get_frictionless_csv_data_values(self):
        return [self._value, self.get_value_title()]

    def different_to(self, other_field_value):
        return self._value != other_field_value._value

    def get_api_value(self) -> dict:
        return {"value": self._value}

    def get_urls_in_value(self) -> list:
        return []
