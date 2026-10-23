#!/usr/bin/env python3
"""生成「转发验证码」快捷指令（未签名的 .shortcut 文件）。

用法：
    python3 shortcut/make_shortcut.py [-o 输出路径]

逻辑与 PDF 指南第 5 页手动搭建的完全一致：
    匹配文本 (?<!\\d)\\d{4,8}(?!\\d) → 取第一项 → 如果有值 → 发送信息「验证码：… 原文：…」

收件人不写死，导入时 iPhone 会弹出「导入问题」让你填 B 的 Apple 账户。

注意：iOS 15 起只能导入签过名的快捷指令，签名只能在 Mac 上做：
    shortcuts sign --mode anyone --input 转发验证码.unsigned.shortcut --output 转发验证码.shortcut
"""
import argparse
import plistlib
import uuid
from pathlib import Path

PATTERN = r"(?<!\d)\d{4,8}(?!\d)"
OBJ = "￼"  # 文本里变量占位符


def new_uuid():
    return str(uuid.uuid4()).upper()


def output_ref(action_uuid, name):
    return {"Type": "ActionOutput", "OutputUUID": action_uuid, "OutputName": name}


def attachment(value):
    return {"Value": value, "WFSerializationType": "WFTextTokenAttachment"}


def token_string(parts):
    """parts: 字符串或变量 dict 的列表，拼成带变量的文本参数。"""
    text, attachments = "", {}
    for part in parts:
        if isinstance(part, str):
            text += part
        else:
            attachments[f"{{{len(text)}, 1}}"] = part
            text += OBJ
    return {
        "Value": {"string": text, "attachmentsByRange": attachments},
        "WFSerializationType": "WFTextTokenString",
    }


def action(identifier, **params):
    return {"WFWorkflowActionIdentifier": identifier, "WFWorkflowActionParameters": params}


def build():
    shortcut_input = {"Type": "ExtensionInput"}
    text_id, match_id, item_id, if_group = new_uuid(), new_uuid(), new_uuid(), new_uuid()

    actions = [
        # 把输入（收到的信息）转成文本
        action("is.workflow.actions.gettext", UUID=text_id,
               WFTextActionText=token_string([shortcut_input])),
        action("is.workflow.actions.text.match", UUID=match_id,
               WFMatchTextPattern=PATTERN, WFMatchTextCaseSensitive=False,
               text=attachment(output_ref(text_id, "文本"))),
        action("is.workflow.actions.getitemfromlist", UUID=item_id,
               WFItemSpecifier="First Item",
               WFInput=attachment(output_ref(match_id, "匹配项"))),
        # WFCondition 100 = 有任何值
        action("is.workflow.actions.conditional", GroupingIdentifier=if_group,
               WFControlFlowMode=0, WFCondition=100,
               WFInput={"Type": "Variable",
                        "Variable": attachment(output_ref(item_id, "列表中的项目"))}),
        action("is.workflow.actions.sendmessage", UUID=new_uuid(), ShowWhenRun=False,
               WFSendMessageContent=token_string([
                   "验证码：", output_ref(item_id, "列表中的项目"),
                   "\n原文：", output_ref(text_id, "文本"),
               ])),
        action("is.workflow.actions.conditional", GroupingIdentifier=if_group,
               WFControlFlowMode=2),
    ]
    send_index = next(i for i, a in enumerate(actions)
                      if a["WFWorkflowActionIdentifier"].endswith("sendmessage"))

    return {
        "WFWorkflowName": "转发验证码",
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "2607.0.2",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowHasShortcutInputVariables": True,
        "WFWorkflowInputContentItemClasses": ["WFStringContentItem", "WFRichTextContentItem"],
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowTypes": [],
        "WFWorkflowIcon": {"WFWorkflowIconStartColor": 4292093695,  # 绿色
                           "WFWorkflowIconGlyphNumber": 59511},
        "WFWorkflowImportQuestions": [{
            "ActionIndex": send_index,
            "Category": "Parameter",
            "ParameterKey": "WFSendMessageActionRecipients",
            "Text": "验证码发给谁？填手机 B 的 iMessage 账户（新 Apple 账户邮箱）",
            "DefaultValue": "",
        }],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    default_out = Path(__file__).with_name("转发验证码.unsigned.shortcut")
    parser.add_argument("-o", "--output", type=Path, default=default_out)
    args = parser.parse_args()
    with open(args.output, "wb") as f:
        plistlib.dump(build(), f, fmt=plistlib.FMT_BINARY)
    print(f"已生成 {args.output}")


if __name__ == "__main__":
    main()
