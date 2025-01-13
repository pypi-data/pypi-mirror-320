from abc import ABC, abstractmethod
from collections.abc import Generator, Sequence
from typing import Any, Generic, TypeVar

from inzicht.declarative import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class CRUDInterface(ABC, Generic[T]):
    """
    Abstract base class that defines the CRUD interface for generic operations on a resource of type T.
    """

    @classmethod
    @abstractmethod
    def get_model(cls) -> type[T]:
        """
        Retrieves the model class associated with the GenericCRUD class.

        Returns:
            type[T]: The model class associated with the GenericCRUD class.
        """

    @abstractmethod
    def count(self, where: Any | None = None) -> int:
        """
        Count the total number of records.

        Args:
            where (Any, optional): Filter conditions for retrieving records.

        Returns:
            int: The total number of records in the collection.
        """

    @abstractmethod
    def create(self, *, payload: dict[str, Any]) -> T:
        """
        Create a new record with the provided payload.

        Args:
            payload (dict[str, Any]): The data to create the new record.

        Returns:
            T: The created record.
        """

    @abstractmethod
    def create_many(self, *, payload: Sequence[dict[str, Any]]) -> Sequence[T]:
        """
        Create multiple records with the provided payload.

        Args:
            payload (Sequence[dict[str, Any]]): A sequence of data dictionaries to create the new records.

        Returns:
            Sequence[T]: A sequence of created records.
        """

    @abstractmethod
    def read(self, id: int | str) -> T:
        """
        Retrieve a single record by its ID.

        Args:
            id (int | str): The ID of the record to retrieve.

        Returns:
            T: The record with the specified ID.
        """

    @abstractmethod
    def read_many(
        self,
        *,
        where: Any | None = None,
        order_by: Any | None = None,
        skip: int = 0,
        take: int = 10,
    ) -> Generator[T, None, None]:
        """
        Retrieve multiple records based on conditions.

        Args:
            where (Any, optional): Filter conditions for retrieving records.
            order_by (Any, optional): Criteria to order the results.
            skip (int, optional): Number of records to skip. Defaults to 0.
            take (int, optional): Number of records to retrieve. Defaults to 10.

        Returns:
            Generator[T, None, None]: A generator of the retrieved records.
        """

    @abstractmethod
    def update(self, id: int | str, *, payload: dict[str, Any]) -> T:
        """
        Update a record by its ID with the provided payload.

        Args:
            id (int | str): The ID of the record to update.
            payload (dict[str, Any]): The data to update the record with.

        Returns:
            T: The updated record.
        """

    @abstractmethod
    def delete(self, id: int | str) -> T:
        """
        Delete a record by its ID.

        Args:
            id (int | str): The ID of the record to delete.

        Returns:
            T: The deleted record.
        """
