import unittest

from app import app, model_bundle


def valid_listing():
    city = model_bundle["cities"][0]
    return {
        "city": city,
        "neighbourhood": model_bundle["neighbourhoods_by_city"][city][0],
        "property_type": model_bundle["property_types"][0],
        "room_type": model_bundle["room_types"][0],
        "bed_type": model_bundle["bed_types"][0],
        "cancellation_policy": model_bundle["cancellation_policies"][0],
        "accommodates": 2,
        "bathrooms": 1,
        "bedrooms": 1,
        "beds": 1,
        "cleaning_fee": False,
        "instant_bookable": False,
        "amenities": ["has_wifi", "has_kitchen"],
    }


class PriceEstimatorApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_options_are_loaded_from_model_bundle(self):
        response = self.client.get("/api/options")

        self.assertEqual(response.status_code, 200)
        options = response.get_json()
        self.assertEqual(options["cities"], model_bundle["cities"])
        self.assertEqual(
            options["neighbourhoods_by_city"],
            model_bundle["neighbourhoods_by_city"],
        )
        self.assertEqual(options["model_name"], model_bundle["model_name"])

    def test_prediction_returns_positive_nightly_price(self):
        response = self.client.post("/api/predict", json=valid_listing())

        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertGreater(result["predicted_price"], 0)
        self.assertEqual(result["currency"], "USD")
        self.assertEqual(result["period"], "night")

    def test_invalid_neighbourhood_is_rejected(self):
        listing = valid_listing()
        listing["neighbourhood"] = "Not in this city"

        response = self.client.post("/api/predict", json=listing)

        self.assertEqual(response.status_code, 400)
        self.assertIn("neighbourhood", response.get_json()["error"])

    def test_out_of_range_capacity_is_rejected(self):
        listing = valid_listing()
        listing["accommodates"] = 17

        response = self.client.post("/api/predict", json=listing)

        self.assertEqual(response.status_code, 400)
        self.assertIn("between 1 and 16", response.get_json()["error"])

    def test_non_json_request_is_rejected(self):
        response = self.client.post("/api/predict", data="{}")

        self.assertEqual(response.status_code, 415)
        self.assertIn("JSON", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
