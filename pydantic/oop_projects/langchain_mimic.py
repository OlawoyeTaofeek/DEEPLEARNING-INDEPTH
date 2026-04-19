import re
from schema import PromptTemplateSchema


def extract_variables(template: str):
    return re.findall(r"{(.*?)}", template)


class PromptTemplate:
    """
    Core PromptTemplate engine (LangChain-inspired)
    """

    def __init__(
        self,
        template: str,
        *,
        input_variables=None,
        input_types=None,
        partial_variables=None,
    ):
        # Auto-infer if not provided
        inferred_vars = extract_variables(template)

        self.schema = PromptTemplateSchema(
            template=template,
            input_variables=input_variables or inferred_vars,
            input_types=input_types or {},
            partial_variables=partial_variables or {},
        )

    # ---------------------------
    # FACTORY METHOD (optional)
    # ---------------------------
    @classmethod
    def from_template(cls, template: str):
        return cls(template)

    # ---------------------------
    # CORE PROPERTIES
    # ---------------------------
    @property
    def template(self):
        return self.schema.template

    @property
    def input_variables(self):
        return self.schema.input_variables

    @property
    def partial_variables(self):
        return self.schema.partial_variables

    @property
    def input_types(self):
        return self.schema.input_types

    # ---------------------------
    # FORMATTING LOGIC
    # ---------------------------
    def format(self, **kwargs) -> str:
        final_inputs = {**self.partial_variables, **kwargs}

        missing = set(self.input_variables) - set(final_inputs.keys())
        extra = set(final_inputs.keys()) - set(self.input_variables)

        if missing:
            raise ValueError(f"Missing variables: {missing}")
        if extra:
            raise ValueError(f"Unexpected variables: {extra}")

        return self.template.format(**final_inputs)

    # ---------------------------
    # CLEAN REPRESENTATION
    # ---------------------------
    def __repr__(self):
        return (
            f"PromptTemplate("
            f"input_variables={self.input_variables}, "
            f"template={self.template!r}), "
            f"input_types={self.input_types}, "
            f"partial_variables={self.partial_variables})"
        )

# prompt = PromptTemplate.from_template("Explain {topic} in simple terms. using {language} language.")
# print(prompt)
# print(type(prompt))
# print(prompt.input_variables)
# print(prompt.template)

# msgs = prompt.format(topic="AI", language="English")
# print(msgs)

prompt = PromptTemplate(template="What is the capital of {country}?", input_variables=["country"])
print(prompt)
print(prompt.input_variables)
print(prompt.template)
print(prompt.format(country="France"))
