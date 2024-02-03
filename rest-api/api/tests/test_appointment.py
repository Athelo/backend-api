from __future__ import annotations

from api.constants import V1_API_PREFIX


class TestMainApi:
    def test_get_appointment_detail(
        self,
        app,
        client,
        booked_appointment_in_one_week,
        database,
    ):
        def mock_return():
            return print("NO 5 Sec Delay!!!")

        # monkeypatch.setattr("monkeypatch_examples.calculate_sum.delay", mock_return)

        response = client.get(
            f"{V1_API_PREFIX}/appointment/{booked_appointment_in_one_week.id}/",
        )

        assert response.status_code == 200
