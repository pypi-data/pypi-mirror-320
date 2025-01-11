import base64
import json
import pickle
import time
from datetime import datetime
from io import StringIO
from typing import Tuple, TypeVar, Type, Optional

import pandas as pd
import requests
from pydantic import BaseModel
from chronulus_core.types.response import QueuePredictionResponse

from .prediction import Prediction
from .session import Session

BaseModelSubclass = TypeVar('BaseModelSubclass', bound=BaseModel)


class Estimator:

    def __init__(self, session: Session, input_type: Type[BaseModelSubclass]):
        self.estimator_id = None
        self.session = session
        self.estimator_name = "EstimatorBase"
        self.input_type = input_type


class EstimatorCreationRequest(BaseModel):
    estimator_name: str
    session_id: str
    input_item_schema_b64: str


class NormalizedForecaster(Estimator):

    def __init__(self, session: Session, input_type: Type[BaseModelSubclass]):
        super().__init__(session, input_type)
        self.estimator_name = "NormalizedForecaster"
        self.create()

    def create(self):

        fields = pickle.dumps(self.input_type.model_fields)
        fields_b64 = base64.b64encode(fields).decode()

        request_data = EstimatorCreationRequest(
            estimator_name=self.estimator_name,
            session_id=self.session.session_id,
            input_item_schema_b64=fields_b64,
        )

        resp = requests.post(
            url=f"{self.session.env.API_URI}/estimators/create",
            headers=self.session.headers,
            json=request_data.model_dump()
        )

        response_json = resp.json()

        if 'estimator_id' in response_json:
            self.estimator_id = response_json['estimator_id']
            print(f"Estimator created with estimator_id: {response_json['estimator_id']}")
        else:
            raise ValueError("There was an error creating the estimator. Please try again.")

    def queue(
            self,
            item: BaseModelSubclass,
            start_dt: datetime,
            weeks: int = None,
            days: int = None,
            hours: int = None,
            note_length: Tuple[int, int] = (3, 5),
    ):

        if not isinstance(item, self.input_type):
            raise TypeError(f"Expect item to be an instance of {self.input_type}, but item has type {type(item)}")

        data = dict(
            estimator_id=self.estimator_id,
            item_data=item.model_dump(),
            start_dt=start_dt.timestamp(),
            weeks=weeks,
            days=days,
            hours=hours,
            note_length=note_length,
        )
        resp = requests.post(
            url=f"{self.session.env.API_URI}/estimators/queue-predict",
            headers=self.session.headers,
            json=data,
        )

        if resp.status_code == 200:
            return QueuePredictionResponse(**resp.json())
        else:
            return QueuePredictionResponse(
                success=False,
                request_id='',
                message=f'Queuing failed with status code {resp.status_code}: {resp.text}',
            )

    def get_predictions(self, request_id: str, try_every: int = 3, max_tries: int = 20):

        retries = 0

        while retries < max_tries:

            resp = requests.post(
                url=f"{self.session.env.API_URI}/predictions/check-by-request-id",
                headers=self.session.headers,
                json=dict(request_id=request_id),
            )

            if resp.status_code != 200:
                print(resp)
                raise Exception(f"An error occurred")

            else:
                response_json = resp.json()

                if response_json['status'] == 'ERROR':
                    return response_json

                if response_json['status'] == 'SUCCESS':
                    print(f'{response_json["status"]}. {response_json["message"]}. Fetching predictions.')
                    prediction_ids = response_json.get('prediction_ids', [])
                    return [self.get_prediction(prediction_id) for prediction_id in prediction_ids]

                if response_json['status'] in ['PENDING', 'NOT_FOUND']:
                    print(f'{response_json["status"]}. {response_json["message"]}. Trying again in {try_every} seconds...')
                    time.sleep(try_every)

                retries += 1

        if retries >= max_tries:
            raise Exception(f"Retry limit exceeded max_tries of {max_tries}")

    def get_prediction(self, prediction_id: str) -> Optional[Prediction]:

        resp = requests.post(
            url=f"{self.session.env.API_URI}/predictions/get-by-prediction-id",
            headers=self.session.headers,
            json=dict(prediction_id=prediction_id),
        )

        response_json = resp.json()

        if resp.status_code == 200 and response_json['success']:
            estimator_response = response_json['response']
            json_str = json.dumps(estimator_response['json_split_format_dict'])

            prediction = Prediction(
                _id=prediction_id,
                text=estimator_response['notes'],
                df=pd.read_json(StringIO(json_str), orient='split'),
            )

            return prediction

        else:
            return None

    def predict(
                self,
                item: BaseModelSubclass,
                start_dt: datetime = None,
                weeks: int = None,
                days: int = None,
                hours: int = None,
                note_length: Tuple[int, int] = (3, 5),
       ) -> Prediction:
        req = self.queue(item, start_dt, weeks, days, hours, note_length)
        predictions = self.get_predictions(req['request_id'])
        return predictions[0] if predictions else None



