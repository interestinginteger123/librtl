from contextlib import contextmanager

from unittest.mock import patch, MagicMock

from librtl.azdo import AzureDevOpsInteractor

def mock_pull_request(title="RouteToLive: feature/Utopia to develop", source="feature/Utopia", destination="develop", description=AzureDevOpsInteractor.pr_description(), is_draft=True):
    return MagicMock(title=title, source_ref_name=source, target_ref_name=destination, description=description, is_draft=is_draft)

@contextmanager
def mocked_azdo_backend(client, method, return_value):
    response = MagicMock()
    response.status_code.return_value = 200
    pdb.set_trace()
    send_mock = MagicMock()
    send_mock.return_value = response
    deser_mock = MagicMock()
    deser_mock.return_value = None
    with patch.multiple(client, _base_deserialize=deser_mock, _send=send_mock, _client=MagicMock() ):
        with patch.object(client, method, return_value) as mocked_thing:
            yield mocked_thing
