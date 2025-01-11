# Infisical Python SDK

The Infisical SDK provides a convenient way to interact with the Infisical API. 

### Migrating to version 1.0.0 or above

We have recently rolled out our first stable version of the SDK, version `1.0.0` and above.

The 1.0.0 version comes with a few key changes that may change how you're using the SDK.
1. **Removal of `rest`**: The SDK no longer exposes the entire Infisical API. This was nessecary as we have moved away from using an OpenAPI generator approach. We aim to add support for more API resources in the near future. If you have any specific requests, please [open an issue](https://github.com/Infisical/python-sdk-official/issues).

2. **New response types**: The 1.0.0 release uses return types that differ from the older versions. The new return types such as `BaseSecret`, are all exported from the Infisical SDK.

3. **Property renaming**: Some properties on the responses have been slightly renamed. An example of this would be that the `secret_key` property on the `get_secret_by_name()` method, that has been renamed to `secretKey`.

With this in mind, you're ready to upgrade your SDK version to `1.0.0` or above. 

You can refer to our [legacy documentation](https://github.com/Infisical/python-sdk-official/tree/9b0403938ee5ae599d42c5f1fdf9158671a15606?tab=readme-ov-file#infisical-python-sdk) if need be.

## Requirements

Python 3.7+

## Installation

```bash
pip install infisicalsdk
```

## Getting Started

```python
from infisical_sdk import InfisicalSDKClient

# Initialize the client
client = InfisicalSDKClient(host="https://app.infisical.com")

# Authenticate (example using Universal Auth)
client.auth.universal_auth.login(client_id="your_client_id", client_secret="your_client_secret")

# Use the SDK to interact with Infisical
secrets = client.secrets.list_secrets(project_id="your_project_id", environment_slug="dev", secret_path="/")
```

## Core Methods

The SDK methods are organized into the following high-level categories:

1. `auth`: Handles authentication methods.
2. `secrets`: Manages CRUD operations for secrets.

### `auth`

The `Auth` component provides methods for authentication:

#### Universal Auth

```python
response = client.auth.universal_auth.login(client_id="your_client_id", client_secret="your_client_secret")
```

#### AWS Auth

```python
response = client.auth.aws_auth.login(identity_id="your_identity_id")
```

### `secrets`

This sub-class handles operations related to secrets:

#### List Secrets

```python
secrets = client.secrets.list_secrets(
    project_id="your_project_id",
    environment_slug="dev",
    secret_path="/",
    expand_secret_references=True,
    recursive=False,
    include_imports=True,
    tag_filters=[]
)
```

**Parameters:**
- `project_id` (str): The ID of your project.
- `environment_slug` (str): The environment in which to list secrets (e.g., "dev").
- `secret_path` (str): The path to the secrets.
- `expand_secret_references` (bool): Whether to expand secret references.
- `recursive` (bool): Whether to list secrets recursively.
- `include_imports` (bool): Whether to include imported secrets.
- `tag_filters` (List[str]): Tags to filter secrets.

**Returns:**
- `ListSecretsResponse`: The response containing the list of secrets.

#### Create Secret

```python
new_secret = client.secrets.create_secret_by_name(
    secret_name="NEW_SECRET",
    project_id="your_project_id",
    secret_path="/",
    environment_slug="dev",
    secret_value="secret_value",
    secret_comment="Optional comment",
    skip_multiline_encoding=False,
    secret_reminder_repeat_days=30,  # Optional
    secret_reminder_note="Remember to update this secret"  # Optional
)
```

**Parameters:**
- `secret_name` (str): The name of the secret.
- `project_id` (str): The ID of your project.
- `secret_path` (str): The path to the secret.
- `environment_slug` (str): The environment in which to create the secret.
- `secret_value` (str): The value of the secret.
- `secret_comment` (str, optional): A comment associated with the secret.
- `skip_multiline_encoding` (bool, optional): Whether to skip encoding for multiline secrets.
- `secret_reminder_repeat_days` (Union[float, int], optional): Number of days after which to repeat secret reminders.
- `secret_reminder_note` (str, optional): A note for the secret reminder.

**Returns:**
- `BaseSecret`: The response after creating the secret.

#### Update Secret

```python
updated_secret = client.secrets.update_secret_by_name(
    current_secret_name="EXISTING_SECRET",
    project_id="your_project_id",
    secret_path="/",
    environment_slug="dev",
    secret_value="new_secret_value",
    secret_comment="Updated comment",  # Optional
    skip_multiline_encoding=False,
    secret_reminder_repeat_days=30,  # Optional
    secret_reminder_note="Updated reminder note",  # Optional
    new_secret_name="NEW_NAME"  # Optional
)
```

**Parameters:**
- `current_secret_name` (str): The current name of the secret.
- `project_id` (str): The ID of your project.
- `secret_path` (str): The path to the secret.
- `environment_slug` (str): The environment in which to update the secret.
- `secret_value` (str, optional): The new value of the secret.
- `secret_comment` (str, optional): An updated comment associated with the secret.
- `skip_multiline_encoding` (bool, optional): Whether to skip encoding for multiline secrets.
- `secret_reminder_repeat_days` (Union[float, int], optional): Updated number of days after which to repeat secret reminders.
- `secret_reminder_note` (str, optional): An updated note for the secret reminder.
- `new_secret_name` (str, optional): A new name for the secret.

**Returns:**
- `BaseSecret`: The response after updating the secret.

#### Get Secret by Name

```python
secret = client.secrets.get_secret_by_name(
    secret_name="EXISTING_SECRET",
    project_id="your_project_id",
    environment_slug="dev",
    secret_path="/",
    expand_secret_references=True,
    include_imports=True,
    version=None  # Optional
)
```

**Parameters:**
- `secret_name` (str): The name of the secret.
- `project_id` (str): The ID of your project.
- `environment_slug` (str): The environment in which to retrieve the secret.
- `secret_path` (str): The path to the secret.
- `expand_secret_references` (bool): Whether to expand secret references.
- `include_imports` (bool): Whether to include imported secrets.
- `version` (str, optional): The version of the secret to retrieve. Fetches the latest by default.

**Returns:**
- `BaseSecret`: The response containing the secret.

#### Delete Secret by Name

```python
deleted_secret = client.secrets.delete_secret_by_name(
    secret_name="EXISTING_SECRET",
    project_id="your_project_id",
    environment_slug="dev",
    secret_path="/"
)
```

**Parameters:**
- `secret_name` (str): The name of the secret to delete.
- `project_id` (str): The ID of your project.
- `environment_slug` (str): The environment in which to delete the secret.
- `secret_path` (str): The path to the secret.

**Returns:**
- `BaseSecret`: The response after deleting the secret.
