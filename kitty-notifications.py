import datetime
import weechat


SCRIPT_NAME = "notification_center"
SCRIPT_AUTHOR = "Emma Eilefsen Glenna <emma@eilefsen.net>"
SCRIPT_VERSION = "1.0.0"
SCRIPT_LICENSE = "MIT"
SCRIPT_DESC = "Pass highlights and private messages as OS notifcations via the Kitty terminal (OSC 99)"

weechat.register(
    SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""
)

WEECHAT_VERSION = weechat.info_get("version_number", "") or 0
DEFAULT_OPTIONS = {
    "show_highlights": "on",
    "show_private_message": "on",
    "show_message_text": "on",
    "ignore_old_messages": "off",
    "ignore_current_buffer_messages": "off",
    "channels": "",
    "tags": "",
}

for key, val in DEFAULT_OPTIONS.items():
    if not weechat.config_is_set_plugin(key):
        weechat.config_set_plugin(key, val)

weechat.hook_print(
    "", "irc_privmsg," + weechat.config_get_plugin("tags"), "", 1, "notify", ""
)


def notify(
    data: str,
    buffer: str,
    date: str,
    tags: str,
    displayed: int,
    highlight: int,
    prefix: str,
    message: str,
) -> int:
    # Ignore if it's yourself
    own_nick = weechat.buffer_get_string(buffer, "localvar_nick")
    if prefix == own_nick or prefix == ("@%s" % own_nick):
        return weechat.WEECHAT_RC_OK

    # Ignore messages from the current buffer
    if (
        weechat.config_get_plugin("ignore_current_buffer_messages") == "on"
        and buffer == weechat.current_buffer()
    ):
        return weechat.WEECHAT_RC_OK

    # Ignore messages older than the configured theshold (such as ZNC logs) if enabled
    if weechat.config_get_plugin("ignore_old_messages") == "on":
        message_time = datetime.datetime.fromtimestamp(int(date))
        now_time = datetime.datetime.now()

        # Ignore if the message is greater than 5 seconds old
        if (now_time - message_time).seconds > 5:
            return weechat.WEECHAT_RC_OK

    channel_allow_list = []
    if weechat.config_get_plugin("channels") != "":
        channel_allow_list = weechat.config_get_plugin("channels").split(",")
    channel = weechat.buffer_get_string(buffer, "localvar_channel")

    if channel in channel_allow_list:
        if weechat.config_get_plugin("show_message_text") == "on":
            Notifier.notify(
                message,
                title="%s %s" % (prefix, channel),
            )
        else:
            Notifier.notify(
                "In %s by %s" % (channel, prefix),
                title="Channel Activity",
            )
    elif weechat.config_get_plugin("show_highlights") == "on" and int(highlight):
        if weechat.config_get_plugin("show_message_text") == "on":
            Notifier.notify(
                message,
                title="%s %s" % (prefix, channel),
            )
        else:
            Notifier.notify(
                "In %s by %s" % (channel, prefix),
                title="Highlighted Message",
            )
    elif (
        weechat.config_get_plugin("show_private_message") == "on"
        and "irc_privmsg" in tags
        and "notify_private" in tags
    ):
        if weechat.config_get_plugin("show_message_text") == "on":
            Notifier.notify(
                message,
                title="%s [private]" % prefix,
            )
        else:
            Notifier.notify(
                "From %s" % prefix,
                title="Private Message",
            )
    return weechat.WEECHAT_RC_OK
