class ComplianceFramework:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule, description):
        """
        Adds a compliance rule.
        :param rule: Callable that takes `data` as input and returns a violation message or None.
        :param description: A brief description of the rule.
        """
        self.rules.append({"rule": rule, "description": description})

    def check(self, data):
        """
        Checks the data against all rules.
        :param data: The dataset to check.
        :return: List of violations.
        """
        violations = []
        for rule in self.rules:
            result = rule["rule"](data)
            if result:
                violations.append(result)
        return violations
