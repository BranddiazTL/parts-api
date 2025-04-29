import pytest
import httpx
import random
from typing import Any, Dict, Union
from faker import Faker
from starlette import status
import uuid

from app.models.part import PartVisibility

pytestmark = pytest.mark.asyncio

API_PREFIX = "/parts"
fake = Faker()


@pytest.fixture
async def created_part(client_user: httpx.AsyncClient) -> dict[str, Any]:
    part_data = {
        "name": f"Part_{fake.word()}",
        "sku": f"SKU-API-{random.randint(10000, 99999)}",
        "description": "Initial Description",
        "weight_ounces": 10,
        "visibility": PartVisibility.PRIVATE.value,
    }
    response = await client_user.post(f"{API_PREFIX}", json=part_data)
    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


@pytest.mark.parametrize(
    "payload, expected_status_code",
    [
        # Valid data
        (
            {
                "name": f"Valid Part {fake.word()}",
                "sku": f"SKU-VALID-{random.randint(10000, 99999)}",
                "description": fake.sentence(),
                "weight_ounces": random.randint(1, 100),
                "visibility": "PUBLIC",
            },
            status.HTTP_201_CREATED,
        ),
        # Missing required name
        (
            {
                "sku": f"SKU-MISS-NAME-{random.randint(10000, 99999)}",
                "description": fake.sentence(),
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        # Missing required sku
        (
            {"name": f"Missing SKU {fake.word()}", "description": fake.sentence()},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        # Invalid visibility value
        (
            {
                "name": f"Invalid Vis {fake.word()}",
                "sku": f"SKU-INV-VIS-{random.randint(10000, 99999)}",
                "visibility": "SOMEWHERE",
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        # Non-dict payload
        ("not a dictionary", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_create_part_api(
    client_user: httpx.AsyncClient,
    payload: Union[Dict[str, Any], str],
    expected_status_code: int,
):
    response = await client_user.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_201_CREATED:
        data = response.json()
        if isinstance(payload, dict):
            assert data["name"] == payload["name"]
            assert data["sku"] == payload["sku"]
        assert "id" in data
        assert "owner_id" in data


async def test_create_part_duplicate_sku(
    client_user: httpx.AsyncClient, created_part: dict[str, Any]
):
    duplicate_payload = {
        "name": f"Duplicate SKU Part {fake.word()}",
        "sku": created_part["sku"],
        "description": "Trying to reuse SKU",
    }
    response = await client_user.post(f"{API_PREFIX}", json=duplicate_payload)
    assert response.status_code == status.HTTP_409_CONFLICT


async def test_get_part_api(
    client_user: httpx.AsyncClient, created_part: dict[str, Any]
):
    part_id = created_part["id"]
    response = await client_user.get(f"{API_PREFIX}/{part_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == part_id
    assert data["name"] == created_part["name"]
    assert data["sku"] == created_part["sku"]
    assert "owner_id" in data


async def test_get_nonexistent_part_api(client_user: httpx.AsyncClient):
    non_existent_id = uuid.uuid4()
    response = await client_user.get(f"{API_PREFIX}/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "update_payload, expected_status_code",
    [
        (
            {
                "name": "Updated Name via API",
                "description": "Updated description.",
                "visibility": PartVisibility.PUBLIC.value,
            },
            status.HTTP_200_OK,
        ),
        ({"visibility": "INVALID_VISIBILITY"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"weight_ounces": "not-an-int"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_update_part_api(
    client_user: httpx.AsyncClient,
    created_part: dict[str, Any],
    update_payload: dict[str, Any],
    expected_status_code: int,
):
    part_id = created_part["id"]
    response = await client_user.patch(f"{API_PREFIX}/{part_id}", json=update_payload)

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        data = response.json()
        assert data["id"] == part_id
        assert data["name"] == update_payload.get("name", created_part["name"])
        assert data["description"] == update_payload.get(
            "description", created_part["description"]
        )
        assert data["visibility"] == update_payload.get(
            "visibility", created_part["visibility"]
        )
        assert data["sku"] == created_part["sku"]


async def test_update_nonexistent_part_api(client_user: httpx.AsyncClient):
    non_existent_id = uuid.uuid4()
    update_payload = {"name": "Trying to update non-existent"}
    response = await client_user.patch(
        f"{API_PREFIX}/{non_existent_id}", json=update_payload
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_part_api(
    client_user: httpx.AsyncClient, created_part: dict[str, Any]
):
    part_id = created_part["id"]

    # Delete the part
    delete_response = await client_user.delete(f"{API_PREFIX}/{part_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's long gone
    get_response = await client_user.get(f"{API_PREFIX}/{part_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_nonexistent_part_api(client_user: httpx.AsyncClient):
    non_existent_id = uuid.uuid4()
    response = await client_user.delete(f"{API_PREFIX}/{non_existent_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
