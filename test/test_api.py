import pytest

import conexample.interface


class TestEntryRequests:
    class TestGet:
        def test_success(self, api_client):
            response = api_client.get("/v1/entry")
            assert response.status_code == 200
            assert len(response.json) == 2

        def test_error_propagation(self, api_client, core):
            core.get_entries.side_effect = conexample.interface.CoreException
            response = api_client.get("/v1/entry")
            assert response.status_code == 500

    class TestPost:
        def test_success(self, api_client, core):

            name = "python"
            rating = 5

            response = api_client.post(
                "/v1/entry", json={"name": name, "rating": rating}
            )

            assert response.status_code == 201
            assert response.headers["Location"].endswith("/v1/entry/" + name)
            core.set_entry_rating.assert_called_with(name, rating)

        def test_on_entry_already_exists(self, api_client, core):

            core.set_entry_rating.return_value = False

            name = "python"
            rating = 5

            response = api_client.post(
                "/v1/entry", json={"name": name, "rating": rating}
            )

            assert response.status_code == 200
            assert response.headers["Location"].endswith("/v1/entry/" + name)
            core.set_entry_rating.assert_called_with(name, rating)

        @pytest.mark.parametrize(
            "data",
            (
                {},
                {"name": "python"},
                {"rating": 5},
                {"name": 5, "rating": 5},
                {"name": "python", "rating": "5"},
                {"name": "python", "rating": -5},
            ),
        )
        def test_fails_for_bad_request(self, api_client, data):
            response = api_client.post("/v1/entry", json=data)
            assert response.status_code == 400

        def test_fails_for_core_invalid_request(self, api_client, core):
            core.set_entry_rating.side_effect = conexample.interface.CoreInvalidRequest
            response = api_client.post(
                "/v1/entry", json={"name": "python", "rating": 5}
            )
            assert response.status_code == 400

        def test_error_propagation(self, api_client, core):
            core.set_entry_rating.side_effect = conexample.interface.CoreException
            response = api_client.post(
                "/v1/entry", json={"name": "python", "rating": 5}
            )
            assert response.status_code == 500


class TestEntryElementRequests:
    class TestGet:
        def test_success(self, api_client):
            response = api_client.get("/v1/entry/python")
            assert response.status_code == 200
            assert response.json["name"] == "python"
            assert response.json["rating"] == 5

        def test_error_propagation(self, api_client, core):
            core.get_rating.side_effect = conexample.interface.CoreException
            response = api_client.get("/v1/entry/python")
            assert response.status_code == 500

        def test_on_no_entry(self, api_client, core):
            core.get_rating.side_effect = conexample.interface.CoreEntryNotFound
            response = api_client.get("/v1/entry/python")
            assert response.status_code == 404

    class TestPost:
        def test_success(self, api_client, core):

            name = "python"
            rating = 5

            response = api_client.post("/v1/entry/" + name, json={"rating": rating})

            assert response.status_code == 201
            assert response.headers["Location"].endswith("/v1/entry/" + name)
            core.set_entry_rating.assert_called_with(name, rating)

        def test_on_entry_already_exists(self, api_client, core):

            core.set_entry_rating.return_value = False

            name = "python"
            rating = 5

            response = api_client.post("/v1/entry/" + name, json={"rating": rating})

            assert response.status_code == 200
            assert response.headers["Location"].endswith("/v1/entry/" + name)
            core.set_entry_rating.assert_called_with(name, rating)

        @pytest.mark.parametrize(
            "data", ({}, {"rating": "5"}, {"rating": -5},),
        )
        def test_fails_for_bad_request(self, api_client, data):
            response = api_client.post("/v1/entry/python", json=data)
            assert response.status_code == 400

        def test_fails_for_core_invalid_request(self, api_client, core):
            core.set_entry_rating.side_effect = conexample.interface.CoreInvalidRequest
            response = api_client.post("/v1/entry/python", json={"rating": 5})
            assert response.status_code == 400

        def test_error_propagation(self, api_client, core):
            core.set_entry_rating.side_effect = conexample.interface.CoreException
            response = api_client.post("/v1/entry/python", json={"rating": 5})
            assert response.status_code == 500

    class TestDelete:
        def test_on_success(self, api_client):
            response = api_client.delete("/v1/entry/python")
            assert response.status_code == 200

        def test_on_no_entry(self, api_client, core):
            core.delete_entry.side_effect = conexample.interface.CoreEntryNotFound
            response = api_client.delete("/v1/entry/python")
            assert response.status_code == 404

        def test_error_propagation(self, api_client, core):
            core.delete_entry.side_effect = conexample.interface.CoreException
            response = api_client.delete("/v1/entry/python")
            assert response.status_code == 500


def test_connexion_resolver_on_invalid_func_id(core):
    api = conexample.api.rest.RestApi(core)
    with pytest.raises(ImportError):
        api.func_resolv("dummy.get")
