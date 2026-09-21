import pytest
from aioshad.types import User, Chat, Message


def test_user_from_dict():
    data = {
        "user_guid": "u0123456789abcdef",
        "first_name": "Amin",
        "last_name": "Madani",
        "username": "aminmadani",
        "phone": "989123456789",
        "bio": "Developer",
    }
    user = User.from_dict(data)
    assert user.guid == "u0123456789abcdef"
    assert user.first_name == "Amin"
    assert user.last_name == "Madani"
    assert user.full_name == "Amin Madani"
    assert user.username == "aminmadani"


def test_chat_from_dict_group():
    data = {
        "group": {
            "group_guid": "g0abcdef123456",
            "group_title": "Python Developers",
            "count_members": 42,
            "description": "Welcome!",
        }
    }
    chat = Chat.from_dict(data)
    assert chat.guid == "g0abcdef123456"
    assert chat.title == "Python Developers"
    assert chat.type == "Group"
    assert chat.is_group is True
    assert chat.is_channel is False
    assert chat.is_private is False
    assert chat.members_count == 42


def test_chat_from_dict_channel():
    data = {
        "channel": {
            "channel_guid": "c0abcdef123456",
            "channel_title": "Tech News",
            "count_members": 1000,
        }
    }
    chat = Chat.from_dict(data)
    assert chat.guid == "c0abcdef123456"
    assert chat.is_channel is True
    assert chat.is_group is False


def test_message_from_dict():
    data = {
        "message_id": "1001",
        "text": "Hello world!",
        "author_object_guid": "u0author",
        "object_guid": "g0group",
        "type": "Text",
    }
    msg = Message.from_dict(data)
    assert msg.id == "1001"
    assert msg.text == "Hello world!"
    assert msg.author_guid == "u0author"
    assert msg.chat_guid == "g0group"
    assert msg.sender_id == "u0author"
    assert msg.chat_id == "g0group"
