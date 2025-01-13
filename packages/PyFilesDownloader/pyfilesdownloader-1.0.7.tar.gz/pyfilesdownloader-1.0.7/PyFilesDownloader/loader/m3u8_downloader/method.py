import m3u8
import requests
from loguru import logger


def redirected_resolution_url(
        url: str,
        headers: dict = None,
        verify_ssl: bool = False,
        timeout: int = 10, *,
        idx: int = -1
):
    """
    从m3u8文件获取重定向的解析URL.
    :param url: m3u8文件 URL.
    :param headers: 请求头.
    :param verify_ssl: 是否验证SSL证书.
    :param timeout: 超时时间.
    :param idx: m3u8文件中解析URL的索引.
    :return: 重定向的解析URL.
    """
    logger.info(f"获取m3u8文件{url} 的重定向解析 URL")
    headers = headers or {}
    m3u8_obj: m3u8.M3U8 = m3u8.load(url, headers=headers, verify_ssl=verify_ssl, timeout=timeout)
    try:
        logger.info(f"获取m3u8文件{url} 的重定向解析 URL, 索引为{idx}")
        absolute_uri = m3u8_obj.playlists[idx].absolute_uri
        logger.info(f"获取m3u8文件{url} 的重定向解析 URL, 索引为{idx}, 解析 URL 为{absolute_uri}")
        return absolute_uri
    except IndexError:
        logger.error(f"获取m3u8文件{url} 的重定向解析 URL, 索引为 {idx} 超出范围")
        return None


def m3u8_to_absolute_uris(
        url: str,
        headers: dict = None,
        verify_ssl: bool = False,
        timeout: int = 10
):
    """
    从m3u8文件获取重定向的解析URL列表.
    :param url: m3u8文件 URL.
    :param headers: 请求头.
    :param verify_ssl: 是否验证SSL证书.
    :param timeout: 超时时间.
    :return: 重定向的解析URL列表.
    """
    headers = headers or {}
    logger.info(f"获取m3u8文件{url} 的重定向解析 URL列表")
    m3u8_obj = m3u8.load(url, headers=headers, verify_ssl=verify_ssl, timeout=timeout)
    absolute_uris = []
    kt: m3u8.Key = m3u8_obj.segments[0].key
    logger.info(f"解析URL列表, key为{kt}")
    key = {
        'key': '',
        'method': '',
        'uri': '',
        'iv': '',
        'keyformat': '',
        'keyformatversions': ''
    }
    if kt:
        response = requests.get(kt.absolute_uri, headers=headers, verify=verify_ssl)
        response.raise_for_status()
        iv = kt.iv
        if iv:
            iv = iv[2:18]
        key = {
            'key': response.content,
            'method': kt.method,
            'uri': kt.absolute_uri,
            'iv': iv,
            'keyformat': kt.keyformat,
            'keyformatversions': kt.keyformatversions
        }
        logger.info(f"解析 m3u8 秘钥,key为 {key}")
    logger.info('获取ts文件列表')
    for segment in m3u8_obj.segments:
        segment: m3u8.Segment
        absolute_uris.append(segment.absolute_uri)
    logger.info('获取ts文件列表完成')
    return absolute_uris, key
