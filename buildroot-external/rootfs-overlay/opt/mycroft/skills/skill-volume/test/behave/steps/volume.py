from time import sleep
from behave import given, then

from mycroft.messagebus import Message
from mycroft.audio import wait_while_speaking

from test.integrationtests.voight_kampff import emit_utterance


@given("Mycroft audio is muted")
def given_muted(context):
    context.bus.emit(Message('mycroft.volume.mute',
                             data={'speak_message': False}))
    sleep(0.5)


@given("the volume is set to 5")
def given_volume_is_five(context):
    emit_utterance(context.bus, 'Set volume to 5')
    context.volume = 0.5
    sleep(1)
    wait_while_speaking()
    context.bus.clear_messages()


@given("the volume is set to 10")
def given_volume_is_ten(context):
    emit_utterance(context.bus, 'Set volume to 10')
    context.volume = 1.0
    sleep(1)
    wait_while_speaking()
    context.bus.clear_messages()


@then('"mycroft-volume" should decrease the volume')
def then_decrease(context):
    cnt = 0
    msgs = context.bus.get_messages('mycroft.volume.set')

    while msgs == []:
        if cnt > 20:
            assert False, "Message not found"
            break
        else:
            cnt += 1
        sleep(0.5)
        msgs = context.bus.get_messages('mycroft.volume.set')
    if msgs:
        err_info = "Volume hasn't decreased!"
        print(msgs[0].data['percent'])
        assert msgs[0].data['percent'] < context.volume, err_info


@then('"mycroft-volume" should increase the volume')
def then_increase(context):
    cnt = 0
    msgs = context.bus.get_messages('mycroft.volume.set')

    while msgs == []:
        if cnt > 20:
            assert False, "Message not found"
            break
        else:
            cnt += 1
        sleep(0.5)
        msgs = context.bus.get_messages('mycroft.volume.set')
    if msgs:
        err_info = "Volume hasn't increased!"
        print(msgs[0].data['percent'])
        assert msgs[0].data['percent'] > context.volume, err_info
