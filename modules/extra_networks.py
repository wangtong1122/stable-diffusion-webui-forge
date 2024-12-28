import json
import os
import re
import logging
from collections import defaultdict

from modules import errors

extra_network_registry = {}
extra_network_aliases = {}


def initialize():
    extra_network_registry.clear()
    extra_network_aliases.clear()


def register_extra_network(extra_network):
    extra_network_registry[extra_network.name] = extra_network


def register_extra_network_alias(extra_network, alias):
    extra_network_aliases[alias] = extra_network


def register_default_extra_networks():
    from modules.extra_networks_hypernet import ExtraNetworkHypernet
    register_extra_network(ExtraNetworkHypernet())


class ExtraNetworkParams:
    def __init__(self, items=None):
        self.items = items or []
        self.positional = []
        self.named = {}

        for item in self.items:
            parts = item.split('=', 2) if isinstance(item, str) else [item]
            if len(parts) == 2:
                self.named[parts[0]] = parts[1]
            else:
                self.positional.append(item)

    def __eq__(self, other):
        return self.items == other.items

#ExtraNetwork类是一个抽象类，包含activate和deactivate两个方法
#ExtraNetworkLora和ExtraNetworkHypernet类继承自ExtraNetwork类
class ExtraNetwork:
    def __init__(self, name):
        self.name = name

    def activate(self, p, params_list):
        """
        Called by processing on every run. Whatever the extra network is meant to do should be activated here.
        Passes arguments related to this extra network in params_list.
        User passes arguments by specifying this in his prompt:

        <name:arg1:arg2:arg3>

        Where name matches the name of this ExtraNetwork object, and arg1:arg2:arg3 are any natural number of text arguments
        separated by colon.

        Even if the user does not mention this ExtraNetwork in his prompt, the call will still be made, with empty params_list -
        in this case, all effects of this extra networks should be disabled.

        Can be called multiple times before deactivate() - each new call should override the previous call completely.

        For example, if this ExtraNetwork's name is 'hypernet' and user's prompt is:

        > "1girl, <hypernet:agm:1.1> <extrasupernet:master:12:13:14> <hypernet:ray>"

        params_list will be:

        [
            ExtraNetworkParams(items=["agm", "1.1"]),
            ExtraNetworkParams(items=["ray"])
        ]

        """
        raise NotImplementedError

    def deactivate(self, p):
        """
        Called at the end of processing for housekeeping. No need to do anything here.
        """

        raise NotImplementedError


#`lookup_extra_networks` 方法的输入是一个字典 `extra_network_data`，其键是 `extra_network` 的名称，值是 `ExtraNetworkParams` 对象的列表。输出是一个字典，其键是 `ExtraNetwork` 对象，值是 `ExtraNetworkParams` 对象的列表。

# 输入示例：
# ```python
# {
#     'lora': [<ExtraNetworkParams object>],
#     'hypernet': [<ExtraNetworkParams object>]
# }
# ```
#
# 输出示例：
# ```python
# {
#     <ExtraNetworkLora object>: [<ExtraNetworkParams object>],
#     <ExtraNetworkHypernet object>: [<ExtraNetworkParams object>]
# }
# ```
def lookup_extra_networks(extra_network_data):
    """returns a dict mapping ExtraNetwork objects to lists of arguments for those extra networks.

    Example input:
    {
        'lora': [<modules.extra_networks.ExtraNetworkParams object at 0x0000020690D58310>],
        'lyco': [<modules.extra_networks.ExtraNetworkParams object at 0x0000020690D58F70>],
        'hypernet': [<modules.extra_networks.ExtraNetworkParams object at 0x0000020690D5A800>]
    }

    Example output:

    {
        <extra_networks_lora.ExtraNetworkLora object at 0x0000020581BEECE0>: [<modules.extra_networks.ExtraNetworkParams object at 0x0000020690D58310>, <modules.extra_networks.ExtraNetworkParams object at 0x0000020690D58F70>],
        <modules.extra_networks_hypernet.ExtraNetworkHypernet object at 0x0000020581BEEE60>: [<modules.extra_networks.ExtraNetworkParams object at 0x0000020690D5A800>]
    }
    """

    res = {}

    for extra_network_name, extra_network_args in list(extra_network_data.items()):
        extra_network = extra_network_registry.get(extra_network_name, None)
        alias = extra_network_aliases.get(extra_network_name, None)

        if alias is not None and extra_network is None:
            extra_network = alias

        if extra_network is None:
            logging.info(f"Skipping unknown extra network: {extra_network_name}")
            continue

        #这行代码的作用是将 `extra_network_args` 列表中的元素添加到字典 `res` 中对应的 `extra_network` 键的值列表中。如果 `res` 字典中还没有 `extra_network` 键，则使用 `setdefault` 方法创建一个新的空列表作为该键的值，然后再将 `extra_network_args` 列表中的元素添加到这个新列表中。
        # 具体来说：
        # - `res.setdefault(extra_network, [])`：如果 `res` 字典中存在 `extra_network` 键，则返回其对应的值（一个列表）；如果不存在，则创建一个新的空列表作为该键的值，并返回这个新列表。
        # - `.extend(extra_network_args)`：将 `extra_network_args` 列表中的所有元素添加到 `res` 字典中 `extra_network` 键对应的列表中。
        res.setdefault(extra_network, []).extend(extra_network_args)

    return res


def activate(p, extra_network_data):
    """call activate for extra networks in extra_network_data in specified order, then call
    activate for all remaining registered networks with an empty argument list"""

    activated = []

    for extra_network, extra_network_args in lookup_extra_networks(extra_network_data).items():

        try:
            extra_network.activate(p, extra_network_args)#调用ExtraNetwork的activate方法
            activated.append(extra_network)
        except Exception as e:
            errors.display(e, f"activating extra network {extra_network.name} with arguments {extra_network_args}")

    for extra_network_name, extra_network in extra_network_registry.items():
        if extra_network in activated:
            continue

        try:
            extra_network.activate(p, [])
        except Exception as e:
            errors.display(e, f"activating extra network {extra_network_name}")

    if p.scripts is not None:
        p.scripts.after_extra_networks_activate(p, batch_number=p.iteration, prompts=p.prompts, seeds=p.seeds, subseeds=p.subseeds, extra_network_data=extra_network_data)


def deactivate(p, extra_network_data):
    """call deactivate for extra networks in extra_network_data in specified order, then call
    deactivate for all remaining registered networks"""

    data = lookup_extra_networks(extra_network_data)

    for extra_network in data:
        try:
            extra_network.deactivate(p)
        except Exception as e:
            errors.display(e, f"deactivating extra network {extra_network.name}")

    for extra_network_name, extra_network in extra_network_registry.items():
        if extra_network in data:
            continue

        try:
            extra_network.deactivate(p)
        except Exception as e:
            errors.display(e, f"deactivating unmentioned extra network {extra_network_name}")


re_extra_net = re.compile(r"<(\w+):([^>]+)>")


def parse_prompt(prompt):
    res = defaultdict(list)

    def found(m):
        name = m.group(1)
        args = m.group(2)

        res[name].append(ExtraNetworkParams(items=args.split(":")))

        return ""
    #根据正则表达式re_extra_net，将prompt中的extra network提取出来，然后将其替换为空
    #返回的res是一个字典，key是extra network的名字，value是一个ExtraNetworkParams对象的列表
    prompt = re.sub(re_extra_net, found, prompt)
    #prompt是一个字符串，res是一个字典 res表示lora的配置信息
    return prompt, res


def parse_prompts(prompts):
    res = []
    extra_data = None

    for prompt in prompts:
        updated_prompt, parsed_extra_data = parse_prompt(prompt)

        if extra_data is None:
            extra_data = parsed_extra_data

        res.append(updated_prompt)

    return res, extra_data


def get_user_metadata(filename, lister=None):
    if filename is None:
        return {}

    basename, ext = os.path.splitext(filename)
    metadata_filename = basename + '.json'

    metadata = {}
    try:
        exists = lister.exists(metadata_filename) if lister else os.path.exists(metadata_filename)
        if exists:
            with open(metadata_filename, "r", encoding="utf8") as file:
                metadata = json.load(file)
    except Exception as e:
        errors.display(e, f"reading extra network user metadata from {metadata_filename}")

    return metadata
