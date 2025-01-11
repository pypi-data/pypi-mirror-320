#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : kolors
# @Time         : 2025/1/6 16:39
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import asyncio

from meutils.pipe import *
from meutils.io.files_utils import to_url_fal
from meutils.schemas.image_types import KolorsRequest

from openai import OpenAI, AsyncOpenAI


async def generate(request: KolorsRequest):
    client = AsyncOpenAI(
        base_url="https://ai.gitee.com/v1",
        api_key="WPCSA3ZYD8KBQQ2ZKTAPVUA059J2Q47TLWGB2ZMQ",
        default_headers={"X-Failover-Enabled": "true", "X-Package": "1910"},
    )

    response = await client.images.generate(
        model="Kolors",
        prompt=request.prompt,

        size=request.size,
        extra_body={
            "num_inference_steps": 25,
            "guidance_scale": 7.5,
        },
    )
    if request.response_format == "url":
        async def to_response_url(response_data):
            url = await to_url_fal(response_data.b64_json, content_type="image/png")
            response_data.url = url
            response_data.b64_json = None

        await asyncio.gather(*[to_response_url(data) for data in response.data])  # 多张图片

    return response


if __name__ == '__main__':
    request = KolorsRequest(prompt="一个小女孩举着横幅，上面写着“新年快乐”", size="1024x1024", response_format="url")
    arun(generate(request))
