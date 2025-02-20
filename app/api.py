from enum import Enum
from lib2to3.pytree import Base

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from . import model
from .model import JoinRoomResult, LiveDifficulty, RoomInfo, RoomUser, SafeUser, WaitRoomStatus

app = FastAPI()

# Sample APIs


@app.get("/")
async def root():
    return {"message": "Hello World"}


# User APIs


class UserCreateRequest(BaseModel):
    user_name: str
    leader_card_id: int


class UserCreateResponse(BaseModel):
    user_token: str



@app.post("/user/create", response_model=UserCreateResponse)
def user_create(req: UserCreateRequest):
    """新規ユーザー作成"""
    token = model.create_user(req.user_name, req.leader_card_id)
    return UserCreateResponse(user_token=token)

bearer = HTTPBearer()


def get_auth_token(cred: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    assert cred is not None
    if not cred.credentials:
        raise HTTPException(status_code=401, detail="invalid credential")
    return cred.credentials


@app.get("/user/me", response_model=SafeUser)
def user_me(token: str = Depends(get_auth_token)):
    user = model.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=404)
    # print(f"user_me({token=}, {user=})")
    return user


class Empty(BaseModel):
    pass


@app.post("/user/update", response_model=Empty)
def update(req: UserCreateRequest, token: str = Depends(get_auth_token)):
    """Update user attributes"""
    # print(req)
    model.update_user(token, req.user_name, req.leader_card_id)
    return {}


#Room APIs

class RoomCreateRequest(BaseModel):
    live_id: int
    select_difficulty: LiveDifficulty

class RoomCreateResponse(BaseModel):
    room_id: int

@app.post("/room/create", response_model = RoomCreateResponse)
def room_create(req: RoomCreateRequest,token: str = Depends(get_auth_token)):
    """ルーム作成"""
    room_id = model.create_room(token,req.live_id, req.select_difficulty)
    return RoomCreateResponse(room_id=room_id)

class RoomListRequest(BaseModel):
    live_id: int

class RoomListResponse(BaseModel):
    room_info: list[RoomInfo]

@app.post("/room/list", response_model = RoomListResponse)
def room_list(req: RoomListRequest):
    room_info:list[RoomInfo] = model.list_room(req.live_id)
    return RoomListResponse(room_info = room_info)

class RoomJoinRequest(BaseModel):
    room_id:int
    select_difficulty:LiveDifficulty

class RoomJoinResponse(BaseModel):
    join_room_result:JoinRoomResult

@app.post("/room/join", response_model = RoomJoinResponse)
def room_join(req:RoomJoinRequest,token: str = Depends(get_auth_token)):
    room_join:JoinRoomResult = model.join_room(token,req.room_id,req.select_difficulty)
    return RoomJoinResponse(join_room_join = room_join)

class RoomWaitRequest(BaseModel):
    room_id:int

class RoomWaitResponse(BaseModel):
    status:WaitRoomStatus
    room_user_list:list[RoomUser]

@app.post("/room/wait", response_model = RoomWaitResponse)
def room_wait(req:RoomWaitRequest,token : str = Depends(get_auth_token)):
    status:WaitRoomStatus = model.status_room(req.room_id)
    room_user_list:list[RoomUser] = model.user_list_room(token,req.room_id)
    return RoomWaitResponse(status = status,room_user_list = room_user_list)

class RoomStartRequest(BaseModel):
    room_id:int

class RoomStartResponse(BaseModel):
    pass

@app.post("/room/start",response_model= RoomStartResponse)
def room_start(req:RoomStartRequest,token:str = Depends(get_auth_token)):
    model.start_room(token,req.room_id)
    return RoomStartResponse()