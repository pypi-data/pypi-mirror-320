# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from unittest import mock
import time
import uuid

from grpc._channel import _InactiveRpcError
from frozendict import frozendict

from ldlm import Client, TLSConfig, exceptions
from ldlm.client import Lock
from ldlm.protos import ldlm_pb2 as pb2


class MockedClient(Client):

    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of the class.

        Initializes the following instance variables:
            - renew_lock_response (None): The response for the renew lock operation.
            - unlock_response (None): The response for the unlock operation.
            - lock_response (None): The response for the lock operation.
            - try_lock_response (None): The response for the try lock operation.

        Calls the parent class's __init__ method.

        Creates a MagicMock object for the stub with the following methods:
            - Unlock: A mock MagicMock that calls the get_unlock_response method.
            - Lock: A mock MagicMock that calls the get_lock_response method.
            - TryLock: A mock MagicMock that calls the get_try_lock_response method.
            - Renew: A mock MagicMock that calls the get_renew_lock_response method.
        """
        self.renew_response = None
        self.unlock_response = None
        self.lock_response = None
        self.try_lock_response = None

        super().__init__(*args, **kwargs)
        self._stub = mock.MagicMock(
            Unlock=mock.MagicMock(side_effect=self.get_unlock_response),
            Lock=mock.MagicMock(side_effect=self.get_lock_response),
            TryLock=mock.MagicMock(side_effect=self.get_try_lock_response),
            Renew=mock.MagicMock(side_effect=self.get_renew_lock_response),
        )

    def get_renew_lock_response(self, req, metadata=None):
        assert isinstance(req, pb2.RenewRequest)
        return pb2.LockResponse(
            locked=True,
            name=req.name,
            key=req.key,
        )

    def get_unlock_response(self, req, metadata=None) -> pb2.UnlockResponse:
        assert isinstance(req, pb2.UnlockRequest)
        return self.unlock_response or pb2.UnlockResponse(
            unlocked=True,
            name=req.name,
        )

    def get_lock_response(self, req, metadata=None) -> pb2.LockResponse:
        assert isinstance(req, pb2.LockRequest)
        return self.lock_response or pb2.LockResponse(
            locked=True,
            name=req.name,
            key=str(uuid.uuid4()),
        )

    def get_try_lock_response(self, req, metadata=None) -> pb2.LockResponse:
        assert isinstance(req, pb2.TryLockRequest)
        return self.try_lock_response or pb2.LockResponse(
            locked=True,
            name=req.name,
            key=str(uuid.uuid4()),
        )


@pytest.fixture
def client():
    return MockedClient(address="ldlm-server:3144")


class TestLock:

    @pytest.mark.parametrize("auto_renew", [True, False])
    @pytest.mark.parametrize(
        "name,kwargs",
        [
            ("mylock1", frozendict({
                "lock_timeout_seconds": 10,
                "size": 1
            })),
            ("testlock", frozendict({
                "lock_timeout_seconds": 0,
                "size": 0
            })),
            ("testlock2", frozendict({"lock_timeout_seconds": None})),
            (
                "mylock1",
                frozendict({
                    "lock_timeout_seconds": 10,
                    "wait_timeout_seconds": 0,
                    "size": 22,
                }),
            ),
            (
                "testlock3",
                frozendict({
                    "lock_timeout_seconds": 0,
                    "wait_timeout_seconds": 20
                }),
            ),
            (
                "testlock2",
                frozendict({
                    "lock_timeout_seconds": None,
                    "wait_timeout_seconds": None,
                    "size": 4,
                }),
            ),
            ("simplelock", frozendict({})),
        ],
    )
    def test_lock(self, name, kwargs, auto_renew, client):
        """
        Test the lock method of the client.

        This test function uses the pytest.mark.parametrize decorator to define multiple sets of parameters for the test.
        The parameters include the lock name, keyword arguments, and the auto_renew flag.
        The function iterates over each set of parameters and performs the following steps:
        1. Sets the _auto_renew_locks attribute of the client to the value of the auto_renew flag.
        2. Uses the mock.patch.object decorator to patch the _start_renew method of the client.
        3. Calls the lock method of the client with the provided name and keyword arguments.
        4. Checks if the _start_renew method was called with the correct arguments if auto_renew is True and lock_timeout_seconds is provided.
        5. Checks if the _start_renew method was not called if auto_renew is False.
        6. Creates a LockRequest object with the provided name and sets the lock_timeout_seconds and wait_timeout_seconds attributes if provided.
        7. Asserts that the Lock method of the client's stub was called with the expected LockRequest object and metadata=None.
        """
        client._auto_renew_locks = auto_renew

        with mock.patch.object(client, "_start_renew") as sr_mock:
            l = client.lock(name, **kwargs)

        # If auto_renew is True and there is a lock timeout, _start_renew should have been called
        if auto_renew and kwargs.get("lock_timeout_seconds"):
            assert sr_mock.mock_calls == [
                mock.call(l, kwargs["lock_timeout_seconds"]),
            ]
        else:
            assert sr_mock.mock_calls == []

        expected = pb2.LockRequest(name=name)
        if kwargs.get("lock_timeout_seconds"):
            expected.lock_timeout_seconds = kwargs["lock_timeout_seconds"]
        if kwargs.get("wait_timeout_seconds"):
            expected.wait_timeout_seconds = kwargs["wait_timeout_seconds"]
        if kwargs.get("size"):
            expected.size = kwargs["size"]

        # Assert Lock() was called with the correct gRPC message
        assert client._stub.Lock.mock_calls == [
            mock.call(
                expected,
                metadata=None,
            )
        ]

    @pytest.mark.parametrize("locked", [True, False])
    @pytest.mark.parametrize(
        "name,kwargs",
        [
            ("mylock1", frozendict({"lock_timeout_seconds": 10})),
            ("testlock", frozendict({
                "lock_timeout_seconds": 0,
                "size": 4,
            })),
            ("testlock2", frozendict({"lock_timeout_seconds": None})),
            (
                "mylock1",
                frozendict({
                    "lock_timeout_seconds": 10,
                    "wait_timeout_seconds": 0,
                    "size": 0,
                }),
            ),
            (
                "testlock3",
                frozendict({
                    "lock_timeout_seconds": 0,
                    "wait_timeout_seconds": 20
                }),
            ),
            (
                "testlock2",
                frozendict({
                    "lock_timeout_seconds": None,
                    "size": 1,
                }),
            ),
            ("simplelock", frozendict({})),
        ],
    )
    def test_context(self, client, name, kwargs, locked):
        """
        Test the behavior of the `lock_context` method of the `client` object in different scenarios by using the `pytest.mark.parametrize` decorator to define multiple sets of parameters. 
        The parameters include the `name`, `kwargs`, and `locked` values. 
        The function iterates over each set of parameters and performs the following steps:
        1. Mocks the `lock` and `unlock` methods of the `client` object to return specific responses.
        2. Calls the `lock_context` method with the specified parameters and asserts the expected mock calls for the `lock` method.
        3. Asserts the expected mock calls for the `unlock` method based on the `locked` parameter.
        """
        with mock.patch.object(client, 'lock', return_value=Lock(client, pb2.LockResponse(name=name, locked=locked, key="foo"))) as lock_mock,\
                mock.patch.object(client, 'unlock', return_value=pb2.UnlockResponse(unlocked=True)) as unlock_mock:
            with client.lock_context(name, **kwargs):
                pass

        assert lock_mock.mock_calls == [
            mock.call(
                name,
                wait_timeout_seconds=kwargs.get("wait_timeout_seconds", 0),
                lock_timeout_seconds=kwargs.get("lock_timeout_seconds"),
                size=kwargs.get("size", 0),
            )
        ]

        if locked:
            assert unlock_mock.mock_calls == [
                mock.call(
                    name,
                    "foo",
                ),
            ]
        else:
            assert unlock_mock.mock_calls == []

    def test_instance_timeout(self):
        """
        Test the lock method of the client with a client instance lock timeout.
        """
        client = MockedClient(
            address="ldlm-server:3144",
            lock_timeout_seconds=10,
            auto_renew_locks=False,
        )
        l = client.lock("foo")

        # Assert Lock() was called with the correct gRPC message
        assert client._stub.Lock.mock_calls == [
            mock.call(
                pb2.LockRequest(
                    name="foo",
                    lock_timeout_seconds=10,
                ),
                metadata=None,
            )
        ]

        assert l.locked

    def test_wait_timeout(self):
        """
        Test the lock method of the client with a wait timeout set.
        """
        client = MockedClient(
            address="ldlm-server:3144",
            auto_renew_locks=False,
        )
        client.lock_response = pb2.LockResponse(
            locked=False,
            error=pb2.Error(
                code=pb2.ErrorCode.LockWaitTimeout,
                message="Lock wait timeout exceeded",
            ))

        l = client.lock("foo", wait_timeout_seconds=1)

        # Assert Lock() was called with the correct gRPC message
        assert client._stub.Lock.mock_calls == [
            mock.call(
                pb2.LockRequest(
                    name="foo",
                    wait_timeout_seconds=1,
                ),
                metadata=None,
            )
        ]

        assert not l.locked  # because the wait timeout was exceeded


class TestTryLock:

    @pytest.mark.parametrize("auto_renew", [True, False])
    @pytest.mark.parametrize(
        "name,kwargs",
        [
            ("mylock1", frozendict({
                "lock_timeout_seconds": 10,
                "size": 0
            })),
            ("testlock", frozendict({
                "lock_timeout_seconds": 0,
                "size": 1
            })),
            ("testlock2", frozendict({
                "lock_timeout_seconds": None,
                "size": 10
            })),
            ("simplelock", frozendict({})),
        ],
    )
    def test_try_lock(self, name, kwargs, auto_renew, client):
        """
        Test the try_lock method of the client.

        This test function uses the pytest.mark.parametrize decorator to define multiple sets of parameters for the test.
        The parameters include the lock name, keyword arguments, and the auto_renew flag.
        The function iterates over each set of parameters and performs the following steps:
        1. Sets the _auto_renew_locks attribute of the client to the value of the auto_renew flag.
        2. Uses the mock.patch.object decorator to patch the _start_renew method of the client.
        3. Calls the try_lock method of the client with the provided name and keyword arguments.
        4. Checks if the _start_renew method was called with the correct arguments if auto_renew is True and lock_timeout_seconds is provided.
        5. Checks if the _start_renew method was not called if auto_renew is False.
        6. Creates a TryLockRequest object with the provided name and sets the lock_timeout_seconds attribute if provided.
        7. Asserts that the TryLock method of the client's stub was called with the expected TryLockRequest object and metadata=None.
        """
        client._auto_renew_locks = auto_renew

        with mock.patch.object(client, "_start_renew") as sr_mock:
            l = client.try_lock(name, **kwargs)

        if auto_renew and kwargs.get("lock_timeout_seconds"):
            assert sr_mock.mock_calls == [
                mock.call(l, kwargs["lock_timeout_seconds"]),
            ]
        else:
            assert sr_mock.mock_calls == []

        expected = pb2.TryLockRequest(name=name)
        if kwargs.get("lock_timeout_seconds"):
            expected.lock_timeout_seconds = kwargs["lock_timeout_seconds"]
        if kwargs.get("size"):
            expected.size = kwargs["size"]

        assert l.name == name
        assert l.locked == True

        assert client._stub.TryLock.mock_calls == [
            mock.call(
                expected,
                metadata=None,
            )
        ]

    @pytest.mark.parametrize("locked", [True, False])
    @pytest.mark.parametrize(
        "name,kwargs",
        [
            ("mylock1", frozendict({"lock_timeout_seconds": 10})),
            ("testlock", frozendict({
                "lock_timeout_seconds": 0,
                "size": 2
            })),
            ("testlock2", frozendict({
                "lock_timeout_seconds": None,
                "size": 0
            })),
            ("simplelock", frozendict({})),
        ],
    )
    def test_context(self, client, name, kwargs, locked):
        """
        Test the behavior of the `try_lock_context` method of the `client` object in different scenarios by using the `pytest.mark.parametrize` decorator to define multiple sets of parameters. 
        The parameters include the `name`, `kwargs`, and `locked` values. 
        The function iterates over each set of parameters and performs the following steps:
        1. Mocks the `try_lock` and `unlock` methods of the `client` object to return specific responses.
        2. Calls the `try_lock_context` method with the specified parameters and asserts the expected mock calls for the `try_lock` method.
        3. Asserts the expected mock calls for the `unlock` method based on the `locked` parameter.
        """
        with mock.patch.object(client, 'try_lock', return_value=Lock(client, pb2.LockResponse(name=name, locked=locked, key="foo"))) as lock_mock,\
                mock.patch.object(client, 'unlock', return_value=pb2.UnlockResponse(unlocked=True)) as unlock_mock:
            with client.try_lock_context(name, **kwargs):
                pass

        assert lock_mock.mock_calls == [
            mock.call(
                name,
                lock_timeout_seconds=kwargs.get("lock_timeout_seconds"),
                size=kwargs.get("size", 0),
            )
        ]

        if locked:
            assert unlock_mock.mock_calls == [
                mock.call(
                    name,
                    "foo",
                ),
            ]
        else:
            assert unlock_mock.mock_calls == []

    def test_instance_timeout(self):
        """
        Test the lock method of the client with a client instance lock timeout.
        """
        client = MockedClient(
            address="ldlm-server:3144",
            lock_timeout_seconds=10,
            auto_renew_locks=False,
        )
        l = client.try_lock("foo")

        # Assert Lock() was called with the correct gRPC message
        assert client._stub.TryLock.mock_calls == [
            mock.call(
                pb2.TryLockRequest(
                    name="foo",
                    lock_timeout_seconds=10,
                ),
                metadata=None,
            )
        ]

        assert l.locked


class TestRenew:

    @pytest.mark.parametrize(
        "name,key,lock_timeout",
        [
            ("mylock1", "oof", 22),
            ("testlock", "ok", 4),
            ("testlock2", "", 8),
            ("simplelock", "foo", 9),
        ],
    )
    def test_renew_lock(self, name, key, lock_timeout, client):
        """
        Test the renew_lock method of the client with different parameter values.
        """
        l = client.renew(name, key, lock_timeout)

        expected = pb2.RenewRequest(name=name,
                                    key=key,
                                    lock_timeout_seconds=lock_timeout)

        assert client._stub.Renew.mock_calls == [
            mock.call(
                expected,
                metadata=None,
            )
        ]

    @pytest.mark.parametrize(
        "name,lock_timeout",
        [
            ("mylock1", 1),
            ("testlock", 3),
            ("testlock2", 0),
        ],
    )
    def test_auto_renew(self, name, lock_timeout, client):
        """
        Test the auto_renew feature of the client with different parameter values.
        """
        with mock.patch.object(client, "min_renew_interval_seconds", 1):
            with client.lock_context(name,
                                     lock_timeout_seconds=lock_timeout) as l:
                time.sleep(lock_timeout + 0.5)

        interval = max(lock_timeout - 30, 1)
        times = max(0, int(lock_timeout / interval))

        expected = pb2.RenewRequest(name=name,
                                    key=l.key,
                                    lock_timeout_seconds=lock_timeout)

        assert client._stub.Renew.mock_calls == [
            mock.call(
                expected,
                metadata=None,
            )
        ] * times


class TestUnlock:

    @pytest.mark.parametrize(
        "name,key",
        [
            ("mylock1", "oof"),
            ("testlock", "ok"),
            ("testlock2", ""),
            ("simplelock", "foo"),
        ],
    )
    def test_unlock(self, name, key, client):
        """
        Test the unlock method of the client with different parameter values.
        """
        l = client.unlock(name, key)

        expected = pb2.UnlockRequest(name=name, key=key)

        assert client._stub.Unlock.mock_calls == [
            mock.call(
                expected,
                metadata=None,
            )
        ]

    def test_remove_renew_timer(self, client):
        """
        Test the remove_renew_timer method of the client with different parameter values.
        """
        l = client.lock("mylock", lock_timeout_seconds=40)

        assert "mylock" in client._lock_timers
        client.unlock("mylock", l.key)
        assert "mylock" not in client._lock_timers


class TestRpcWithRetry:

    @pytest.fixture
    def inactive_rpc_error(self):
        """
        Fixture to create an instance of MyError class which inherits from _InactiveRpcError since
        instantiating _InactiveRpcError requires some gRPC nonsense.
        """

        class MyError(_InactiveRpcError):

            def __init__(self):
                pass

            def _repr(self) -> str:
                return "MyError"

        return MyError

    def test_retry_a_few_errors(self, client, inactive_rpc_error):
        """
        Test the retry mechanism of the client when it encounters a few errors.

        This test function verifies that the client correctly retries the RPC call when it encounters
        specific errors. It sets up a mock for the `TryLock` method of the `client._stub` object to return
        the specified side effects, which include the `inactive_rpc_error` exception. The test then calls
        the `client.try_lock` method with the name "mylock" and asserts that the `TryLock` method was called
        the expected number of times.
        """
        client._retry_delay_seconds = 0
        client._stub.TryLock = mock.MagicMock(side_effect=[
            inactive_rpc_error,
            inactive_rpc_error,
            inactive_rpc_error,
            pb2.LockResponse(locked=True, key="foo"),
        ])
        client.try_lock("mylock")
        assert client._stub.TryLock.mock_calls == [
            mock.call(
                pb2.TryLockRequest(name="mylock"),
                metadata=None,
            )
        ] * 4

    def test_max_retry(self, client, inactive_rpc_error):
        """
        Test the retry mechanism of the client when it encounters a few errors.

        This test function verifies that the client correctly retries the RPC call when it encounters
        specific errors. It sets up a mock for the `TryLock` method of the `client._stub` object to return
        the specified side effects, which include the `inactive_rpc_error` exception. The test then calls
        the `client.try_lock` method with the name "mylock" and asserts that the `TryLock` method was called
        the expected number of times.
        """
        client._retry_delay_seconds = 0
        client._retries = 1
        client._stub.TryLock = mock.MagicMock(side_effect=[
            inactive_rpc_error,
            inactive_rpc_error,
            inactive_rpc_error,
            pb2.LockResponse(locked=True, key="foo"),
        ])
        with pytest.raises(inactive_rpc_error):
            client.try_lock("mylock")
        assert client._stub.TryLock.mock_calls == [
            mock.call(
                pb2.TryLockRequest(name="mylock"),
                metadata=None,
            )
        ] * 2

    def test_password(self):
        """
        Test the password parameter of the client.

        This test function creates an instance of the `MockedClient` class with a password
        authentication. It then calls the `try_lock` method with the lock name "mylock". The test
        asserts that the `TryLock` method of the `c._stub` object was called with the correct
        arguments, including the authorization metadata containing the password.
        """
        c = MockedClient("ldlm-server:3144", password="asdf1234")
        c.try_lock("mylock")
        assert c._stub.TryLock.mock_calls == [
            mock.call(
                pb2.TryLockRequest(name="mylock"),
                metadata=(("authorization", "asdf1234"),),
            )
        ]


class TestCreateChannel:

    @pytest.fixture(autouse=True)
    def mock_stub(self):
        """
        Don't make extra calls to the mocked channel that we want to assert calls for
        """
        with mock.patch("ldlm.base_client.ldlm_grpc.LDLMStub"):
            yield

    @pytest.fixture
    def mock_creds(self):
        with mock.patch("ldlm.client.grpc.ssl_channel_credentials") as m:
            yield m

    @pytest.fixture
    def mock_secure_chan(self):
        with mock.patch("ldlm.client.grpc.secure_channel") as m:
            yield m

    @pytest.fixture
    def mock_insecure_chan(self):
        with mock.patch("ldlm.client.grpc.insecure_channel") as m:
            yield m

    def test_with_ssl_config(self, mock_secure_chan, mock_insecure_chan,
                             mock_creds):
        tls = TLSConfig()
        c = MockedClient("ldlm-server:3144", tls=tls)

        assert mock_secure_chan.mock_calls == [
            mock.call("ldlm-server:3144", mock_creds.return_value),
        ]
        assert mock_insecure_chan.mock_calls == []

    def test_no_ssl_config(self, mock_secure_chan, mock_insecure_chan,
                           mock_creds):
        c = MockedClient("ldlm-server:3144", tls=None)

        assert mock_secure_chan.mock_calls == []
        assert mock_insecure_chan.mock_calls == [
            mock.call("ldlm-server:3144"),
        ]


class TestClose:

    def test_close(self):
        client = Client("ldlm-server:3144")
        client.close()


class TestLockClass:

    def test_unlock_not_locked(self):
        lock = Lock(None, pb2.LockResponse(locked=False))
        with pytest.raises(RuntimeError) as ex:
            lock.unlock()
        assert str(ex.value) == "unlock() called on unlocked lock"

    def test_renew_not_not_locked(self):
        lock = Lock(None, pb2.LockResponse(locked=False))
        with pytest.raises(RuntimeError) as ex:
            lock.renew(1)
        assert str(ex.value) == "renew() called on unlocked lock"

    @pytest.mark.parametrize("locked", [True, False])
    def test_no_client_if_unlocked(self, client, locked):
        lock = Lock(client, pb2.LockResponse(locked=locked))
        assert (lock._client is None) == (not locked)

    @pytest.mark.parametrize("locked", [True, False])
    def test_bool(self, client, locked):
        lock = Lock(client, pb2.LockResponse(locked=locked))
        assert bool(lock) is locked
