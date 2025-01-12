from datetime import datetime, timezone
import os
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic as HTTPBasicSecurity
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from fastapi_booster import settings
from fastapi_booster.UserManager import (
    Group,
    GroupManagerException,
    GroupNotFoundException,
    GroupSchema,
    User,
    UserManagerException,
    UserNotFoundException,
    UserPrivilegeSchema,
    UserRegisterSchema,
    UserSchema,
    UserUpdateSchema,
    _add_privilege_to_group,
    _change_user_group,
    _create_group,
    _create_user,
    _deactivate_user,
    _delete_group,
    _get_all_users,
    _remove_privilege_from_group,
    _update_user,
    UserManager,
)
from fastapi_booster.Module import Module

security = HTTPBasicSecurity()


class HTTPBasic(Module):
    """
    HTTP Basic authentication module for FastAPI Booster.

    This class provides HTTP Basic authentication functionality for FastAPI applications.
    It includes methods for user login, logout, and various user management operations.

    Configuration:
        - ALLOW_SELF_SIGNUP: Whether to allow self-registration of users. Defaults to False.
        - AUTH_SQL_URL: The SQL connection URL. Defaults to "sqlite:///.db".
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(
        self,
    ):
        """
        Initialize the HTTPBasicAuth module.

        Args:
            allow_self_signup (bool): Flag to allow self-registration of users. Defaults to False.
            sql_url (str): The SQL connection URL. Defaults to "sqlite:///.db".
        """
        super().__init__(
            "HTTPBasic",
            "HTTP Basic Authenticator",
            settings.AUTH_SQL_URL,
        )
        self._allow_self_signup = settings.ALLOW_SELF_SIGNUP
        self.router.tags = ["HTTPBasic"]

    def _verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password (str): The plain password.
            hashed_password (str): The hashed password.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        user_manager = UserManager.get_instance()
        return user_manager._pwd_context.verify(plain_password, hashed_password)

    def _authenticate_user(self, username: str, password: str):
        """
        Authenticate a user by username and password.

        Args:
            username (str): The username.
            password (str): The password.

        Returns:
            User: The authenticated user object, or None if authentication fails.
        """
        with self.db_session() as db:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return None
            if not self._verify_password(password, user.hashed_password):
                return None
            user.last_login = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)
            return user

    def __call__(self, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
        """
        Authenticate a user using HTTP Basic credentials.

        Args:
            credentials (HTTPBasicCredentials): The login credentials containing username and password.

        Returns:
            User: The authenticated user object.

        Raises:
            HTTPException: If authentication fails or the user is not active.
        """
        with self.db_session() as db:
            user = db.query(User).filter(User.username == credentials.username).first()
            if not user:
                raise HTTPException(
                    status_code=400, detail="Incorrect username or password"
                )
            if not user.is_active:
                raise HTTPException(status_code=400, detail="User is not active")
            if not self._verify_password(credentials.password, user.hashed_password):
                raise HTTPException(
                    status_code=400, detail="Incorrect username or password"
                )
            return user


httpBasic = HTTPBasic.get_instance()


@httpBasic.router.post("/login")
async def login(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    """
    Authenticate a user and return a success message.

    Args:
        credentials (HTTPBasicCredentials): The login credentials containing username and password.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If authentication fails.
    """
    user = httpBasic._authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"message": "Login successful"}


@httpBasic.router.post("/logout")
async def logout(user: Annotated[User, Depends(httpBasic)]):
    """
    Log out a user by updating their last logout time.

    Args:
        user (User): The authenticated user.

    Returns:
        dict: A dictionary containing a success message.
    """
    user.last_logout = datetime.now(timezone.utc)
    with httpBasic.db_session() as db:
        db.commit()
    return {"message": "Logged out successfully"}


if httpBasic._allow_self_signup:

    @httpBasic.router.post("/register")
    async def self_register(user: UserRegisterSchema):
        """
        Register a new user.

        Args:
            user (UserRegisterSchema): The user registration data.

        Returns:
            dict: A dictionary containing a success message.
        """
        _create_user(user.username, user.email, user.password, False)
        return {"message": "User registered successfully"}

else:

    @httpBasic.router.post("/register")
    async def admin_register(
        user: UserRegisterSchema, _: Annotated[User, Depends(httpBasic)]
    ):
        """
        Register a new user.

        Args:
            user (UserRegisterSchema): The user registration data.

        Returns:
            dict: A dictionary containing a success message.
        """
        _create_user(user.username, user.email, user.password, False)
        return {"message": "User registered successfully"}


@httpBasic.router.get("/users/me", response_model=UserSchema)
async def get_user(user: Annotated[User, Depends(httpBasic)]):
    """
    Get the current authenticated user's information.

    Args:
        user (User): The authenticated user.

    Returns:
        UserSchema: The user's information.
    """
    return user


@httpBasic.router.get("/users", response_model=list[UserSchema])
async def get_all_users(
    user: Annotated[User, Depends(httpBasic)], db: Session = Depends(httpBasic.db)
):
    """
    Get all users (admin only).

    Args:
        user (User): The authenticated user (must be an admin).
        db (Session): The database session.

    Returns:
        list[UserSchema]: A list of all users.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    return _get_all_users(db)


@httpBasic.router.put("/users/update")
async def change_password(
    user_update: UserUpdateSchema,
    user: Annotated[User, Depends(httpBasic)],
    db: Session = Depends(httpBasic.db),
):
    """
    Update a user's information.

    Args:
        user_update (UserUpdateSchema): The updated user information.
        user (User): The authenticated user.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing a success message.
    """
    try:
        user = _update_user(user_update, db)
        return {"message": "User updated successfully"}
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@httpBasic.router.put("/users/deactivate")
async def deactivate_user(
    user: Annotated[User, Depends(httpBasic)], db: Session = Depends(httpBasic.db)
):
    """
    Deactivate a user (admin only).

    Args:
        user (User): The authenticated user (must be an admin).
        db (Session): The database session.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    user = _deactivate_user(user.username, db)
    return {"message": "User deactivated successfully"}


@httpBasic.router.put("/users/change-group")
async def change_user_group(
    username: str,
    new_group: str,
    admin_user: Annotated[User, Depends(httpBasic)],
    db: Session = Depends(httpBasic.db),
):
    """
    Change a user's group (admin only).

    Args:
        username (str): The username of the user to change.
        new_group (str): The name of the new group.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the admin user is not an admin.
        HTTPException: If the user or group is not found.
        HTTPException: If there's an error changing the group.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    try:
        user = _change_user_group(username, new_group, db)
        return {
            "message": f"User '{username}' group changed to '{new_group}' successfully"
        }
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GroupNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@httpBasic.router.get("/groups", response_model=list[GroupSchema])
async def get_all_groups(
    admin_user: Annotated[User, Depends(httpBasic)], db: Session = Depends(httpBasic.db)
):
    """
    Get all groups (admin only).

    Args:
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        list[GroupSchema]: A list of all groups.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    groups = db.query(Group).all()
    return groups


@httpBasic.router.post("/groups/create")
async def create_group(
    group: GroupSchema,
    admin_user: Annotated[User, Depends(httpBasic)],
    db: Session = Depends(httpBasic.db),
):
    """
    Create a new group (admin only).

    Args:
        group (GroupSchema): The group to create.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    _create_group(group, db)
    return {"message": "Group created successfully"}


@httpBasic.router.delete("/groups/delete")
async def delete_group(
    group_name: str,
    admin_user: Annotated[User, Depends(httpBasic)],
    db: Session = Depends(httpBasic.db),
):
    """
    Delete a group (admin only).

    Args:
        group_name (str): The name of the group to delete.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    _delete_group(group_name, db)
    return {"message": "Group deleted successfully"}


@httpBasic.router.get("/groups/privileges", response_model=list[UserPrivilegeSchema])
async def get_group_privileges(
    group_name: str,
    admin_user: Annotated[User, Depends(httpBasic)],
    db: Session = Depends(httpBasic.db),
):
    """
    Get privileges for a specific group (admin only).

    Args:
        group_name (str): The name of the group.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        list[UserPrivilegeSchema]: A list of privileges for the specified group.

    Raises:
        HTTPException: If the user is not an admin.
        HTTPException: If the group is not found.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group.privileges


@httpBasic.router.post("/groups/add-privilege")
async def add_privilege_to_group(
    group_name: str,
    privilege: str,
    admin_user: Annotated[User, Depends(httpBasic)],
    db: Session = Depends(httpBasic.db),
):
    """
    Add a privilege to a group (admin only).

    Args:
        group_name (str): The name of the group.
        privilege (str): The privilege to add.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the user is not an admin.
        HTTPException: If the group is not found.
        HTTPException: If there's an error adding the privilege.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    try:
        privilege = _add_privilege_to_group(group_name, privilege, db)
        return {
            "message": f"Privilege '{privilege}' added to group '{group_name}' successfully"
        }
    except GroupNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GroupManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@httpBasic.router.delete("/groups/remove-privilege")
async def remove_privilege_from_group(
    group_name: str,
    privilege: str,
    admin_user: Annotated[User, Depends(httpBasic)],
    db: Session = Depends(httpBasic.db),
):
    """
    Remove a privilege from a group (admin only).

    Args:
        group_name (str): The name of the group.
        privilege (str): The privilege to remove.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the user is not an admin.
        HTTPException: If the group is not found.
        HTTPException: If there's an error removing the privilege.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    try:
        _remove_privilege_from_group(group_name, privilege, db)
        return {
            "message": f"Privilege '{privilege}' removed from group '{group_name}' successfully"
        }
    except GroupNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GroupManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))
