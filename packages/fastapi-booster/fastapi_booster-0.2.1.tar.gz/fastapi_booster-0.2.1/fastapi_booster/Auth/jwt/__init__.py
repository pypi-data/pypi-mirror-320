import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
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
    UserRegisterSchema,
    UserSchema,
    UserUpdateSchema,
    UserPrivilegeSchema,
    _add_privilege_to_group,
    _change_user_group,
    _create_user,
    _deactivate_user,
    _get_all_users,
    _remove_privilege_from_group,
    _update_user,
    _create_group,
    _delete_group,
    UserManager,
)
from fastapi_booster.Module import Module


class JWT(Module):
    """
    JWT authentication module for FastAPI Booster.

    This class provides JWT (JSON Web Token) based authentication functionality
    for FastAPI applications. It includes methods for user login, logout, token
    refresh, and various user management operations.

    Attributes:
        _instance (JWT): Singleton instance of the JWT class
        oauth2_scheme (OAuth2PasswordBearer): OAuth2 password bearer scheme for token handling

    Configuration:
        JWT_SECRET_KEY (str): Secret key for JWT. Defaults to an environment variable or a random token.
        JWT_TOKEN_EXPIRE_MINUTES (int): Token expiration time in minutes. Defaults to 30.
        JWT_ALGORITHM (str): JWT encoding algorithm. Defaults to "HS256".
        ALLOW_SELF_SIGNUP (bool): Whether to allow self-registration. Defaults to False.
        AUTH_SQL_URL (str): The SQL connection URL. Defaults to "sqlite:///.db".
    """

    _instance = None
    oauth2_scheme = OAuth2PasswordBearer("login")

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of JWT class if it doesn't exist, otherwise return the existing instance.

        This method implements the Singleton pattern for the JWT class.

        Returns:
            JWT: The single instance of the JWT class.
        """
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
        Initialize the JWT authentication module.

        This method sets up the JWT module with the provided configuration and
        defines various API endpoints for user authentication and management.

        Note:
            This method is quite long and complex. Consider breaking it down into
            smaller, more manageable methods for better readability and maintainability.
        """
        super().__init__(
            "JWT", "JWT Authenticator", settings.AUTH_SQL_URL
        )
        self._secret_key = settings.JWT_SECRET_KEY
        self._token_expire_minutes = settings.JWT_TOKEN_EXPIRE_MINUTES
        self._algorithm = settings.JWT_ALGORITHM
        self._allow_self_signup = settings.ALLOW_SELF_SIGNUP
        self.router.tags = ["JWT"]

    def _verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password using bcrypt.

        Args:
            plain_password (str): The plain text password to verify
            hashed_password (str): The bcrypt hashed password to compare against

        Returns:
            bool: True if the password matches, False otherwise
        """
        user_manager = UserManager.get_instance()
        return user_manager._pwd_context.verify(plain_password, hashed_password)

    def _authenticate_user(self, username: str, password: str):
        """
        Authenticate a user with the given username and password.

        Args:
            username (str): The username of the user to authenticate.
            password (str): The password of the user to authenticate.

        Returns:
            User: The authenticated user object if successful, None otherwise.
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

    def _create_access_token(self, username):
        """
        Create a new JWT access token for the given username.

        Args:
            username (str): The username to create the token for

        Returns:
            str: The encoded JWT access token

        Token Structure:
            - username: The user's username
            - issued_at: UTC timestamp when the token was created
            - expires_at: UTC timestamp when the token will expire
        """
        # add username to the token
        to_encode = {"username": username}
        # add issued_at to the token
        issued_at = datetime.now(timezone.utc)
        to_encode.update({"issued_at": issued_at.isoformat()})
        # add expires to the token
        expires = issued_at + timedelta(minutes=self._token_expire_minutes)
        to_encode.update({"expires_at": expires.isoformat()})
        # encode the token
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def __call__(
        self,
        scopes: SecurityScopes,
        token: str = Depends(oauth2_scheme),
    ):
        """
        Validate the JWT token and return the authenticated user.

        This method is called when the JWT dependency is used in a FastAPI route.
        It validates the token, checks for expiration, and ensures the user has
        the required privileges.

        Args:
            scopes (SecurityScopes): The required security scopes for the route.
            token (str): The JWT token to validate.

        Returns:
            User: The authenticated user object.

        Raises:
            HTTPException: If the token is invalid, expired, or the user lacks required privileges.
        """
        with self.db_session() as db:
            try:
                payload = jwt.decode(
                    token,
                    self._secret_key,
                    algorithms=[self._algorithm],
                )
            except jwt.PyJWTError:
                raise HTTPException(
                    status_code=400, detail="Token is invalid, failed to decode"
                )
            try:
                expires_at = datetime.fromisoformat(payload.get("expires_at"))
                if expires_at < datetime.now(timezone.utc):
                    raise HTTPException(status_code=400, detail="Token is expired")
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid token expiry format"
                )
            user = (
                db.query(User).filter(User.username == payload.get("username")).first()
            )
            if not user:
                raise HTTPException(status_code=400, detail="User not found")
            if not user.is_active:
                raise HTTPException(status_code=400, detail="User is not active")
            if user.last_logout:
                # Convert last_logout to offset-aware datetime
                last_logout = user.last_logout.replace(tzinfo=timezone.utc)
                token_issued_at = datetime.fromisoformat(payload.get("issued_at"))
                if last_logout > token_issued_at:
                    raise HTTPException(
                        status_code=400,
                        detail="Token is invalid, token is issued before user last logout",
                    )
            try:
                user_scopes = [
                    privilege.privilege for privilege in user.group.privileges
                ]
                for scope in scopes.scopes:
                    if scope not in user_scopes:
                        raise HTTPException(
                            status_code=400,
                            detail=f"User does not have the required privileges: {scope}",
                        )
            except AttributeError:
                raise HTTPException(
                    status_code=500,
                    detail="User privileges are not properly configured",
                )
            return user


jwt_instance = JWT.get_instance()


@jwt_instance.router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticate a user and return an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The login form data containing username and password

    Returns:
        dict: A dictionary containing:
            - access_token (str): The JWT access token
            - token_type (str): The token type (always "bearer")

    Raises:
        HTTPException: 
            - 400: If username or password is incorrect
            - 500: If token creation fails
    """
    user = jwt_instance._authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    try:
        access_token = jwt_instance._create_access_token(user.username)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create access token, {e}"
        )
    return {"access_token": access_token, "token_type": "bearer"}


@jwt_instance.router.post("/logout")
async def logout(token: Annotated[str, Depends(jwt_instance.oauth2_scheme)]):
    """
    Log out a user by invalidating their token.

    Args:
        token (str): The user's access token.

    Returns:
        dict: A message confirming successful logout.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    try:
        payload: dict = jwt.decode(
            token,
            jwt_instance._secret_key,
            algorithms=[jwt_instance._algorithm],
        )
        username = payload.get("username")
        with jwt_instance.db_session() as db:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                raise HTTPException(status_code=400, detail="User not found")
            user.last_logout = datetime.now(timezone.utc)
            db.commit()
        return {"message": "Logged out successfully"}
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Token is invalid")


@jwt_instance.router.post("/refresh")
async def refresh(user: Annotated[User, Depends(jwt_instance)]):
    """
    Refresh the user's access token.

    Args:
        user (User): The authenticated user.

    Returns:
        dict: A new access token and token type.

    Raises:
        HTTPException: If token creation fails.
    """
    try:
        access_token = jwt_instance._create_access_token(user.username)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create access token, {e}"
        )
    return {"access_token": access_token, "token_type": "bearer"}


if jwt_instance._allow_self_signup:

    @jwt_instance.router.post("/register")
    async def self_register(user: UserRegisterSchema):
        """
        Register a new user.

        Args:
            user (UserRegisterSchema): The user registration data.

        Returns:
            dict: A message confirming successful registration.
        """
        _create_user(user.username, user.email, user.password, False)
        return {"message": "User registered successfully"}

else:

    @jwt_instance.router.post("/register")
    async def admin_register(
        user: UserRegisterSchema, _: Annotated[User, Depends(jwt_instance)]
    ):
        """
        Register a new user.

        Args:
            user (UserRegisterSchema): The user registration data.

        Returns:
            dict: A message confirming successful registration.
        """
        _create_user(user.username, user.email, user.password, False)
        return {"message": "User registered successfully"}


@jwt_instance.router.get("/users/me", response_model=UserSchema)
async def get_user(user: Annotated[User, Depends(jwt_instance)]):
    """
    Get the current authenticated user's information.

    Args:
        user (User): The authenticated user.

    Returns:
        UserSchema: The user's information.

    Raises:
        HTTPException: If the user is not found or there's an error retrieving the information.
    """
    try:
        return user
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_instance.router.get("/users", response_model=list[UserSchema])
async def get_all_users(
    user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
):
    """
    Get all users (admin only).

    Args:
        user (User): The authenticated user (must be an admin).
        db (Session): The database session.

    Returns:
        list[UserSchema]: A list of all users.

    Raises:
        HTTPException: If the user is not an admin or there's an error retrieving the users.
    """
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    try:
        users = _get_all_users(db)
        return users
    except UserManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_instance.router.put("/users/update")
async def change_password(
    user_update: UserUpdateSchema,
    user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
):
    """
    Update a user's information.

    Args:
        user_update (UserUpdateSchema): The updated user information.
        user (User): The authenticated user.
        db (Session): The database session.

    Returns:
        dict: A message confirming successful update.

    Raises:
        HTTPException: If the user is not found or there's an error updating the user.
    """
    try:
        user = _update_user(user_update, db)
        return {"message": "User updated successfully"}
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_instance.router.put("/users/deactivate")
async def deactivate_user(
    user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
):
    """
    Deactivate a user (admin only).

    Args:
        user (User): The authenticated user (must be an admin).
        db (Session): The database session.

    Returns:
        dict: A message confirming successful deactivation.

    Raises:
        HTTPException: If the user is not an admin, the user is not found, or there's an error deactivating the user.
    """
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    try:
        user = _deactivate_user(user.username, db)
        return {"message": "User deactivated successfully"}
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserManagerException as e:
        raise HTTPException(status_code=500, detail=str(e))


@jwt_instance.router.put("/users/change-group")
async def change_user_group(
    username: str,
    new_group: str,
    admin_user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
):
    """
    Change a user's group (admin only).

    Args:
        username (str): The username of the user to change.
        new_group (str): The name of the new group.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A message confirming successful group change.

    Raises:
        HTTPException: If the admin user is not an admin, the user or group is not found, or there's an error changing the group.
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


@jwt_instance.router.get("/groups", response_model=list[GroupSchema])
async def get_all_groups(
    admin_user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
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


@jwt_instance.router.post("/groups/create")
async def create_group(
    group: GroupSchema,
    admin_user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
):
    """
    Create a new group (admin only).

    Args:
        group (GroupSchema): The group to create.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A message confirming successful group creation.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    _create_group(group, db)
    return {"message": "Group created successfully"}


@jwt_instance.router.delete("/groups/delete")
async def delete_group(
    group_name: str,
    admin_user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
):
    """
    Delete a group (admin only).

    Args:
        group_name (str): The name of the group to delete.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A message confirming successful group deletion.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    _delete_group(group_name, db)
    return {"message": "Group deleted successfully"}


@jwt_instance.router.get(
    "/groups/privileges", response_model=list[UserPrivilegeSchema]
)
async def get_group_privileges(
    group_name: str,
    admin_user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
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
        HTTPException: If the user is not an admin or the group is not found.
    """
    if not admin_user.is_admin():
        raise HTTPException(status_code=403, detail="User is not an admin user")
    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group.privileges


@jwt_instance.router.post("/groups/add-privilege")
async def add_privilege_to_group(
    group_name: str,
    privilege: str,
    admin_user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
):
    """
    Add a privilege to a group (admin only).

    Args:
        group_name (str): The name of the group.
        privilege (str): The privilege to add.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A message confirming successful privilege addition.

    Raises:
        HTTPException: If the user is not an admin, the group is not found, or there's an error adding the privilege.
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


@jwt_instance.router.delete("/groups/remove-privilege")
async def remove_privilege_from_group(
    group_name: str,
    privilege: str,
    admin_user: Annotated[User, Depends(jwt_instance)],
    db: Session = Depends(jwt_instance.db),
):
    """
    Remove a privilege from a group (admin only).

    Args:
        group_name (str): The name of the group.
        privilege (str): The privilege to remove.
        admin_user (User): The authenticated admin user.
        db (Session): The database session.

    Returns:
        dict: A message confirming successful privilege removal.

    Raises:
        HTTPException: If the user is not an admin, the group is not found, or there's an error removing the privilege.
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
