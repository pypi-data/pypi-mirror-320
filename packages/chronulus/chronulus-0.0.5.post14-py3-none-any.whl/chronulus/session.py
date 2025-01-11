from typing import Optional

import requests

from .environment import BaseEnv, Env, get_default_headers


class Session(BaseEnv):

    def __init__(self, name: str, situation: str, task: str, session_id: Optional[str] = None, env: Optional[dict] = None):
        super().__init__(**(env if env and isinstance(env, dict) else {}))

        self.name = name
        self.situation = situation
        self.task = task
        self.session_id = session_id

        if self.session_id is None:
            self.create()

    def create(self):

        resp = requests.post(
            url=f"{self.env.API_URI}/sessions/create",
            headers=self.headers,
            json=dict(
                name=self.name,
                situation=self.situation,
                task=self.task,
                session_id=self.session_id,
            )
        )
        response_json = resp.json()
        if resp.status_code != 200:
            if resp.status_code == 403:
                raise Exception("Failed to create session. API Key is not valid or not yet active. Please allow up to 1 minute for activation of new keys.")
            else:
                raise Exception(f"Failed to create session with status code: {resp.status_code}")
        else:
            self.session_id = response_json['session_id']
            print(f"Session created with session_id: {response_json['session_id']}")

    @staticmethod
    def load_from_saved_session(session_id: str, env: Optional[dict] = None):
        env = Env(**env) if env and isinstance(env, dict) else Env()
        headers = get_default_headers(env)

        resp = requests.post(
            url=f"{env.API_URI}/sessions/from-session-id",
            headers=headers,
            json=dict(session_id=session_id)
        )

        if resp.status_code != 200:
            raise ValueError(f"Failed to create session with status code: {resp.status_code}, {resp.text}")

        try:
            response_json = resp.json()
            return Session(**response_json)

        except Exception as e:
            raise ValueError(f"Failed to parse session response: {resp.text}")



