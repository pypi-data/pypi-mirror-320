from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message, MessageEvent, PrivateMessageEvent, GroupMessageEvent
from nonebot.internal.params import ArgPlainText
from nonebot.internal.rule import Rule
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me, command, is_type
from .ResultModule import load_check
from .Config import Config, conf
from .Step import Step
from .Userdata import Userdata, loaduserdata

# ---------------------------Configurations---------------------------
__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-zepplife",
    description="基于调用xwteam平台专属api运行的机器人插件，目前仅支持Zepp、微信、支付宝刷步，后续还会更新其他功能",
    usage="",
    type='application',
    homepage="https://github.com/1296lol/nonebot-plugin-zepplife",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={
        "author": "1296",
        "email": "hh1296@foxmail.com"
    }
)

# user = conf.zepplife_user
# password = conf.zepplife_password
private_chat = conf.private_chat
group_chat = conf.group_chat
group_at = conf.group_at
message_block_group = conf.message_block_group
message_block_private = conf.message_block_private
message_block_config = conf.message_block_config
message_block_users = conf.message_block_users
message_help_user = conf.message_help_user
# message_help_admin = conf.message_help_admin
handle_module = conf.handle_module
superusers = conf.superusers
only_superusers_used = conf.only_superusers_used
zepplife_commands = conf.zepplife_commands
# zepplife_admin_commands = conf.zepplife_admin_commands

# 命令转换函数
def trans_command(cmds: str | list[str]):
    if isinstance(cmds, str):
        cmds = [cmds]
    return command(*cmds)


# 刷步帮助
zepplife_help = to_me() & trans_command(zepplife_commands["help"])

matcher_help = on_message(rule=zepplife_help, priority=50, block=True)


@matcher_help.handle()
async def start(event: MessageEvent):
    message = message_help_user
    # if event.get_user_id() in superusers:
    #     message += message_help_admin
    await matcher_help.finish(Message(message), at_sender=group_at)


# 刷步检查
zepplife_check = to_me() & trans_command(zepplife_commands["check"])

check = on_message(rule=zepplife_check, priority=50, block=True)


@check.handle()
async def checking(event: MessageEvent):
    filename = f"{event.get_user_id()}.json"
    data = await loaduserdata(filename)
    await check.finish(Message(f"检查结果:\n{load_check(data)}"), at_sender=group_at)


# 刷步实现
manual_step = to_me() & trans_command(zepplife_commands["manual_step"])
auto_step = to_me() & trans_command(zepplife_commands["auto_step"])

manual = on_message(rule=manual_step, priority=50, block=True)

auto = on_message(rule=auto_step, priority=50, block=True)


@manual.got("manual_input",
            prompt="请输入账号、密码、步数，格式为：账号,密码,步数。\n\n例如：abc@example.com,password,1000\n\n输入【取消】退出。")
async def handle_choice(event: MessageEvent, manual_input: str = ArgPlainText()):
    user_id = event.get_user_id()

    if user_id not in superusers and only_superusers_used:
        await manual.finish(Message(message_block_users), at_sender=group_at)
        return

    if not private_chat:
        await manual.finish(Message(message_block_private), at_sender=group_at)
        return

    if not group_chat:
        await manual.finish(Message(message_block_group), at_sender=group_at)
        return

    await Step.manual_step(event, manual_input, manual)


@auto.got("steps", prompt="请输入步数，输入【取消】退出。")
async def handle_auto_step(event: MessageEvent, steps: str = ArgPlainText()):
    user_id = event.get_user_id()
    filename = f"{user_id}.json"
    data = await loaduserdata(filename)

    if not data['user'] or not data['password']:
        # raise ValueError(message_block_config)
        await auto.finish(Message(message_block_config), at_sender=group_at)
        return

    if user_id not in superusers and only_superusers_used:
        await auto.finish(Message(message_block_users), at_sender=group_at)
        return

    if not private_chat:
        await auto.finish(Message(message_block_private), at_sender=group_at)
        return

    if not group_chat:
        await auto.finish(Message(message_block_group), at_sender=group_at)
        return

    await Step.auto_step(event, steps, auto)


# 保存用户信息
saveuserdata = to_me() & trans_command(zepplife_commands["save_my_data"])

save = on_message(rule=saveuserdata, priority=50, block=True)


@save.got("userdata", prompt="请输入你的Zepplife账号和密码。\n\n例如：abc@example.com,password\n\n输入【取消】退出。")
async def handle_save_my_data(event: PrivateMessageEvent, userdata: str = ArgPlainText()):
    user_id = event.get_user_id()

    if user_id not in superusers and only_superusers_used:
        await save.finish(Message(message_block_users))
        return

    if not private_chat:
        await save.finish(Message(message_block_private))
        return

    await Userdata.save_my_data(event, userdata, save)


# 删除用户信息
deleteuserdata = to_me() & trans_command(zepplife_commands["delete_my_data"])

delete = on_message(rule=deleteuserdata, priority=50, block=True)


@delete.got("reply", prompt="如需删除你的配置，请输入你的QQ账号以确认操作。\n\n例如：123456\n\n输入【取消】退出。")
async def handle_delete_my_data(event: PrivateMessageEvent, reply: str = ArgPlainText()):
    user_id = event.get_user_id()

    if user_id not in superusers and only_superusers_used:
        await delete.finish(Message(message_block_users))
        return

    if not private_chat:
        await delete.finish(Message(message_block_private))
        return

    await Userdata.delete_my_data(event, reply, delete)


# 查看用户信息
selectuserdata = to_me() & trans_command(zepplife_commands["select_my_data"])

selects = on_message(rule=selectuserdata, priority=50, block=True)


@selects.handle()
async def handle_select_my_data(event: PrivateMessageEvent):
    user_id = event.get_user_id()

    if user_id not in superusers and only_superusers_used:
        await selects.finish(Message(message_block_users))
        return

    if not private_chat:
        await selects.finish(Message(message_block_private))
        return

    await Userdata.select_my_data(event, selects)

# 修改用户信息
modifyuserdata = to_me() & trans_command(zepplife_commands["modify_my_data"])

modify = on_message(rule=modifyuserdata, priority=50, block=True)


@modify.got("reply", prompt="请输入你的账号密码以修改。\n\n例如：abc@example.com,password\n\n输入【取消】退出。")
async def handle_modify_my_data(event: PrivateMessageEvent, reply: str = ArgPlainText()):
    user_id = event.get_user_id()

    if user_id not in superusers and only_superusers_used:
        await modify.finish(Message(message_block_users))
        return

    if not private_chat:
        await modify.finish(Message(message_block_private))
        return

    await Userdata.modify_my_data(event, reply, modify)
