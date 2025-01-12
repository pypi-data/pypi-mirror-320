from datetime import datetime, timezone
import os
from typing import Optional, List

from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, create_engine
from sqlalchemy.orm import (
    MappedColumn,
    mapped_column,
    relationship,
    sessionmaker,
    Session,
)

from fastapi_booster import logger, settings
from fastapi_booster.Module import Module
from fastapi_booster.LifeSpanManager import startup_function


class UserManagerException(Exception):
    """Base exception for user management errors."""

    pass


class UserAlreadyExistsException(UserManagerException):
    """Raised when trying to create a user that already exists."""

    pass


class UserNotFoundException(UserManagerException):
    """Raised when a user is not found."""

    pass


class UserUpdateException(UserManagerException):
    """Raised when there is an error updating a user."""

    pass


class UserDeletionException(UserManagerException):
    """Raised when there is an error deleting a user."""

    pass


class GroupManagerException(UserManagerException):
    """Base exception for group management errors."""

    pass


class GroupAlreadyExistsException(GroupManagerException):
    """Raised when trying to create a group that already exists."""

    pass


class GroupNotFoundException(GroupManagerException):
    """Raised when a group is not found."""

    pass


class GroupUpdateException(GroupManagerException):
    """Raised when there is an error updating a group."""

    pass


class GroupDeletionException(GroupManagerException):
    """Raised when there is an error deleting a group."""

    pass


class UserManager(Module):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """
        Initialize the UserManager module.

        This module is responsible for managing user and group models, including
        password hashing and creating default groups at startup.
        """
        super().__init__(
            name="User Manager",
            description="User Manager module for FastAPI Booster, which defines the user model and the user privilege model",
            sql_url=settings.AUTH_SQL_URL,
        )
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        @startup_function
        def create_default_groups():
            """
            Create default groups if they do not exist.

            This function is executed at startup to ensure that the default groups
            (admin, user, view) are present in the database.
            """
            try:
                with user_manager.db_session() as db:
                    # Check if the groups already exist
                    admin_group = db.query(Group).filter(Group.name == "admin").first()
                    user_group = db.query(Group).filter(Group.name == "user").first()
                    view_group = db.query(Group).filter(Group.name == "view").first()

                    # Create admin group if it doesn't exist
                    if not admin_group:
                        admin_group = Group(name="admin")
                        db.add(admin_group)
                        db.commit()
                        db.refresh(admin_group)
                        logger.info(f"Created admin group")

                    # Create user group if it doesn't exist
                    if not user_group:
                        user_group = Group(name="user")
                        db.add(user_group)
                        db.commit()
                        db.refresh(user_group)
                        logger.info(f"Created user group")
                    # Create view group if it doesn't exist
                    if not view_group:
                        view_group = Group(name="view")
                        db.add(view_group)
                        db.commit()
                        db.refresh(view_group)
                        logger.info(f"Created view group")
            except Exception as e:
                raise GroupManagerException(
                    "An error occurred while creating default groups."
                ) from e

    @property
    def sql_url(self) -> str:
        """
        Get the SQL URL.

        Returns:
            str: The SQL connection URL.
        """
        return self._sql_url

    @sql_url.setter
    def sql_url(self, sql_url: str):
        """
        Set the SQL URL and initialize the SQL engine and session.

        Args:
            sql_url (str): The SQL connection URL.
        """
        self._sql_url = sql_url
        self._sql_engine = create_engine(sql_url)
        self._sql_session = sessionmaker(
            autocommit=False, autoflush=True, bind=self._sql_engine
        )


user_manager = UserManager.get_instance()


class User(user_manager.model):
    """
    Represents a user in the system.

    Attributes:
        __tablename__ (str): The name of the table in the database.
        id (MappedColumn[int]): The primary key of the user.
        username (MappedColumn[str]): The unique username of the user.
        email (MappedColumn[str]): The unique email of the user.
        hashed_password (MappedColumn[str]): The hashed password of the user.
        is_active (MappedColumn[bool]): Indicates if the user is active.
        last_login (MappedColumn[datetime]): The last login time of the user.
        last_logout (MappedColumn[datetime]): The last logout time of the user.
        group_id (MappedColumn[int]): The foreign key to the user's group.
        group (MappedColumn["Group"]): The relationship to the user's group.
    """

    __tablename__: str = "users"
    id: MappedColumn[int] = mapped_column(primary_key=True)
    username: MappedColumn[str] = mapped_column(unique=True, nullable=False)
    email: MappedColumn[str] = mapped_column(unique=True, nullable=True)
    hashed_password: MappedColumn[str] = mapped_column(nullable=False)
    is_active: MappedColumn[bool] = mapped_column(default=True)
    last_login: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_logout: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    group_id: MappedColumn[int] = mapped_column(ForeignKey("groups.id"))
    group: MappedColumn["Group"] = relationship("Group", back_populates="users", lazy="joined")  # type: ignore

    def is_admin(self) -> bool:
        """
        Check if the user is an admin.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return self.group.name == "admin"


class Group(user_manager.model):
    """
    Represents a group in the system.

    Attributes:
        __tablename__ (str): The name of the table in the database.
        id (MappedColumn[int]): The primary key of the group.
        name (MappedColumn[str]): The unique name of the group.
        privileges (MappedColumn[List["Privilege"]]): The privileges associated with the group.
        users (MappedColumn[List["User"]]): The users associated with the group.
    """

    __tablename__ = "groups"
    id: MappedColumn[int] = mapped_column(primary_key=True)
    name: MappedColumn[str] = mapped_column(unique=True, nullable=False)
    privileges: MappedColumn[List["Privilege"]] = relationship(
        "Privilege", back_populates="group", cascade="all, delete-orphan", lazy="joined"
    )  # type: ignore
    users: MappedColumn[List["User"]] = relationship("User", back_populates="group", lazy="joined")  # type: ignore


class Privilege(user_manager.model):
    """
    Represents a privilege in the system.

    Attributes:
        __tablename__ (str): The name of the table in the database.
        id (MappedColumn[int]): The primary key of the privilege.
        group_id (MappedColumn[int]): The foreign key to the group.
        privilege (MappedColumn[str]): The privilege description.
        group (MappedColumn["Group"]): The relationship to the group.
    """

    __tablename__ = "privileges"
    id: MappedColumn[int] = mapped_column(primary_key=True)
    group_id: MappedColumn[int] = mapped_column(ForeignKey("groups.id"))
    privilege: MappedColumn[str] = mapped_column(nullable=False)
    group: MappedColumn["Group"] = relationship("Group", back_populates="privileges", lazy="joined")  # type: ignore


class GroupSchema(BaseModel):
    """
    Schema for a group.

    Attributes:
        name (str): The name of the group.
        privileges (Optional[List[str]]): The list of privileges associated with the group.
    """

    name: str
    privileges: Optional[List[str]] = None


class UserSchema(BaseModel):
    """
    Schema for a user.

    Attributes:
        username (str): The username of the user.
        email (Optional[str]): The email of the user.
        is_active (bool): Indicates if the user is active.
        group (Optional[GroupSchema]): The group associated with the user.
        last_login (Optional[datetime]): The last login time of the user.
        last_logout (Optional[datetime]): The last logout time of the user.
    """

    username: str
    email: Optional[str] = None
    is_active: bool
    group: Optional[GroupSchema] = None
    last_login: Optional[datetime] = None
    last_logout: Optional[datetime] = None


class UserRegisterSchema(BaseModel):
    """
    Schema for user registration.

    Attributes:
        username (str): The username of the new user.
        email (Optional[str]): The email of the new user.
        password (str): The password of the new user.
        group (str): The group of the new user.
    """

    username: str
    email: Optional[str] = None
    password: str
    group: Optional[str] = None


class UserUpdateSchema(BaseModel):
    """
    Schema for updating user information.

    Attributes:
        username (str): The username of the user.
        email (Optional[str]): The email of the user.
        password (Optional[str]): The new password of the user.
    """

    username: str
    email: Optional[str] = None
    password: Optional[str] = None


class UserPrivilegeSchema(BaseModel):
    """
    Schema for user privileges.

    Attributes:
        privilege (str): The privilege description.
    """

    privilege: str


def _update_user(user: UserUpdateSchema, db: Session):
    """Update an existing user's information.

    Args:
        user (UserUpdateSchema): The updated user information.
        db (Session): The database session.

    Returns:
        User: The updated user object.

    Raises:
        UserNotFoundException: If the user is not found.
        UserUpdateException: If there's an error updating the user.
    """
    try:
        existing_user = db.query(User).filter(User.username == user.username).first()
        if not existing_user:
            raise UserNotFoundException(f"User '{user.username}' not found.")
        if user.email:
            existing_user.email = user.email
        if user.password:
            existing_user.hashed_password = user_manager._pwd_context.hash(
                user.password
            )
            existing_user.last_logout = datetime.now(timezone.utc)

        db.commit()
        db.refresh(existing_user)
        return existing_user
    except UserNotFoundException as e:
        raise e
    except Exception as e:
        raise UserUpdateException(
            f"An error occurred while updating the user, {e}"
        ) from e


def _delete_user(username: str, db: Session):
    """Delete a user by username.

    Args:
        username (str): The username of the user to delete.
        db (Session): The database session.

    Returns:
        bool: True if the user was successfully deleted.

    Raises:
        UserNotFoundException: If the user is not found.
        UserDeletionException: If there's an error deleting the user.
    """
    try:
        user_to_delete = db.query(User).filter(User.username == username).first()
        if not user_to_delete:
            raise UserNotFoundException(f"User '{username}' not found.")
        db.query(User).filter(User.username == username).delete()
        db.commit()
        return True
    except UserNotFoundException as e:
        raise e
    except Exception as e:
        raise UserDeletionException("An error occurred while deleting the user.") from e


def _get_all_users(db: Session) -> List[User]:
    """Retrieve all users from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[User]: A list of all users.

    Raises:
        UserManagerException: If there's an error retrieving the users.
    """
    try:
        users = db.query(User).all()
        return users
    except Exception as e:
        raise UserManagerException(
            f"An error occurred while retrieving users, {e}"
        ) from e


def _deactivate_user(username: str, db: Session):
    """Deactivate a user by username.

    Args:
        username (str): The username of the user to deactivate.
        db (Session): The database session.

    Returns:
        User: The deactivated user object.

    Raises:
        UserNotFoundException: If the user is not found.
        UserUpdateException: If there's an error deactivating the user.
    """
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise UserNotFoundException(f"User '{username}' not found.")
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    except UserNotFoundException as e:
        raise e
    except Exception as e:
        raise UserUpdateException(
            "An error occurred while deactivating the user."
        ) from e


def _create_group(group: GroupSchema, db: Session):
    """Create a new group.

    Args:
        group (GroupSchema): The group information.
        db (Session): The database session.

    Returns:
        Group: The created group object.

    Raises:
        GroupAlreadyExistsException: If the group already exists.
        GroupManagerException: If there's an error creating the group.
    """
    try:
        if db.query(Group).filter(Group.name == group.name).first():
            raise GroupAlreadyExistsException(f"Group '{group.name}' already exists.")
        new_group = Group(name=group.name)
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return new_group
    except GroupAlreadyExistsException as e:
        raise e
    except Exception as e:
        raise GroupManagerException(
            "An error occurred while creating the group."
        ) from e


def _delete_group(name: str, db: Session):
    """Delete a group by name.

    Args:
        name (str): The name of the group to delete.
        db (Session): The database session.

    Returns:
        bool: True if the group was successfully deleted.

    Raises:
        GroupNotFoundException: If the group is not found.
        GroupDeletionException: If there's an error deleting the group.
    """
    try:
        group_to_delete = db.query(Group).filter(Group.name == name).first()
        if not group_to_delete:
            raise GroupNotFoundException(f"Group '{name}' not found.")
        db.query(Group).filter(Group.name == name).delete()
        db.commit()
        return True
    except GroupNotFoundException as e:
        raise e
    except Exception as e:
        raise GroupDeletionException(
            "An error occurred while deleting the group."
        ) from e


def _get_group_by_name(name: str, db: Session) -> Optional[Group]:
    """Retrieve a group by name.

    Args:
        name (str): The name of the group to retrieve.
        db (Session): The database session.

    Returns:
        Optional[Group]: The retrieved group object, or None if not found.

    Raises:
        GroupNotFoundException: If the group is not found.
        GroupManagerException: If there's an error retrieving the group.
    """
    try:
        group = db.query(Group).filter(Group.name == name).first()
        if not group:
            raise GroupNotFoundException(f"Group '{name}' not found.")
        return group
    except GroupNotFoundException as e:
        raise e
    except Exception as e:
        raise GroupManagerException(
            "An error occurred while retrieving the group."
        ) from e


def _get_all_groups(db: Session) -> List[Group]:
    """Retrieve all groups from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[Group]: A list of all groups.

    Raises:
        GroupManagerException: If there's an error retrieving the groups.
    """
    try:
        groups = db.query(Group).all()
        return groups
    except Exception as e:
        raise GroupManagerException("An error occurred while retrieving groups.") from e


def _add_privilege_to_group(group_name: str, privilege: str, db: Session):
    """Add a privilege to a group.

    Args:
        group_name (str): The name of the group.
        privilege (str): The privilege to add.
        db (Session): The database session.

    Returns:
        Privilege: The added privilege object.

    Raises:
        GroupNotFoundException: If the group is not found.
        GroupManagerException: If there's an error adding the privilege.
    """
    try:
        group = db.query(Group).filter(Group.name == group_name).first()
        if not group:
            raise GroupNotFoundException(f"Group '{group_name}' not found.")
        new_privilege = Privilege(group_id=group.id, privilege=privilege)
        db.add(new_privilege)
        db.commit()
        db.refresh(new_privilege)
        return new_privilege
    except GroupNotFoundException as e:
        raise e
    except Exception as e:
        raise GroupManagerException(
            "An error occurred while adding the privilege to the group."
        ) from e


def _remove_privilege_from_group(group_name: str, privilege: str, db: Session):
    """Remove a privilege from a group.

    Args:
        group_name (str): The name of the group.
        privilege (str): The privilege to remove.
        db (Session): The database session.

    Returns:
        bool: True if the privilege was successfully removed.

    Raises:
        GroupNotFoundException: If the group or privilege is not found.
        GroupManagerException: If there's an error removing the privilege.
    """
    try:
        group = db.query(Group).filter(Group.name == group_name).first()
        if not group:
            raise GroupNotFoundException(f"Group '{group_name}' not found.")
        privilege_to_remove = (
            db.query(Privilege)
            .filter(Privilege.group_id == group.id, Privilege.privilege == privilege)
            .first()
        )
        if not privilege_to_remove:
            raise GroupNotFoundException(
                f"Privilege '{privilege}' not found in group '{group_name}'."
            )
        db.delete(privilege_to_remove)
        db.commit()
        return True
    except GroupNotFoundException as e:
        raise e
    except Exception as e:
        raise GroupManagerException(
            "An error occurred while removing the privilege from the group."
        ) from e


def _change_user_group(username: str, new_group: str, db: Session):
    """Change a user's group.

    Args:
        username (str): The username of the user.
        new_group (str): The name of the new group.
        db (Session): The database session.

    Returns:
        User: The updated user object.

    Raises:
        UserNotFoundException: If the user is not found.
        GroupNotFoundException: If the new group is not found.
        UserManagerException: If there's an error changing the user's group.
    """
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise UserNotFoundException(f"User '{username}' not found.")
        group = db.query(Group).filter(Group.name == new_group).first()
        if not group:
            raise GroupNotFoundException(f"Group '{new_group}' not found.")
        user.group = group
        db.commit()
        db.refresh(user)
        return user
    except UserNotFoundException as e:
        raise e
    except GroupNotFoundException as e:
        raise e
    except Exception as e:
        raise UserManagerException(
            "An error occurred while changing the user's group."
        ) from e


def _create_user(username: str, email: Optional[str], password: str, is_admin: bool):
    """Create a new user.

    Args:
        username (str): The username of the new user.
        email (Optional[str]): The email of the new user.
        password (str): The password of the new user.
        is_admin (bool): Whether the new user is an admin.

    Returns:
        User: The created user object.

    Raises:
        GroupNotFoundException: If the specified group is not found.
        UserAlreadyExistsException: If the user already exists.
        UserManagerException: If there's an error creating the user.
    """
    group_name = "admin" if is_admin else "user"
    user = UserRegisterSchema(
        username=username, email=email, password=password, group=group_name
    )

    try:
        with user_manager.db_session() as db:
            group = db.query(Group).filter(Group.name == group_name).first()
            if not group:
                raise GroupNotFoundException(f"Group '{group_name}' not found.")

            if db.query(User).filter(User.username == user.username).first():
                raise UserAlreadyExistsException(
                    f"User '{user.username}' already exists."
                )

            new_user = User(
                username=user.username,
                email=user.email,
                hashed_password=user_manager._pwd_context.hash(user.password),
                is_active=True,
                group=group,
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
    except UserAlreadyExistsException as e:
        raise e
    except Exception as e:
        raise UserManagerException(
            f"An error occurred while creating the {group_name} user."
        ) from e


def create_user(username: str, email: Optional[str], password: str, is_admin: bool):
    """Create a new user at startup.

    Args:
        username (str): The username of the new user.
        email (Optional[str]): The email of the new user.
        password (str): The password of the new user.
        is_admin (bool): Whether the new user is an admin.
    """

    @startup_function
    def user_creation():
        try:
            _create_user(username, email, password, is_admin)
        except UserAlreadyExistsException as e:
            return
        except Exception as e:
            logger.error(f"An error occurred while creating the user {username}.")
