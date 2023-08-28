from pyrogram.types import ChatPermissions

# TODO: перенести сюда все длинное дерьмо


class Permissions:
    basic = ChatPermissions(can_send_messages=True, can_send_other_messages=True,
                            can_send_media_messages=True, can_add_web_page_previews=True, can_pin_messages=False,
                            can_send_polls=False, can_invite_users=False, can_change_info=False)

    muted = ChatPermissions(can_send_messages=False, can_send_other_messages=False,
                            can_send_media_messages=False, can_add_web_page_previews=True, can_pin_messages=False,
                            can_send_polls=False, can_invite_users=False, can_change_info=False)

    nolinks = ChatPermissions(can_send_messages=True, can_send_other_messages=False,
                              can_send_media_messages=False, can_add_web_page_previews=True, can_pin_messages=False,
                              can_send_polls=False, can_invite_users=False, can_change_info=False)
