import hashlib # 비밀번호를 해시로 바꾸는 모듈
import hmac # 해시를 비교하는 모듈
import secrets # 무작위 값을 생성하는 모듈(salt, token 등)

from fastapi import FastAPI, HTTPException, Header, Depends 
from pydantic import BaseModel, Field

# 앱
app = FastAPI() # app 이라는 이름의 FastAPI 객체 생성

# basemodel을 상속받아 데이터 모양 정의
class PostIn(BaseModel):
    # title은 문자형이고 최소 1글자, 최대 100글자
    title: str = Field(min_length=1, max_length=100)
    # content은 문자형이고 최소 1글자
    content: str = Field(min_length=1)

class UserIn(BaseModel):
    # username은 문자형이고 최소 3글자, 최대 20글자
    username: str = Field(min_length=3, max_length=20)
    # password는 문자형이고 최소 4글자
    password: str = Field(min_length=4)

# 저장소
posts = [] # posts라는 이름의 리스트 생성
next_id = 1 # next_id라는 이름의 변수에 1 저장
users = {} # users라는 이름의 딕셔너리 생성
tokens = {} # tokens라는 이름의 딕셔너리 생성

# 도우미 함수
def find_post(post_id: int): # post_id를 매개변수로 받음
    for post in posts: # posts 리스트에서 하나씩 꺼내 post에 담기를 반복
        if post["id"] == post_id: # post의 id가 post_id와 같으면
            return post # post를 반환
        # for문이 끝날때까지 같은 id를 찾지 못하면 404 에러를 발생시키고 메시지 반환
        raise HTTPException(status_code=404, detail="글이 없습니다")

# 비밀번호를 해시(되돌릴 수 없는 글자)로 바꾸는 함수
# 매개변수 password는 문자열, salt는 바이트열
def hash_password(password: str, salt: bytes) -> str:
    # pbkdf2_hmac로 100,000번 해시를 반복하고 hex로 16진수로 변환하여 반환
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()

# 헤더에서 토큰을 추출하는 함수
def token_from(authorization: str | None) -> str:
    # authorization이 None이거나 "Bearer "로 시작하지 않으면 
    # 401 에러를 발생시키고 메시지
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")
    # "Bearer "를 제거한 나머지 문자열을 반환
    return authorization.removeprefix("Bearer ")

# 토큰으로 사용자 아이디를 찾는 함수
def current_user(authorization: str | None = Header(default=None)) -> str:
    # token_from 함수에 헤더 값을 넣어 토큰을 추출하고 
    # tokens 딕셔너리에서 사용자 아이디를 찾아 username에 저장
    username = tokens.get(token_from(authorization))
    # username이 None이면 401 에러를 발생시키고 메시지 반환
    if username is None:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")
    return username

# 경로 함수
@app.get("/") # 아래 함수를 "/" 경로에 GET 요청이 오면 실행
def home(): # 함수 정의
    # 돌려줄 내용을 딕셔너리로 만들어 FastAPI가 받아 JSON으로 변환
    return {"message": "안녕하세요"} 

@app.get("/posts") # 아래 함수를 /posts 경로에 GET 요청이 오면 실행
def list_posts():
    # 돌려줄 내용을 리스트로 만들어 FastAPI가 받아 JSON으로 변환
    return posts

# 경로 함수
# 아래 함수를 /posts/{post_id} 경로에 GET 요청이 오면 실행
@app.get("/posts/{post_id}")
# {post_id}에 들어온 값을 FastAPI가 int형으로 바꿔서 넣어줌
def get_post(post_id: int): 
    return find_post(post_id) 

# 경로 함수
# 아래 함수를 /posts 경로에 POST 요청이 오면 실행, 상태코드 201 반환
@app.post("/posts", status_code=201)
def create_post(body: PostIn): # body라는 이름의 PostIn 객체를 매개변수로 받음
    global next_id # next_id를 전역변수로 사용)
    # post라는 이름의 딕셔너리를 만들어 id, title, content를 저장
    post = {"id": next_id, "title": body.title, "content": body.content}
    posts.append(post) # post를 posts 리스트에 추가
    next_id += 1 # next_id를 1 증가
    return post # post를 반환

# 아래 함수를 /posts/{post_id} 경로에 PUT 요청이 오면 실행
@app.put("/posts/{post_id}") 
# post_id는 {post_id}에 들어온 값을 int로, body는 요청 본문에 들어온 JSON 데이터를 PostIn 객체로 변환한 것
def update_post(post_id: int, body: PostIn):
    post = find_post(post_id) # find_post 함수로 해당 post를 찾음
    post["title"] = body.title # post의 title을 요청 본문의 title로 변경
    post["content"] = body.content # post의 content를 요청 본문의 content로 변경
    return post # post를 반환

# 아래 함수를 /posts/{post_id} 경로에 DELETE 요청이 오면 실행, 상태코드 204 반환
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int): # {post_id}에 들어온 값을 int형으로 바꿔서 넣어줌
    post = find_post(post_id) # find_post 함수로 해당 post를 찾음
    posts.remove(post) # 리스트에서 해당 post를 제거

# 아래 함수를 /signup 경로에 POST 요청이 오면 실행, 상태코드 201 반환
@app.post("/signup", status_code=201)
def signup(body: UserIn):
    if body.username in users:
        raise HTTPException(status_code=409, detail="이미 있는 아이디입니다")
    salt = secrets.token_bytes(16)
    users[body.username] = {"salt": salt, "password": hash_password(body.password, salt)}
    return { "username": body.username }

@app.post("/login")
def login(body: UserIn):
    user = users.get(body.username)
    if user is None or not hmac.compare_digest(user["hash"], hash_password(body.password, user["salt"])):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다")
    token = secrets.token_hex(16)
    tokens[token] = body.username
    return { "token": token, "username": body.username }

@app.get("/me")
def me(username: str = Depends(current_user)):
    return { "username": username }

@app.post("/logout", status_code=204)
def logout(authrization: str | None = Header(default=None)):
    tokens.pop(token_from(authrization), None)