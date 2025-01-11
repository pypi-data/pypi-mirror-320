from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.forbidden_restricted_sample_error import ForbiddenRestrictedSampleError
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    container_id: str,
    containable_id: str,
) -> Dict[str, Any]:
    url = "{}/containers/{container_id}/contents/{containable_id}".format(
        client.base_url, container_id=container_id, containable_id=containable_id
    )

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[None, ForbiddenRestrictedSampleError, NotFoundError]]:
    if response.status_code == 204:
        response_204 = None

        return response_204
    if response.status_code == 403:
        response_403 = ForbiddenRestrictedSampleError.from_dict(response.json(), strict=False)

        return response_403
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json(), strict=False)

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[None, ForbiddenRestrictedSampleError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    container_id: str,
    containable_id: str,
) -> Response[Union[None, ForbiddenRestrictedSampleError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        container_id=container_id,
        containable_id=containable_id,
    )

    response = client.httpx_client.delete(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    container_id: str,
    containable_id: str,
) -> Optional[Union[None, ForbiddenRestrictedSampleError, NotFoundError]]:
    """ Delete a container content """

    return sync_detailed(
        client=client,
        container_id=container_id,
        containable_id=containable_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    container_id: str,
    containable_id: str,
) -> Response[Union[None, ForbiddenRestrictedSampleError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        container_id=container_id,
        containable_id=containable_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.delete(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    container_id: str,
    containable_id: str,
) -> Optional[Union[None, ForbiddenRestrictedSampleError, NotFoundError]]:
    """ Delete a container content """

    return (
        await asyncio_detailed(
            client=client,
            container_id=container_id,
            containable_id=containable_id,
        )
    ).parsed
