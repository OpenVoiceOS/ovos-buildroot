from ovos_workshop.skills.ovos import OVOSSkill


class ActiveSkill(OVOSSkill):
    def bind(self, bus):
        super(ActiveSkill, self).bind(bus)
        if bus:
            """ insert skill in active skill list on load """
            self.make_active()

    def handle_skill_deactivated(self, message=None):
        """ skill is always in active skill list,
        ie, converse is always called """
        self.make_active()


