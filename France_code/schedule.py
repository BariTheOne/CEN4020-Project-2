class Schedule:
    def __init__(self):
        self.sections = []

    def add_section(self, new_section):
        if self.has_conflict(new_section):
            return False
        self.sections.append(new_section)
        return True

    def has_conflict(self, new_section):
        for existing_section in self.sections:
            if existing_section.conflicts_with(new_section):
                return True
        return False

    def remove_section(self, crn):
        for section in self.sections:
            if section.crn == crn:
                self.sections.remove(section)
                return True
        return False

    def get_all_sections(self):
        return self.sections
