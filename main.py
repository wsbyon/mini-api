from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel, Field

# 앱
app = FastAPI() # app 이라는 이름의 FastAPI 객체 생성

# basemodel을 상속받아 데이터 모양 정의
class PostIn(BaseModel):
    # title은 문자형이고 최소 1글자, 최대 100글자
    title: str = Field(min_length=1, max_length=100)
    # content은 문자형이고 최소 1글자
    content: str = Field(min_length=1)

# 저장소
posts = [] # posts라는 이름의 리스트 생성
next_id = 1 # next_id라는 이름의 변수에 1 저장

# 도우미 함수
def find_post(post_id: int): # post_id를 매개변수로 받음
    for post in posts: # posts 리스트에서 하나씩 꺼내 post에 담기를 반복
        if post["id"] == post_id: # post의 id가 post_id와 같으면
            return post # post를 반환
        # for문이 끝날때까지 같은 id를 찾지 못하면 404 에러를 발생시키고 메시지 반환
        raise HTTPException(status_code=404, detail="글이 없습니다")
    
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

# 경로 함수
# 아래 함수를 /posts/{post_id} 경로에 PUT 요청이 오면 실행
@app.put("/posts/{post_id}") 
# post_id는 {post_id}에 들어온 값을 int로, body는 요청 본문에 들어온 JSON 데이터를 PostIn 객체로 변환한 것
def update_post(post_id: int, body: PostIn):
    post = find_post(post_id) # find_post 함수로 해당 post를 찾음
    post["title"] = body.title # post의 title을 요청 본문의 title로 변경
    post["content"] = body.content # post의 content를 요청 본문의 content로 변경
    return post # post를 반환

# 경로 함수
# 아래 함수를 /posts/{post_id} 경로에 DELETE 요청이 오면 실행
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int): # {post_id}에 들어온 값을 int형으로 바꿔서 넣어줌
    post = find_post(post_id) # find_post 함수로 해당 post를 찾음
    posts.remove(post) # 리스트에서 해당 post를 제거