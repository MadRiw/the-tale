# coding: utf-8

from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE
from game.quests.quests_generator import commands as cmd

class EVENTS:
    INTRO = 'intro'
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    START_QUEST = 'start_quest'
    GIVE_POWER = 'give_power'

class HelpFriend(Quest):

    ACTORS = [(u'соратник', 'person_end', ACTOR_TYPE.PERSON)]

    @classmethod
    def can_be_used(cls, env):
        return env.knowlege_base.get_special('hero_pref_friend') is not None


    def initialize(self, identifier, env, place_start=None):
        super(HelpFriend, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())

        friend_uuid = env.knowlege_base.get_special('hero_pref_friend')['uuid']

        self.env_local.register('person_end', env.new_person(person_uuid=friend_uuid))
        self.env_local.register('place_end', env.new_place(person_uuid=friend_uuid))

        self.env_local.register('quest_help', env.new_quest(from_list=['delivery', 'caravan', 'spying', 'not_my_work'],
                                                            place_start=self.env_local.place_end,
                                                            person_start=self.env_local.person_end) )

    def create_line(self, env):

        sequence = [ cmd.Message(event=EVENTS.INTRO) ]

        if self.env_local.place_start != self.env_local.place_end:
            sequence += [ cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST) ]

        sequence += [ cmd.Quest(quest=self.env_local.quest_help, event=EVENTS.START_QUEST),
                      cmd.GivePower(person=self.env_local.person_end,
                                    depends_on=self.env_local.person_end, multiply=0.25,
                                    event=EVENTS.GIVE_POWER)]

        main_line =  Line(sequence=sequence)

        self.line = env.new_line(main_line)

        env.quests[self.env_local.quest_help].create_line(env)
