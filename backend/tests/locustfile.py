from locust import HttpUser, task, between


class DemoUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        r = self.client.post(
            "/api/token", data={"username": "viewer", "password": "View123!"}
        )
        if r.ok:
            self.client.headers.update(
                {"Authorization": "Bearer " + r.json()["access_token"]}
            )

    @task
    def dashboard_and_search(self):
        self.client.get("/api/dashboard")
        self.client.get("/api/products?q=widget")
