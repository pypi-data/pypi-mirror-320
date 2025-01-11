#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : common
# @Time         : 2024/12/16 18:19
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://github.com/LLM-Red-Team/jimeng-free-api/commit/acd362a4cecd115938bf4bc9bbb0067738aa0d5b#diff-e6a7354ac1431dc3751e91efaf1799200c1ce2fa8abe975a49c32644290988baR121
from openai import AsyncClient

from meutils.pipe import *
from meutils.hash_utils import md5
from meutils.schemas.image_types import ImageRequest
from meutils.schemas.openai_types import TTSRequest

from meutils.schemas.jimeng_types import BASE_URL, MODELS_MAP
from meutils.str_utils.regular_expression import parse_url
from meutils.apis.jimeng.files import upload
from meutils.io.files_utils import to_bytes
from meutils.caches.redis_cache import cache

from fake_useragent import UserAgent

ua = UserAgent()


def get_headers(url, token="693701c43e477b7c405cc7e2fef0ddbd"):
    device_time = f"{int(time.time())}"
    sign = md5(
        # f"9e2c|receive|7|5.8.0|{device_time}||11ac"
        f"9e2c|{url[-7:]}|7|5.8.0|{device_time}||11ac"
    )

    headers = {
        'appid': '513695',
        'appvr': '5.8.0',
        'device-time': device_time,
        'pf': '7',
        'sign': sign,
        'sign-ver': '1',
        'Cookie': f'sid_guard={token}|{device_time}|5184000|Fri,+14-Feb-2025+00:51:51+GMT',
        'User-Agent': ua.random,

        'content-type': 'application/json',
        # "Referer": "https://jimeng.jianying.com/ai-tool/image/generate",
    }
    return headers


@cache(ttl=3600 // 2)
async def get_upload_token(token):  # 3600 跨账号？
    url = "/artist/v2/tools/get_upload_token"
    headers = get_headers(url, token)

    payload = {"scene": 2}
    client = AsyncClient(base_url=BASE_URL, default_headers=headers)
    response = await client.post(url, body=payload, cast_to=object)
    return response


@alru_cache(12 * 3600)
async def receive_credit(token):
    # token = "eb4d120829cfd3ee957943f63d6152ed"  # y
    # token = "9ba826acc1a4bf0e10912eb01beccfe0"  # w
    url = "/commerce/v1/benefits/credit_receive"
    headers = get_headers(url, token)
    payload = {"time_zone": "Asia/Shanghai"}
    client = AsyncClient(base_url=BASE_URL, default_headers=headers)
    response = await client.post(url, body=payload, cast_to=object)
    logger.debug(bjson(response))


async def get_credit(token):
    # token = "eb4d120829cfd3ee957943f63d6152ed"  # y
    # token = "9ba826acc1a4bf0e10912eb01beccfe0"  # w

    url = "/commerce/v1/benefits/user_credit"
    headers = get_headers(url, token)

    payload = {}
    client = AsyncClient(base_url=BASE_URL, default_headers=headers)
    response = await client.post(url, body=payload, cast_to=object)
    if response['data']['credit']['gift_credit'] == 0:  # 签到
        await receive_credit(token)

    logger.debug(bjson(response))
    return response


async def check_token(token, threshold: int = 1):
    try:
        response = await get_credit(token)
        logger.debug(bjson(response))
        credits = sum(response['data']['credit'].values())
        return credits >= threshold
    except Exception as e:
        return False


async def create_draft_content(request: ImageRequest, token: str):
    """
    创建草稿内容
    """
    request.model = MODELS_MAP.get(request.model, MODELS_MAP["default"])

    height = width = 1360
    if 'x' in request.size:
        height, width = map(int, request.size.split('x'))

    main_component_id = str(uuid.uuid4())

    if urls := parse_url(request.prompt):
        url = urls[-1]
        upload_token = await get_upload_token(token)
        image_uri = upload(await to_bytes(url), upload_token)

        request.prompt = request.prompt.replace(url, '')
        request.model = "high_aes_general_v20_L:general_v2.0_L"  # 2.1不支持图片编辑

        component = {
            "type": "image_base_component",
            "id": main_component_id,
            "min_version": "3.0.2",
            "generate_type": "blend",
            "aigc_mode": "workbench",
            "abilities": {
                "type": "",
                "id": str(uuid.uuid4()),
                "blend": {
                    "type": "",
                    "id": str(uuid.uuid4()),
                    "core_param": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "model": request.model,
                        "prompt": f"##{request.prompt}",
                        "sample_strength": 0.5,
                        "image_ratio": 1,
                        "large_image_info": {
                            "type": "",
                            "id": str(uuid.uuid4()),
                            "height": height,
                            "width": width
                        },
                    },
                    "ability_list": [
                        {
                            "type": "",
                            "id": str(uuid.uuid4()),
                            "name": "byte_edit",
                            "image_uri_list": [
                                image_uri
                            ],
                            "image_list": [
                                {
                                    "type": "image",
                                    "id": str(uuid.uuid4()),
                                    "source_from": "upload",
                                    "platform_type": 1,
                                    "name": "",
                                    "image_uri": image_uri,
                                    "width": 0,
                                    "height": 0,
                                    "format": "",
                                    "uri": image_uri
                                }
                            ],
                            "strength": 0.5
                        }
                    ],
                    "history_option": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                    },
                    "prompt_placeholder_info_list": [
                        {
                            "type": "",
                            "id": str(uuid.uuid4()),
                            "ability_index": 0
                        }
                    ],
                    "postedit_param": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "generate_type": 0
                    }
                }
            }
        }

    else:

        component = {
            "type": "image_base_component",
            "id": main_component_id,
            "min_version": "3.0.2",
            "generate_type": "generate",
            "aigc_mode": "workbench",
            "abilities": {
                "type": "",
                "id": str(uuid.uuid4()),
                "generate": {
                    "type": "",
                    "id": str(uuid.uuid4()),
                    "core_param": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "model": request.model,
                        "prompt": request.prompt,
                        "negative_prompt": request.negative_prompt or "",
                        "seed": request.seed or 426999300,
                        "sample_strength": 0.5,
                        "image_ratio": 1,
                        "large_image_info": {
                            "type": "",
                            "id": str(uuid.uuid4()),
                            "height": height,
                            "width": width
                        }
                    },
                    "history_option": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                    }
                }
            }
        }

    draft_content = {
        "type": "draft",
        "id": str(uuid.uuid4()),
        "min_version": "3.0.2",
        "min_features": [],
        "is_from_tsn": True,
        "version": "3.0.8",
        "main_component_id": main_component_id,
        "component_list": [component]
    }

    logger.debug(bjson(draft_content))

    return draft_content


def create_photo_lip_sync(request: TTSRequest):
    # 映射
    tts_info = {
        "name": request.voice or "魅力姐姐",
        "text": request.input,  # "永远相信美好的事情即将发生"
        "speed": request.seed or 1,
        "source_type": "text-to-speech",
        "tone_category_id": 0,
        "tone_category_key": "all",
        "tone_id": "7382879492752019995",
        "toneKey": request.voice or "魅力姐姐",
    }
    payload = {
        "promptSource": "photo_lip_sync",
        "generateTimes": 1,
        "lipSyncInfo": tts_info,
        "isUseAiGenPrompt": False,
        "batchNumber": 1
    }

    return {
        "submit_id": "",
        "task_extra": json.dumps(payload),
        "http_common_info": {
            "aid": 513695
        },
        "input": {
            "seed": 1834980836,
            "video_gen_inputs": [
                {
                    "v2v_opt": {},
                    "i2v_opt": {
                        "realman_avatar": {
                            "enable": true,
                            "origin_image": {
                                "width": 480,
                                "height": 270,
                                "image_uri": "tos-cn-i-tb4s082cfz/fae8f746367b40f5a708bf0f1e84de11",
                                "image_url": ""  ########## https://oss.ffire.cc/files/kling_watermark.png
                            },
                            "resource_id_loopy": "34464cac-5e3e-46be-88ff-ccbc7da4d742",
                            "resource_id_std": "2f66b408-37c3-4de5-b8a4-ba15c104612e",
                            "origin_audio": {
                                "duration": 3.216,
                                "vid": "v02bc3g10000ctrpqrfog65purfpn7a0"
                            },
                            "tts_info": json.dumps(tts_info)
                        }
                    },
                    "audio_vid": "v02bc3g10000ctrpqrfog65purfpn7a0",
                    "video_mode": 4
                }
            ]
        },
        "mode": "workbench",
        "history_option": {},
        "commerce_info": {
            "resource_id": "generate_video",
            "resource_id_type": "str",
            "resource_sub_type": "aigc",
            "benefit_type": "lip_sync_avatar_std"
        },
        "scene": "lip_sync_image",
        "client_trace_data": {},
        "submit_id_list": [
            "d4554e2c-707f-4ebe-b4e6-93aa6687d1c1"
        ]
    }


if __name__ == '__main__':
    token = "693701c43e477b7c405cc7e2fef0ddbd"
    token = "eb4d120829cfd3ee957943f63d6152ed"
    token = "dcf7bbc31faed9740b0bf748cd4d2c74"
    token = "38d7d300b5e0a803431ef88d8d2acfef"
    token = "916fed81175f5186a2c05375699ea40d"
    # arun(get_credit(token))
    arun(check_token(token))

    # arun(get_upload_token(token))
    #
    # request = ImageRequest(prompt='https://oss.ffire.cc/files/kling_watermark.png笑起来')
    # arun(create_draft_content(request, token))
