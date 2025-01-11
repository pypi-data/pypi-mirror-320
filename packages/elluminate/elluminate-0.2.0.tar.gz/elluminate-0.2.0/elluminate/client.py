import asyncio
import atexit
import os
import time
from typing import Any, ClassVar, Literal

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_random_exponential

from elluminate.schemas import (
    BatchCreatePromptResponseRequest,
    BatchCreatePromptResponseStatus,
    BatchCreateRatingRequest,
    BatchCreateRatingResponseStatus,
    CreateCollectionRequest,
    CreateExperimentRequest,
    CreatePromptResponseRequest,
    CreatePromptTemplateRequest,
    CreateRatingRequest,
    CreateTemplateVariablesRequest,
    Criterion,
    Experiment,
    GenerateCriteriaRequest,
    GenerationMetadata,
    LLMConfig,
    Project,
    PromptResponse,
    PromptTemplate,
    Rating,
    RatingMode,
    TemplateVariables,
    TemplateVariablesCollection,
    TemplateVariablesCollectionWithEntries,
)
from elluminate.utils import raise_for_status_with_detail, run_async

# TODO: Actually only retry for Database/Timeout errors
retry_request = retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=3, min=10, max=120))


class Client:
    _semaphore: ClassVar[asyncio.Semaphore] = asyncio.Semaphore(10)

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        api_key_env: str = "ELLUMINATE_API_KEY",
        base_url_env: str = "ELLUMINATE_BASE_URL",
        timeout: float = 120.0,
    ) -> None:
        """Initialize the Elluminate SDK client.

        Args:
            base_url (str): Base URL of the Elluminate API. Defaults to "https://elluminate.de".
            api_key (str | None): API key for authentication. If not provided, will look for key in environment variable given by `api_key_env`.
            api_key_env (str): Name of environment variable containing API key. Defaults to "ELLUMINATE_API_KEY".
            base_url_env (str): Name of environment variable containing base URL. Defaults to "ELLUMINATE_BASE_URL". If set, overrides base_url.
            timeout (float): Timeout in seconds for API requests. Defaults to 30.0.

        Raises:
            ValueError: If no API key is provided or found in environment.

        """
        # Init the API key
        self.api_key = api_key or os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError(f"{api_key_env} not set.")

        # Init the base URL. Use a sane default if no values are provided
        self.base_url = base_url or os.getenv(base_url_env) or "https://elluminate.de"
        if not base_url and os.getenv(base_url_env):
            logger.debug(f"Using base URL from environment: {self.base_url}")

        # Create async client with the API key header
        headers = {"X-API-Key": self.api_key}
        self.timeout = timeout
        timeout_config = httpx.Timeout(self.timeout)
        self.async_session = httpx.AsyncClient(headers=headers, timeout=timeout_config)
        # This is only needed to get the project synchronously
        self.sync_session = httpx.Client(headers=headers, timeout=timeout_config)

        # Load the project and set the route prefix
        self.project = self.load_project()
        self.project_route_prefix = f"{self.base_url}/api/v0/projects/{self.project.id}"

    async def aload_project(self) -> Project:
        """Async version of load_project."""
        response = await self.async_session.get(f"{self.base_url}/api/v0/projects/")
        raise_for_status_with_detail(response)
        projects = [Project.model_validate(project) for project in response.json()["items"]]
        if not projects:
            raise RuntimeError("No projects found.")
        return projects[0]

    def load_project(self) -> Project:
        """Loads the project associated with the API key.

        Returns:
            (Project): The project associated with the API key.

        Raises:
            RuntimeError: If no projects are found.

        """
        response = self.sync_session.get(f"{self.base_url}/api/v0/projects/")
        raise_for_status_with_detail(response)
        projects = [Project.model_validate(project) for project in response.json()["items"]]
        if not projects:
            raise RuntimeError("No projects found.")
        return projects[0]

    async def acreate_prompt_template(
        self,
        user_prompt_template: str,
        *,
        name: str | None = None,
        parent_prompt_template_id: int | None = None,
        default_collection_id: int | None = None,
    ) -> PromptTemplate:
        """Async version of create_prompt_template."""
        response = await self.async_session.post(
            f"{self.project_route_prefix}/prompt_templates/",
            json=CreatePromptTemplateRequest(
                name=name,
                user_prompt_template_str=user_prompt_template,
                parent_prompt_template_id=parent_prompt_template_id,
                default_collection_id=default_collection_id,
            ).model_dump(),
        )
        raise_for_status_with_detail(response)
        return PromptTemplate.model_validate(response.json())

    def create_prompt_template(
        self,
        user_prompt_template: str,
        *,
        name: str | None = None,
        parent_prompt_template_id: int | None = None,
        default_collection_id: int | None = None,
    ) -> PromptTemplate:
        """Creates a new prompt template.

        Each created prompt template is assigned a default collection. If no `default_collection_id` is provided, a random
        default collection is created.

        Args:
            user_prompt_template (str): The template string containing variables in {variable_name} format.
            name (str | None): Optional name for the template. If not provided, a random name will be generated.
            parent_prompt_template_id (int | None): Optional ID of parent template to inherit from.
            default_collection_id (int | None): Optional ID of default template variables collection.

        Returns:
            (PromptTemplate): The created prompt template.

        Raises:
            httpx.HTTPStatusError: If a prompt template with the same name and content already exists or the given parent according to `parent_prompt_template_id` does not exist.

        """
        return run_async(self.acreate_prompt_template)(
            user_prompt_template,
            name=name,
            parent_prompt_template_id=parent_prompt_template_id,
            default_collection_id=default_collection_id,
        )

    async def aget_prompt_template(
        self,
        *,
        name: str,
        version: int | Literal["latest"] = "latest",
    ) -> PromptTemplate:
        """Async version of get_prompt_template."""
        params = {"name": name}
        if version != "latest":
            params["version"] = str(version)

        response = await self.async_session.get(f"{self.project_route_prefix}/prompt_templates/", params=params)
        raise_for_status_with_detail(response)
        templates = [PromptTemplate.model_validate(template) for template in response.json().get("items", [])]
        if not templates:
            raise ValueError(f"No prompt template found with name {name} and version {version}")
        return templates[0]

    def get_prompt_template(
        self,
        *,
        name: str,
        version: int | Literal["latest"] = "latest",
    ) -> PromptTemplate:
        """Get a prompt template by name and version.

        Args:
            name (str): Name of the prompt template.
            version (int | Literal["latest"]): Version number or "latest". Defaults to "latest".

        Returns:
            (PromptTemplate): The requested prompt template.

        Raises:
            ValueError: If no template is found with given name and version.

        """
        return run_async(self.aget_prompt_template)(name=name, version=version)

    async def aget_or_create_prompt_template(
        self,
        user_prompt_template: str,
        *,
        name: str,
        parent_prompt_template_id: int | None = None,
        default_collection_id: int | None = None,
    ) -> tuple[PromptTemplate, bool]:
        """Async version of get_or_create_prompt_template.

        Gets the prompt template by its name and user prompt contents if it exists.
        If a prompt template with the same name exists, but the user prompt is new,
        then it creates a new prompt template version with the new user prompt
        which will be the new latest version. If no such prompt template name exists,
        the user prompt will create a new prompt template with version 1.
        """
        try:
            # Try to create first
            template = await self.acreate_prompt_template(
                user_prompt_template,
                name=name,
                parent_prompt_template_id=parent_prompt_template_id,
                default_collection_id=default_collection_id,
            )
            return template, True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                # If we got a conflict, extract the existing template ID and fetch it
                error_data = e.response.json()
                template_id = error_data.get("prompt_template_id")
                if template_id is None:
                    raise ValueError("Received 409 without prompt_template_id") from e

                response = await self.async_session.get(
                    f"{self.project_route_prefix}/prompt_templates/{template_id}/",
                )
                raise_for_status_with_detail(response)
                return PromptTemplate.model_validate(response.json()), False
            raise

    def get_or_create_prompt_template(
        self,
        user_prompt_template: str,
        *,
        name: str,
        parent_prompt_template_id: int | None = None,
        default_collection_id: int | None = None,
    ) -> tuple[PromptTemplate, bool]:
        """Get an existing prompt template or create a new one.

        Args:
            user_prompt_template (str): The template string containing variables in {variable} format.
            name (str): Name for the template.
            parent_prompt_template_id (int | None): Optional ID of parent template to inherit from.
            default_collection_id (int | None): Optional ID of default template variables collection.

        Returns:
            tuple[PromptTemplate, bool]: A tuple containing:
                - The prompt template
                - Boolean indicating if a new template was created (True) or existing one returned (False)

        Raises:
            ValueError: If a 409 response is received without a prompt_template_id.

        """
        return run_async(self.aget_or_create_prompt_template)(
            user_prompt_template,
            name=name,
            parent_prompt_template_id=parent_prompt_template_id,
            default_collection_id=default_collection_id,
        )

    async def acreate_llm_config(
        self,
        name: str,
        llm_model_name: str,
        api_key: str,
        *,
        llm_base_url: str | None = None,
        api_version: str | None = None,
        max_connections: int = 20,
        max_retries: int | None = None,
        timeout: int | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        temperature: float | None = None,
        best_of: int | None = None,
        top_k: int | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
    ) -> LLMConfig:
        """Async version of create_llm_config."""
        # The create request data is the same as the `LLMConfig`, just without the ID
        create_request_data = LLMConfig(
            name=name,
            llm_model_name=llm_model_name,
            api_key=api_key,
            llm_base_url=llm_base_url,
            api_version=api_version,
            max_connections=max_connections,
            max_retries=max_retries,
            timeout=timeout,
            system_message=system_message,
            max_tokens=max_tokens,
            top_p=top_p,
            temperature=temperature,
            best_of=best_of,
            top_k=top_k,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
        ).model_dump(exclude={"id"})
        response = await self.async_session.post(
            f"{self.project_route_prefix}/llm_configs/",
            json=create_request_data,
        )
        raise_for_status_with_detail(response)
        return LLMConfig.model_validate(response.json())

    def create_llm_config(
        self,
        name: str,
        llm_model_name: str,
        api_key: str,
        *,
        llm_base_url: str | None = None,
        api_version: str | None = None,
        max_connections: int = 20,
        max_retries: int | None = None,
        timeout: int | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        temperature: float | None = None,
        best_of: int | None = None,
        top_k: int | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
    ) -> LLMConfig:
        """Create a new LLM configuration.

        Args:
            name (str): Name for the LLM config.
            llm_model_name (str): Name of the LLM model.
            api_key (str): API key for the LLM service.
            llm_base_url (str | None): Optional base URL for the LLM service.
            api_version (str | None): Optional API version.
            max_connections (int): Maximum number of concurrent connections to the LLM provider.
            max_retries (int | None): Optional maximum number of retries.
            timeout (int | None): Optional timeout in seconds.
            system_message (str | None): Optional system message for the LLM.
            max_tokens (int | None): Optional maximum tokens to generate.
            top_p (float | None): Optional nucleus sampling parameter.
            temperature (float | None): Optional temperature parameter.
            best_of (int | None): Optional number of completions to generate.
            top_k (int | None): Optional top-k sampling parameter.
            logprobs (bool | None): Optional flag to return log probabilities.
            top_logprobs (int | None): Optional number of top log probabilities to return.

        Returns:
            (LLMConfig): The created LLM configuration.

        """
        return run_async(self.acreate_llm_config)(
            name,
            llm_model_name,
            api_key,
            llm_base_url=llm_base_url,
            api_version=api_version,
            max_connections=max_connections,
            max_retries=max_retries,
            timeout=timeout,
            system_message=system_message,
            max_tokens=max_tokens,
            top_p=top_p,
            temperature=temperature,
            best_of=best_of,
            top_k=top_k,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
        )

    async def aget_llm_config(self, name: str) -> LLMConfig:
        """Sync version of aget_llm_config."""
        response = await self.async_session.get(
            f"{self.project_route_prefix}/llm_configs/",
            params={"name": name},
        )
        raise_for_status_with_detail(response)
        configs = [LLMConfig.model_validate(config) for config in response.json()["items"]]
        if not configs:
            raise ValueError(f"No LLM config found with name '{name}'")
        return configs[0]

    def get_llm_config(self, name: str) -> LLMConfig:
        """Get an LLM config by name.

        Args:
            name (str): Name of the LLM config.

        Returns:
            (LLMConfig): The requested LLM config.

        Raises:
            ValueError: If no LLM config is found with the given name.

        """
        return run_async(self.aget_llm_config)(name=name)

    async def aget_or_create_llm_config(
        self,
        name: str,
        llm_model_name: str,
        api_key: str,
        *,
        llm_base_url: str | None = None,
        api_version: str | None = None,
        max_connections: int = 20,
        max_retries: int | None = None,
        timeout: int | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        temperature: float | None = None,
        best_of: int | None = None,
        top_k: int | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
    ) -> tuple[LLMConfig, bool]:
        """Fetch an llm config by name. If it does not exist, then create one with all of the given parameters."""
        try:
            # Try to get existing config first
            llm_config = await self.aget_llm_config(name=name)
            return llm_config, False
        except ValueError:
            # If not found, create new config
            llm_config = await self.acreate_llm_config(
                name=name,
                llm_model_name=llm_model_name,
                api_key=api_key,
                llm_base_url=llm_base_url,
                api_version=api_version,
                max_connections=max_connections,
                max_retries=max_retries,
                timeout=timeout,
                system_message=system_message,
                max_tokens=max_tokens,
                top_p=top_p,
                temperature=temperature,
                best_of=best_of,
                top_k=top_k,
                logprobs=logprobs,
                top_logprobs=top_logprobs,
            )
            return llm_config, True

    def get_or_create_llm_config(
        self,
        name: str,
        llm_model_name: str,
        api_key: str,
        *,
        llm_base_url: str | None = None,
        api_version: str | None = None,
        max_connections: int = 20,
        max_retries: int | None = None,
        timeout: int | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        temperature: float | None = None,
        best_of: int | None = None,
        top_k: int | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
    ) -> tuple[LLMConfig, bool]:
        """Get an existing LLM config or create a new one.

        Args:
            name (str): Name for the LLM config.
            llm_model_name (str): Name of the LLM model.
            api_key (str): API key for the LLM service.
            llm_base_url (str | None): Optional base URL for the LLM service.
            api_version (str | None): Optional API version.
            max_connections (int): Maximum number of concurrent connections to the LLM provider.
            max_retries (int | None): Optional maximum number of retries.
            timeout (int | None): Optional timeout in seconds.
            system_message (str | None): Optional system message for the LLM.
            max_tokens (int | None): Optional maximum tokens to generate.
            top_p (float | None): Optional nucleus sampling parameter.
            temperature (float | None): Optional temperature parameter.
            best_of (int | None): Optional number of completions to generate.
            top_k (int | None): Optional top-k sampling parameter.
            logprobs (bool | None): Optional flag to return log probabilities.
            top_logprobs (int | None): Optional number of top log probabilities to return.

        Returns:
            tuple[LLMConfig, bool]: A tuple containing:
                - The LLM configuration
                - Boolean indicating if a new config was created (True) or existing one returned (False)

        """
        return run_async(self.aget_or_create_llm_config)(
            name=name,
            llm_model_name=llm_model_name,
            api_key=api_key,
            llm_base_url=llm_base_url,
            api_version=api_version,
            max_connections=max_connections,
            max_retries=max_retries,
            timeout=timeout,
            system_message=system_message,
            max_tokens=max_tokens,
            top_p=top_p,
            temperature=temperature,
            best_of=best_of,
            top_k=top_k,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
        )

    async def _form_response_request_helper(
        self,
        prompt_template: PromptTemplate,
        *,
        llm_config: LLMConfig | None = None,
        response: str | None = None,
        template_variables: dict[str, str] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        template_variables_id: int | None = None,
        metadata: LLMConfig | GenerationMetadata | None = None,
    ) -> CreatePromptResponseRequest:
        """Helper function for creating responses."""
        # Validate that a response cannot be provided along with a llm_config
        if llm_config is not None and (response is not None or metadata is not None):
            raise ValueError("A llm_config cannot be provided along with a response or metadata.")

        if template_variables_id is None and template_variables is not None:
            if template_variables_collection is None:
                template_variables_collection = prompt_template.default_template_variables_collection

            if template_variables_collection is None:
                raise ValueError("No template variables collection specified")

            variables_response, _ = await self.aget_or_add_entry(
                template_variables_collection,
                template_variables,
            )
            template_variables_id = variables_response.id

        # If metadata is an LLMConfig, wrap it in GenerationMetadata
        if isinstance(metadata, LLMConfig):
            metadata = GenerationMetadata(
                llm_model_config=metadata,
            )

        request_data = CreatePromptResponseRequest(
            llm_config_id=llm_config.id if llm_config else None,
            response=response,
            prompt_template_id=prompt_template.id,
            template_variables_id=template_variables_id,
            metadata=metadata,
        )
        return request_data

    async def _form_batch_response_request_helper(
        self,
        prompt_template: PromptTemplate,
        *,
        batch_responses: list[str] | None = None,
        batch_template_variables: list[dict[str, str]] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        batch_template_variables_ids: list[int] | None = None,
        llm_config: LLMConfig | None = None,
        batch_metadata: list[LLMConfig | GenerationMetadata | None] | None = None,
    ) -> BatchCreatePromptResponseRequest:
        # Get length from first non-None list parameter
        n_responses = None
        for param_list in [batch_responses, batch_template_variables, batch_template_variables_ids, batch_metadata]:
            if param_list is not None:
                n_responses = len(param_list)
                break

        if n_responses is None:
            raise ValueError("Batch inputs must be provided.")

        # Validate all non-None lists have matching length
        for param_name, param_list in [
            ("batch_responses", batch_responses),
            ("batch_template_variables", batch_template_variables),
            ("batch_template_variables_ids", batch_template_variables_ids),
            ("batch_metadata", batch_metadata),
        ]:
            if param_list is not None and len(param_list) != n_responses:
                raise ValueError(f"Expected {n_responses} {param_name} entries, got {len(param_list)}")

        # Transform `None` list parameters into lists of `None` values
        processed_params = {
            "batch_responses": batch_responses,
            "batch_template_variables": batch_template_variables,
            "batch_template_variables_ids": batch_template_variables_ids,
            "batch_metadata": batch_metadata,
        }

        processed_params = {
            key: value if value is not None else [None] * n_responses for key, value in processed_params.items()
        }

        # Create the batch request
        batch_request_data = [
            await self._form_response_request_helper(
                prompt_template,
                llm_config=llm_config,
                response=response,
                template_variables=template_variables,
                template_variables_collection=template_variables_collection,
                template_variables_id=template_variables_id,
                metadata=metadata,
            )
            for response, template_variables, template_variables_id, metadata in zip(
                processed_params["batch_responses"],
                processed_params["batch_template_variables"],
                processed_params["batch_template_variables_ids"],
                processed_params["batch_metadata"],
            )
        ]

        return BatchCreatePromptResponseRequest(
            prompt_response_ins=batch_request_data,
        )

    @retry_request
    async def aadd_response(
        self,
        prompt_template: PromptTemplate,
        response: str,
        *,
        template_variables: dict[str, str] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        template_variables_id: int | None = None,
        metadata: LLMConfig | GenerationMetadata | None = None,
    ) -> PromptResponse:
        """Async version of add_response."""
        async with self._semaphore:
            request_data = await self._form_response_request_helper(
                prompt_template,
                llm_config=None,
                response=response,
                template_variables=template_variables,
                template_variables_collection=template_variables_collection,
                template_variables_id=template_variables_id,
                metadata=metadata,
            )

            response = await self.async_session.post(
                f"{self.project_route_prefix}/responses/",
                json=request_data.model_dump(),
            )
            raise_for_status_with_detail(response)
            return PromptResponse.model_validate(response.json())

    def add_response(
        self,
        prompt_template: PromptTemplate,
        response: str,
        *,
        template_variables: dict[str, str] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        template_variables_id: int | None = None,
        metadata: LLMConfig | GenerationMetadata | None = None,
    ) -> PromptResponse:
        """Add a response to a prompt template.

        Args:
            prompt_template (PromptTemplate): The prompt template to add the response to.
            response (str): The response to add.
            template_variables (dict[str, str] | None): The template variables to use for the response.
            template_variables_collection (TemplateVariablesCollection | None): The collection to use for the template variables.
            template_variables_id (int | None): The ID of the template variables to use.
            metadata (LLMConfig | GenerationMetadata | None): Optional metadata to associate with the response.

        Returns:
            PromptResponse: The newly created prompt response object.

        """
        return run_async(self.aadd_response)(
            prompt_template,
            response,
            template_variables=template_variables,
            template_variables_collection=template_variables_collection,
            template_variables_id=template_variables_id,
            metadata=metadata,
        )

    @retry_request
    async def abatch_add_responses(
        self,
        prompt_template: PromptTemplate,
        batch_responses: list[str],
        *,
        batch_template_variables: list[dict[str, str]] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        batch_template_variables_ids: list[int] | None = None,
        batch_metadata: list[LLMConfig | GenerationMetadata | None] | None = None,
    ) -> list[PromptResponse]:
        """Batched version of add_response.

        Args:
            prompt_template (PromptTemplate): The prompt template to add responses to.
            batch_responses (list[str]): List of responses to add.
            batch_template_variables (list[dict[str, str]] | None): List of template variables for each response.
            template_variables_collection (TemplateVariablesCollection | None): The collection to use for the template variables.
            batch_template_variables_ids (list[int] | None): List of template variable IDs for each response.
            batch_metadata (list[LLMConfig | GenerationMetadata | None] | None): List of metadata for each response.

        Returns:
            list[PromptResponse]: List of newly created prompt response objects.

        """
        request_data = await self._form_batch_response_request_helper(
            prompt_template,
            batch_responses=batch_responses,
            batch_template_variables=batch_template_variables,
            template_variables_collection=template_variables_collection,
            batch_template_variables_ids=batch_template_variables_ids,
            llm_config=None,
            batch_metadata=batch_metadata,
        )
        async with self._semaphore:
            response = await self.async_session.post(
                f"{self.project_route_prefix}/responses/batches/",
                json=request_data.model_dump(),
            )
            raise_for_status_with_detail(response)
            task_id = response.json()

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            # For the status
            response = await self.async_session.get(
                f"{self.project_route_prefix}/responses/batches/{task_id}",
            )
            raise_for_status_with_detail(response)
            status = BatchCreatePromptResponseStatus.model_validate(response.json())
            if status.status == "FAILURE":
                raise RuntimeError("Failed to batch add responses.")
            elif status.status == "SUCCESS":
                result = status.result
                if result is None:
                    raise RuntimeError("Failed to batch add responses.")
                else:
                    return result

            # Delay before looping again
            await asyncio.sleep(3)
        else:
            raise TimeoutError("Batch add responses timed out.")

    def batch_add_responses(
        self,
        prompt_template: PromptTemplate,
        batch_responses: list[str],
        *,
        batch_template_variables: list[dict[str, str]] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        batch_template_variables_ids: list[int] | None = None,
        batch_metadata: list[LLMConfig | GenerationMetadata | None] | None = None,
    ) -> list[PromptResponse]:
        """Batch add multiple responses to a prompt template."""
        return run_async(self.abatch_add_responses)(
            prompt_template,
            batch_responses,
            batch_template_variables=batch_template_variables,
            template_variables_collection=template_variables_collection,
            batch_template_variables_ids=batch_template_variables_ids,
            batch_metadata=batch_metadata,
        )

    @retry_request
    async def agenerate_response(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: dict[str, str] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        template_variables_id: int | None = None,
        llm_config: LLMConfig | None = None,
    ) -> PromptResponse:
        """Async version of generate_response."""
        async with self._semaphore:
            request_data = await self._form_response_request_helper(
                prompt_template,
                llm_config=llm_config,
                response=None,
                template_variables=template_variables,
                template_variables_collection=template_variables_collection,
                template_variables_id=template_variables_id,
                metadata=None,
            )

            response = await self.async_session.post(
                f"{self.project_route_prefix}/responses/",
                json=request_data.model_dump(),
            )
            raise_for_status_with_detail(response)
            return PromptResponse.model_validate(response.json())

    def generate_response(
        self,
        prompt_template: PromptTemplate,
        *,
        llm_config: LLMConfig | None = None,
        template_variables: dict[str, str] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        template_variables_id: int | None = None,
    ) -> PromptResponse:
        """Generate a response for a prompt template.

        Args:
            prompt_template (PromptTemplate): The prompt template to generate a response for.
            llm_config (LLMConfig | None): Optional LLMConfig to use for generation.
            template_variables (dict[str, str] | None): The template variables to use for the response.
            template_variables_collection (TemplateVariablesCollection | None): The collection to use for the template variables.
            template_variables_id (int | None): The ID of the template variables to use.

        Returns:
            PromptResponse: The newly created prompt response object.

        """
        return run_async(self.agenerate_response)(
            prompt_template,
            llm_config=llm_config,
            template_variables=template_variables,
            template_variables_collection=template_variables_collection,
            template_variables_id=template_variables_id,
        )

    @retry_request
    async def abatch_generate_responses(
        self,
        prompt_template: PromptTemplate,
        *,
        batch_template_variables: list[dict[str, str]] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        batch_template_variables_ids: list[int] | None = None,
        llm_config: LLMConfig | None = None,
        batch_metadata: list[LLMConfig | GenerationMetadata | None] | None = None,
    ) -> list[PromptResponse]:
        """Batch generate responses using a prompt template.

        Args:
            prompt_template (PromptTemplate): The prompt template to use for generation.
            batch_template_variables (list[dict[str, str]] | None): List of template variables for each response.
            template_variables_collection (TemplateVariablesCollection | None): The collection to use for the template variables.
            batch_template_variables_ids (list[int] | None): List of template variable IDs for each response.
            llm_config (LLMConfig | None): Optional LLMConfig to use for generation.
            batch_metadata (list[LLMConfig | GenerationMetadata | None] | None): List of metadata for each response.

        Returns:
            list[PromptResponse]: List of newly created prompt response objects.

        """
        request_data = await self._form_batch_response_request_helper(
            prompt_template,
            batch_responses=None,
            batch_template_variables=batch_template_variables,
            template_variables_collection=template_variables_collection,
            batch_template_variables_ids=batch_template_variables_ids,
            llm_config=llm_config,
            batch_metadata=batch_metadata,
        )
        async with self._semaphore:
            response = await self.async_session.post(
                f"{self.project_route_prefix}/responses/batches/",
                json=request_data.model_dump(),
            )
            raise_for_status_with_detail(response)
            task_id = response.json()

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            # For the status
            response = await self.async_session.get(
                f"{self.project_route_prefix}/responses/batches/{task_id}",
            )
            raise_for_status_with_detail(response)
            status = BatchCreatePromptResponseStatus.model_validate(response.json())
            if status.status == "FAILURE":
                raise RuntimeError("Failed to batch add responses.")
            elif status.status == "SUCCESS":
                result = status.result
                if result is None:
                    raise RuntimeError("Failed to batch add responses.")
                else:
                    return result

            # Delay before looping again
            await asyncio.sleep(3)
        else:
            raise TimeoutError("Batch add responses timed out.")

    def batch_generate_responses(
        self,
        prompt_template: PromptTemplate,
        *,
        batch_template_variables: list[dict[str, str]] | None = None,
        template_variables_collection: TemplateVariablesCollection | None = None,
        batch_template_variables_ids: list[int] | None = None,
        llm_config: LLMConfig | None = None,
        batch_metadata: list[LLMConfig | GenerationMetadata | None] | None = None,
    ) -> list[PromptResponse]:
        """Batch generate multiple responses using a prompt template."""
        return run_async(self.abatch_generate_responses)(
            prompt_template,
            batch_template_variables=batch_template_variables,
            template_variables_collection=template_variables_collection,
            batch_template_variables_ids=batch_template_variables_ids,
            llm_config=llm_config,
            batch_metadata=batch_metadata,
        )

    async def aget_responses(
        self,
        prompt_id: int | None = None,
        prompt_template_id: int | None = None,
        template_variables_id: int | None = None,
    ) -> list[PromptResponse]:
        """Async version of get_responses."""
        params = {}
        if prompt_id is not None:
            params["prompt_id"] = prompt_id
        if prompt_template_id is not None:
            params["prompt_template_id"] = prompt_template_id
        if template_variables_id is not None:
            params["template_variables_id"] = template_variables_id

        response = await self.async_session.get(
            f"{self.project_route_prefix}/responses/",
            params=params,
        )
        raise_for_status_with_detail(response)
        return [PromptResponse.model_validate(response_data) for response_data in response.json()["items"]]

    def get_responses(
        self,
        prompt_id: int | None = None,
        prompt_template_id: int | None = None,
        template_variables_id: int | None = None,
    ) -> list[PromptResponse]:
        """Get the responses for a prompt template.

        Args:
            prompt_id (int | None): The ID of the prompt to get responses for.
            prompt_template_id (int | None): The ID of the prompt template to get responses for.
            template_variables_id (int | None): The ID of the template variables to get responses for.

        Returns:
            list[PromptResponse]: The list of prompt responses.

        """
        return run_async(self.aget_responses)(
            prompt_id=prompt_id, prompt_template_id=prompt_template_id, template_variables_id=template_variables_id
        )

    async def agenerate_responses_from_collection(
        self,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        *,
        llm_config: LLMConfig | None = None,
    ) -> list[PromptResponse]:
        """Async version of generate_responses_from_collection."""
        entries = await self.aget_entries(collection)
        return await self.abatch_generate_responses(
            prompt_template,
            batch_template_variables_ids=[template_variables.id for template_variables in entries.variables],
            llm_config=llm_config,
        )

    def generate_responses_from_collection(
        self,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        *,
        llm_config: LLMConfig | None = None,
    ) -> list[PromptResponse]:
        """Generates responses using the template for all entries in the collection.

        Args:
            prompt_template (PromptTemplate): The prompt template to use for generation.
            collection (TemplateVariablesCollection): Collection containing template variables.
            llm_config (LLMConfig | None): Optional LLMConfig to use for generation.

        Returns:
            list[PromptResponse]: List of generated response objects.

        """
        return run_async(self.agenerate_responses_from_collection)(
            prompt_template, collection, llm_config=llm_config
        )

    @retry_request
    async def aadd_criteria(
        self,
        prompt_template: PromptTemplate,
        criteria: list[str],
        *,
        delete_existing: bool = False,
    ) -> list[Criterion]:
        """Async version of add_criteria."""
        request_data = GenerateCriteriaRequest(
            prompt_template_id=prompt_template.id,
            criteria=criteria,
            delete_existing=delete_existing,
        )
        response = await self.async_session.post(
            f"{self.project_route_prefix}/criteria/",
            json=request_data.model_dump(),
        )
        raise_for_status_with_detail(response)
        return [Criterion.model_validate(criterion) for criterion in response.json()]

    def add_criteria(
        self,
        prompt_template: PromptTemplate,
        criteria: list[str],
        *,
        delete_existing: bool = False,
    ) -> list[Criterion]:
        """Adds custom evaluation criteria to the prompt template.

        Args:
            prompt_template (PromptTemplate): The prompt template to add criteria to.
            criteria (list[str]): List of criterion strings to add.
            delete_existing (bool): If True, deletes existing criteria before adding new ones.

        Returns:
            list[Criterion]: The list of added criterion objects.

        """
        return run_async(self.aadd_criteria)(prompt_template, criteria, delete_existing=delete_existing)

    @retry_request
    async def agenerate_criteria(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: TemplateVariables | None = None,
        delete_existing: bool = False,
    ) -> list[Criterion]:
        """Async version of generate_criteria."""
        request_data = GenerateCriteriaRequest(
            prompt_template_id=prompt_template.id,
            template_variables_id=template_variables.id if template_variables else None,
            delete_existing=delete_existing,
        )
        response = await self.async_session.post(
            f"{self.project_route_prefix}/criteria/",
            json=request_data.model_dump(),
        )
        raise_for_status_with_detail(response)
        return [Criterion.model_validate(criterion) for criterion in response.json()]

    def generate_criteria(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: TemplateVariables | None = None,
        delete_existing: bool = False,
    ) -> list[Criterion]:
        """Automatically generates evaluation criteria for the prompt template. The criteria is added to the prompt template.

        Args:
            prompt_template (PromptTemplate): The prompt template to generate criteria for.
            template_variables (TemplateVariables | None): If given the criteria is generated for the template variables.
            delete_existing (bool): If True, deletes any existing criteria before generating new ones.

        Returns:
            list[Criterion]: The list of generated criteria objects.

        Raises:
            httpx.HTTPStatusError: If criteria already exist and delete_existing is False

        """
        return run_async(self.agenerate_criteria)(
            prompt_template, template_variables=template_variables, delete_existing=delete_existing
        )

    async def aget_criteria(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: TemplateVariables | None = None,
    ) -> list[Criterion]:
        """Async version of get_criteria."""
        params = {"prompt_template_id": prompt_template.id}
        if template_variables:
            params["template_variables_id"] = template_variables.id

        response = await self.async_session.get(
            f"{self.project_route_prefix}/criteria/",
            params=params,
        )
        raise_for_status_with_detail(response)
        return [Criterion.model_validate(criterion) for criterion in response.json()["items"]]

    def get_criteria(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: TemplateVariables | None = None,
    ) -> list[Criterion]:
        """Get the criteria for a prompt template.

        Args:
            prompt_template (PromptTemplate): The prompt template to get criteria for.
            template_variables (TemplateVariables | None): If given the criteria is generated for the template variables.

        Returns:
            list[Criterion]: The list of criteria objects.

        """
        return run_async(self.aget_criteria)(prompt_template, template_variables=template_variables)

    async def aget_or_generate_criteria(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: TemplateVariables | None = None,
    ) -> tuple[list[Criterion], bool]:
        criteria = await self.aget_criteria(prompt_template, template_variables=template_variables)
        if criteria:
            return criteria, False

        return await self.agenerate_criteria(
            prompt_template,
            template_variables=template_variables,
        ), True

    def get_or_generate_criteria(
        self,
        prompt_template: PromptTemplate,
        *,
        template_variables: TemplateVariables | None = None,
    ) -> tuple[list[Criterion], bool]:
        return run_async(self.aget_or_generate_criteria)(
            prompt_template,
            template_variables=template_variables,
        )

    async def acreate_collection(
        self, *, name: str | None = None, description: str = ""
    ) -> TemplateVariablesCollection:
        """Async version of create_collection."""
        response = await self.async_session.post(
            f"{self.project_route_prefix}/collections/",
            json=CreateCollectionRequest(name=name, description=description).model_dump(),
        )
        raise_for_status_with_detail(response)
        return TemplateVariablesCollection.model_validate(response.json())

    def create_collection(self, *, name: str | None = None, description: str = "") -> TemplateVariablesCollection:
        """Creates a new collection.

        Args:
            name (str | None): The name for the new collection.
            description (str): Optional description for the collection.

        Returns:
            (TemplateVariablesCollection): The newly created collection object.

        Raises:
            httpx.HTTPStatusError: If collection with same name already exists (400 BAD REQUEST)

        """
        return run_async(self.acreate_collection)(name=name, description=description)

    async def aget_collection(self, *, name: str) -> TemplateVariablesCollection:
        """Async version of get_collection."""
        response = await self.async_session.get(
            f"{self.project_route_prefix}/collections/",
            params={"name": name},
        )
        raise_for_status_with_detail(response)
        collections = [TemplateVariablesCollection.model_validate(c) for c in response.json()["items"]]
        if not collections:
            raise ValueError(f"No collection found with name '{name}'")
        return collections[0]

    def get_collection(self, *, name: str) -> TemplateVariablesCollection:
        """Get a collection by name.

        Args:
            name (str): The name of the collection to get.

        Returns:
            TemplateVariablesCollection: The collection object.

        Raises:
            ValueError: If no collection is found with the given name.

        """
        return run_async(self.aget_collection)(name=name)

    async def aget_or_create_collection(
        self,
        *,
        name: str,
        description: str = "",
    ) -> tuple[TemplateVariablesCollection, bool]:
        try:
            return await self.aget_collection(name=name), False
        except ValueError:
            return await self.acreate_collection(name=name, description=description), True

    def get_or_create_collection(
        self,
        *,
        name: str,
        description: str = "",
    ) -> tuple[TemplateVariablesCollection, bool]:
        """Gets an existing collection by name or creates a new one if it doesn't exist.

        Args:
            name: The name of the collection to get or create.
            description: Optional description for the collection if created.

        Returns:
            tuple[TemplateVariablesCollection, bool]: A tuple containing:
                - Collection: The retrieved or created collection object
                - bool: True if a new collection was created, False if existing was found

        """
        return run_async(self.aget_or_create_collection)(name=name, description=description)

    async def aget_entries(
        self,
        collection: TemplateVariablesCollection,
    ) -> TemplateVariablesCollectionWithEntries:
        """Async version of get_entries."""
        response = await self.async_session.get(
            f"{self.project_route_prefix}/collections/{collection.id}",
        )
        raise_for_status_with_detail(response)
        return TemplateVariablesCollectionWithEntries.model_validate(response.json())

    def get_entries(
        self,
        collection: TemplateVariablesCollection,
    ) -> TemplateVariablesCollectionWithEntries:
        """Get the entries for a collection.

        Args:
            collection (TemplateVariablesCollection): The collection to get entries for.

        Returns:
            TemplateVariablesCollectionWithEntries: The collection with entries.

        Raises:
            httpx.HTTPStatusError: If the collection is not found

        """
        return run_async(self.aget_entries)(collection)

    async def aget_or_add_entry(
        self,
        collection: TemplateVariablesCollection,
        template_variables: dict[str, str],
    ) -> tuple[TemplateVariables, bool]:
        async with self._semaphore:
            response = await self.async_session.post(
                f"{self.project_route_prefix}/collections/{collection.id}/entries",
                json=CreateTemplateVariablesRequest(input_values=template_variables).model_dump(),
            )
            raise_for_status_with_detail(response)
            return TemplateVariables.model_validate(response.json()), response.status_code == 201

    def get_or_add_entry(
        self,
        collection: TemplateVariablesCollection,
        template_variables: dict[str, str],
    ) -> tuple[TemplateVariables, bool]:
        """Gets an existing entry or adds a new entry to a collection.

        Args:
            collection (TemplateVariablesCollection): The collection to get or add the entry to.
            template_variables (dict[str, str]): The template variables to get or add.

        Returns:
            tuple[TemplateVariables, bool]: A tuple containing:
                - TemplateVariables: The retrieved or created template variables object
                - bool: True if a new entry was created, False if existing was found

        """
        return run_async(self.aget_or_add_entry)(collection, template_variables)

    async def agenerate_synthetic_entry(
        self,
        collection: TemplateVariablesCollection,
        prompt_template: PromptTemplate,
    ) -> TemplateVariables:
        """Async version of generate_synthetic_entry."""
        async with self._semaphore:
            response = await self.async_session.post(
                f"{self.project_route_prefix}/collections/{collection.id}/entries",
                json=CreateTemplateVariablesRequest(
                    input_values=None,
                    prompt_template_id=prompt_template.id,
                ).model_dump(),
            )
            raise_for_status_with_detail(response)
            return TemplateVariables.model_validate(response.json())

    def generate_synthetic_entry(
        self,
        collection: TemplateVariablesCollection,
        prompt_template: PromptTemplate,
    ) -> TemplateVariables:
        """Generates a new entry in a collection using a prompt template.

        Args:
            collection (TemplateVariablesCollection): The collection to add the generated entry to.
            prompt_template (PromptTemplate): The prompt template to use for generation.

        Returns:
            TemplateVariables: The newly generated template variables object.

        """
        return run_async(self.agenerate_synthetic_entry)(collection, prompt_template)

    async def acreate_experiment(
        self,
        name: str,
        *,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
    ) -> Experiment:
        """Async version of create_experiment."""
        if llm_config and llm_config.id is None:
            raise ValueError("The LLMConfig must include an `id` field.")

        create_request = CreateExperimentRequest(
            name=name,
            description=description,
            prompt_template_id=prompt_template.id,
            collection_id=collection.id,
            llm_config_id=llm_config.id if llm_config else None,
        )

        response = await self.async_session.post(
            f"{self.project_route_prefix}/experiments/",
            json=create_request.model_dump(),
        )
        raise_for_status_with_detail(response)
        return Experiment.model_validate(response.json())

    def create_experiment(
        self,
        name: str,
        *,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
    ) -> Experiment:
        """Creates a new experiment.

        Args:
            name (str): The name of the experiment.
            prompt_template (PromptTemplate): The prompt template to use for the experiment.
            collection (TemplateVariablesCollection): The collection of template variables to use for the experiment.
            llm_config (LLMConfig | None): Optional LLMConfig to use for the experiment.
            description (str): Optional description for the experiment.

        Returns:
            Experiment: The newly created experiment object.

        Raises:
            httpx.HTTPStatusError: If the experiment with the same name already exists

        """
        return run_async(self.acreate_experiment)(
            name,
            prompt_template=prompt_template,
            collection=collection,
            llm_config=llm_config,
            description=description,
        )

    async def aget_experiment(self, *, name: str) -> Experiment:
        """Async version of get_experiment."""
        response = await self.async_session.get(
            f"{self.project_route_prefix}/experiments/",
            params={"experiment_name": name},
        )
        raise_for_status_with_detail(response)
        experiments = [Experiment.model_validate(e) for e in response.json()["items"]]

        if not experiments:
            raise ValueError(f"No experiment found with name '{name}'")

        return experiments[0]

    def get_experiment(self, *, name: str) -> Experiment:
        """Get the experiment with the given name.

        Args:
            name (str): The name of the experiment to get.

        Returns:
            Experiment: The experiment object.

        Raises:
            ValueError: If no experiment is found with the given name.

        """
        return run_async(self.aget_experiment)(name=name)

    async def aget_or_create_experiment(
        self,
        name: str,
        *,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
    ) -> tuple[Experiment, bool]:
        """Async version of get_or_create_experiment.

        Returns
        -------
            A tuple of (experiment, created) where created is True if a new experiment
            was created, False if an existing one was retrieved.

        """
        try:
            # Try to get existing experiment first
            experiment = await self.aget_experiment(name=name)
            return experiment, False
        except ValueError:
            # If not found, create new experiment
            experiment = await self.acreate_experiment(
                name,
                prompt_template=prompt_template,
                collection=collection,
                llm_config=llm_config,
                description=description,
            )
            return experiment, True

    def get_or_create_experiment(
        self,
        name: str,
        *,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
    ) -> tuple[Experiment, bool]:
        """Gets an existing experiment or creates a new one if it doesn't exist.

        Args:
            name (str): The name of the experiment to get or create.
            prompt_template (PromptTemplate): The prompt template to use for the experiment.
            collection (TemplateVariablesCollection): The collection of template variables to use for the experiment.
            llm_config (LLMConfig | None): Optional LLMConfig to use for the experiment.
            description (str): Optional description for the experiment.

        Returns:
            tuple[Experiment, bool]: A tuple containing:
                - The experiment object
                - Boolean indicating if a new experiment was created (True) or existing one returned (False)

        """
        return run_async(self.aget_or_create_experiment)(
            name,
            prompt_template=prompt_template,
            collection=collection,
            llm_config=llm_config,
            description=description,
        )

    @retry_request
    async def arate(
        self,
        prompt_response: PromptResponse,
        *,
        experiment: Experiment | None = None,
        rating_mode: RatingMode = RatingMode.FAST,
    ) -> list[Rating]:
        """Async version of rate."""
        if experiment:
            if not prompt_response.prompt.template_variables:
                logger.warning("Skipping rating - prompt response has no template variables")
                return []

            if (
                not prompt_response.generation_metadata
                or not prompt_response.generation_metadata.llm_model_config.llm_model_name
            ):
                logger.warning("Skipping rating - prompt response has no LLM config")
                return []

            prompt_template_id = prompt_response.prompt.prompt_template.id
            collection_id = prompt_response.prompt.template_variables.collection.id

            if experiment.prompt_template.id != prompt_template_id:
                logger.warning("Skipping rating - prompt template does not match experiment")
                return []

            if experiment.collection.id != collection_id:
                logger.warning("Skipping rating - collection does not match experiment")
                return []

            # TODO: This is not entirely correct since the same `llm_model_name` could
            # come from different LLMConfigs with different sampling parameters. This is
            # a simplification for now since we do not have a reliable way to associate
            # a response with the specific LLMConfig used to generate it.
            if (
                experiment.llm_config.llm_model_name
                != prompt_response.generation_metadata.llm_model_config.llm_model_name
            ):
                logger.warning("Skipping rating - LLM config does not match experiment")
                return []

        async with self._semaphore:
            response = await self.async_session.post(
                f"{self.project_route_prefix}/ratings/",
                json=CreateRatingRequest(
                    prompt_response_id=prompt_response.id,
                    experiment_id=experiment.id if experiment else None,
                    rating_mode=rating_mode,
                ).model_dump(),
            )
            raise_for_status_with_detail(response)
            ratings = [Rating.model_validate(rating) for rating in response.json()]

        # Add the rated response to the experiment if one was provided
        if experiment and ratings:
            # Add the ratings to the prompt response
            prompt_response.ratings = ratings
            # Add the prompt response to the experiment's rated responses if not already present
            if prompt_response not in experiment.rated_responses:
                experiment.rated_responses.append(prompt_response)

        return ratings

    def rate(
        self,
        prompt_response: PromptResponse,
        *,
        experiment: Experiment | None = None,
        rating_mode: RatingMode = RatingMode.FAST,
    ) -> list[Rating]:
        """Rates a response against its prompt template's criteria.

        Args:
            prompt_response (PromptResponse): The response to rate.
            experiment (Experiment | None): Optional experiment to associate ratings with.
            rating_mode (RatingMode): Mode for rating generation (FAST or DETAILED). If DETAILED a reasoning is added to the rating.

        Returns:
            list[Rating]: List of rating objects, one per criterion.

        """
        return run_async(self.arate)(prompt_response, experiment=experiment, rating_mode=rating_mode)

    @retry_request
    async def abatch_rate(
        self,
        batch_prompt_responses: list[PromptResponse],
        *,
        experiment: Experiment | None = None,
        rating_mode: RatingMode = RatingMode.FAST,
    ) -> list[list[Rating]]:
        """Batch version of rate.

        Args:
            batch_prompt_responses (list[PromptResponse]): List of prompt responses to rate.
            experiment (Experiment | None): Optional experiment to associate ratings with.
            rating_mode (RatingMode): Mode for rating generation (FAST or DETAILED). If DETAILED a reasoning is added to the rating.

        Returns:
            list[list[Rating]]: List of lists of rating objects, one per criterion for each prompt response.

        """
        # Start with all responses and remove invalid ones
        filtered_prompt_responses = batch_prompt_responses.copy()
        if experiment:
            # Create slice copy to safely modify during iteration
            for prompt_response in batch_prompt_responses[:]:
                if not prompt_response.prompt.template_variables:
                    logger.warning("Skipping rating - prompt response has no template variables")
                    filtered_prompt_responses.remove(prompt_response)
                    continue

                if (
                    not prompt_response.generation_metadata
                    or not prompt_response.generation_metadata.llm_model_config.llm_model_name
                ):
                    logger.warning("Skipping rating - prompt response has no LLM config")
                    filtered_prompt_responses.remove(prompt_response)
                    continue

                prompt_template_id = prompt_response.prompt.prompt_template.id
                collection_id = prompt_response.prompt.template_variables.collection.id

                if experiment.prompt_template.id != prompt_template_id:
                    logger.warning("Skipping rating - prompt template does not match experiment")
                    filtered_prompt_responses.remove(prompt_response)
                    continue

                if experiment.collection.id != collection_id:
                    logger.warning("Skipping rating - collection does not match experiment")
                    filtered_prompt_responses.remove(prompt_response)
                    continue

                # TODO: This is not entirely correct since the same `llm_model_name` could
                # come from different LLMConfigs with different sampling parameters. This is
                # a simplification for now since we do not have a reliable way to associate
                # a response with the specific LLMConfig used to generate it.
                if (
                    experiment.llm_config.llm_model_name
                    != prompt_response.generation_metadata.llm_model_config.llm_model_name
                ):
                    logger.warning("Skipping rating - LLM config does not match experiment")
                    filtered_prompt_responses.remove(prompt_response)
                    continue

        async with self._semaphore:
            response = await self.async_session.post(
                f"{self.project_route_prefix}/ratings/batches",
                json=BatchCreateRatingRequest(
                    prompt_response_ids=[prompt_response.id for prompt_response in filtered_prompt_responses],
                    experiment_id=experiment.id if experiment else None,
                    rating_mode=rating_mode,
                ).model_dump(),
            )
            raise_for_status_with_detail(response)
            task_id = response.json()

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            # For the status
            response = await self.async_session.get(
                f"{self.project_route_prefix}/ratings/batches/{task_id}",
            )
            raise_for_status_with_detail(response)
            status = BatchCreateRatingResponseStatus.model_validate(response.json())
            if status.status == "FAILURE":
                raise RuntimeError("Failed to batch add responses.")
            elif status.status == "SUCCESS":
                result = status.result
                if result is None:
                    raise RuntimeError("Failed to batch add responses.")
                else:
                    return result

            # Delay before looping again
            await asyncio.sleep(3)
        else:
            raise TimeoutError("Batch add responses timed out.")

    def batch_rate(
        self,
        batch_prompt_responses: list[PromptResponse],
        *,
        experiment: Experiment | None = None,
        rating_mode: RatingMode = RatingMode.FAST,
    ) -> list[list[Rating]]:
        return run_async(self.abatch_rate)(batch_prompt_responses, experiment=experiment, rating_mode=rating_mode)

    # Resource management methods
    async def _aclose(self) -> None:
        """Safely close the async client."""
        try:
            await self.async_session.aclose()
        except Exception:
            pass

    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Create a new event loop for cleanup if necessary
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(self._aclose())
        except Exception:
            pass
        finally:
            atexit.unregister(self._cleanup)

    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any
    ) -> None:
        await self._aclose()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        self._cleanup()
