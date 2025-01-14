# Avido

Types:

```python
from avido.types import IngestResponse
```

Methods:

- <code title="post /v0/ingest">client.<a href="./src/avido/_client.py">ingest</a>(\*\*<a href="src/avido/types/client_ingest_params.py">params</a>) -> <a href="./src/avido/types/ingest_response.py">IngestResponse</a></code>

# Webhook

Types:

```python
from avido.types import WebhookValidationResponse
```

Methods:

- <code title="post /v0/validate-webhook">client.webhook.<a href="./src/avido/resources/webhook.py">validate</a>(\*\*<a href="src/avido/types/webhook_validate_params.py">params</a>) -> <a href="./src/avido/types/webhook_validation_response.py">WebhookValidationResponse</a></code>

# Evaluations

Types:

```python
from avido.types import EvaluationCase, PaginatedEvaluationCase, EvaluationListResponse
```

Methods:

- <code title="post /v0/evaluations">client.evaluations.<a href="./src/avido/resources/evaluations.py">create</a>(\*\*<a href="src/avido/types/evaluation_create_params.py">params</a>) -> <a href="./src/avido/types/evaluation_case.py">EvaluationCase</a></code>
- <code title="get /v0/evaluations/{id}">client.evaluations.<a href="./src/avido/resources/evaluations.py">retrieve</a>(id) -> <a href="./src/avido/types/evaluation_case.py">EvaluationCase</a></code>
- <code title="get /v0/evaluations">client.evaluations.<a href="./src/avido/resources/evaluations.py">list</a>(\*\*<a href="src/avido/types/evaluation_list_params.py">params</a>) -> <a href="./src/avido/types/evaluation_list_response.py">SyncOffsetPagination[EvaluationListResponse]</a></code>

# Applications

Types:

```python
from avido.types import ApplicationResponse, PaginatedApplication, ApplicationListResponse
```

Methods:

- <code title="post /v0/applications">client.applications.<a href="./src/avido/resources/applications.py">create</a>(\*\*<a href="src/avido/types/application_create_params.py">params</a>) -> <a href="./src/avido/types/application_response.py">ApplicationResponse</a></code>
- <code title="get /v0/applications/{id}">client.applications.<a href="./src/avido/resources/applications.py">retrieve</a>(id) -> <a href="./src/avido/types/application_response.py">ApplicationResponse</a></code>
- <code title="get /v0/applications">client.applications.<a href="./src/avido/resources/applications.py">list</a>(\*\*<a href="src/avido/types/application_list_params.py">params</a>) -> <a href="./src/avido/types/application_list_response.py">SyncOffsetPagination[ApplicationListResponse]</a></code>

# Topics

Types:

```python
from avido.types import EvaluationTopicResponse, PaginatedEvaluationTopic, TopicListResponse
```

Methods:

- <code title="post /v0/topics">client.topics.<a href="./src/avido/resources/topics.py">create</a>(\*\*<a href="src/avido/types/topic_create_params.py">params</a>) -> <a href="./src/avido/types/evaluation_topic_response.py">EvaluationTopicResponse</a></code>
- <code title="get /v0/topics/{id}">client.topics.<a href="./src/avido/resources/topics.py">retrieve</a>(id) -> <a href="./src/avido/types/evaluation_topic_response.py">EvaluationTopicResponse</a></code>
- <code title="get /v0/topics">client.topics.<a href="./src/avido/resources/topics.py">list</a>(\*\*<a href="src/avido/types/topic_list_params.py">params</a>) -> <a href="./src/avido/types/topic_list_response.py">SyncOffsetPagination[TopicListResponse]</a></code>

# Tests

Types:

```python
from avido.types import PaginatedTest, TestResponse, TestListResponse
```

Methods:

- <code title="get /v0/tests/{id}">client.tests.<a href="./src/avido/resources/tests.py">retrieve</a>(id) -> <a href="./src/avido/types/test_response.py">TestResponse</a></code>
- <code title="get /v0/tests">client.tests.<a href="./src/avido/resources/tests.py">list</a>(\*\*<a href="src/avido/types/test_list_params.py">params</a>) -> <a href="./src/avido/types/test_list_response.py">SyncOffsetPagination[TestListResponse]</a></code>
- <code title="post /v0/tests/run">client.tests.<a href="./src/avido/resources/tests.py">run</a>(\*\*<a href="src/avido/types/test_run_params.py">params</a>) -> <a href="./src/avido/types/test_response.py">TestResponse</a></code>

# Threads

Types:

```python
from avido.types import ThreadListResponse, ThreadResponse
```

Methods:

- <code title="get /v0/threads/{id}">client.threads.<a href="./src/avido/resources/threads.py">retrieve</a>(id) -> <a href="./src/avido/types/thread_response.py">ThreadResponse</a></code>
- <code title="get /v0/threads">client.threads.<a href="./src/avido/resources/threads.py">list</a>(\*\*<a href="src/avido/types/thread_list_params.py">params</a>) -> <a href="./src/avido/types/thread_list_response.py">ThreadListResponse</a></code>
