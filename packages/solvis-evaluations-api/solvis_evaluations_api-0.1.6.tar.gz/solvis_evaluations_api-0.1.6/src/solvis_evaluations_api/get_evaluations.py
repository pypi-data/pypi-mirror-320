import io
import logging
import time
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import requests


class GetEvaluations:
    """
    A class to interact with the surveys API and fetch evaluations data.
    """

    def __init__(self, survey_base_url: str = 'https://www.solvis.net.br/results_api/v1/surveys') -> None:
        """
        Initialize the GetEvaluations class with default attributes.
        """
        self.user: Optional[str] = None
        self.password: Optional[str] = None
        self.session: Optional[requests.Session] = None
        self.survey_base_url = survey_base_url

    def __fetch_with_retries(self, url: str, retries: int = 10) -> Optional[str]:
        for attempt in range(retries):
            try:
                resp = self.session.get(url, auth=(self.user, self.password), timeout=30)
                if resp.status_code == 200:
                    return resp.text
                logging.warning(f'Non-200 response ({resp.status_code}) for {self.date_str}. Attempt: {attempt + 1}')
                if resp.status_code >= 500:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logging.error(f'Attempt {attempt + 1} failed for {self.date_str}: {e}')
            if attempt == retries - 1:
                raise Exception(f'Max retries reached for {self.date_str}. Aborting operation.')
        return None

    def get_evaluations(
        self,
        user: str,
        password: str,
        survey_id: str,
        start_date: str,
        end_date: str,
        verbose: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch survey evaluations from the API within a specified date range.

        Args:
            user (str): API username.
            password (str): API password.
            survey_id (int): Survey ID to fetch evaluations for.
            start_date (str): Start date in 'DD/MM/YYYY' format.
            end_date (str): End date in 'DD/MM/YYYY' format.
            verbose (bool): If True, logs INFO level messages; otherwise, logs ERROR level messages.

        Returns:
            pd.DataFrame: A DataFrame containing evaluations.

        Raises:
            ValueError: If date range is invalid.
            Exception: For API-related errors.
        """
        self.user = user
        self.password = password
        self.session = requests.Session()

        logging.basicConfig(
            level=logging.INFO if verbose else logging.ERROR,
            format='%(levelname)s - %(message)s',
        )

        start_datetime = datetime.strptime(start_date, '%d/%m/%Y')
        end_datetime = datetime.strptime(end_date, '%d/%m/%Y')
        if start_datetime > end_datetime:
            raise ValueError('Start date must be before or equal to the end date.')

        api_base_url = f'{self.survey_base_url}/{survey_id}/responses'
        logging.info(f'Selected period: {start_date} to {end_date}')

        rows = []
        for i in range((end_datetime - start_datetime).days + 1):
            self.date_str = (start_datetime + timedelta(days=i)).strftime('%Y-%m-%d')
            url = f'{api_base_url}?date={self.date_str}'
            response = self.__fetch_with_retries(url)

            if response and response.strip():
                response_buffer = io.StringIO(response)
                temp_df = pd.read_csv(response_buffer, index_col=False)
                rows.extend(temp_df.to_dict(orient='records'))
                logging.info(f'{self.date_str} fetched successfully')
            else:
                logging.warning(f'No data for {self.date_str}. Skipping.')

        if rows:
            logging.info('Data fetching complete!')
            return pd.DataFrame(rows)
        else:
            logging.info('No evaluations for the selected date range.')
            return pd.DataFrame()
